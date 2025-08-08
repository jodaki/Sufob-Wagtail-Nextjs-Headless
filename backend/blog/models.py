from email.mime import image

from django.contrib.auth import get_user_model as user_model
from django.db import models, transaction
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from mptt.models import MPTTModel, TreeForeignKey
from pypinyin import lazy_pinyin
from requests import head
from streams import blocks as stream_blocks
from taggit.models import ItemBase, TagBase
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
    TitleFieldPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField

# Create your models here.
from wagtail.models import Orderable, Page, Revision, Task, TaskState
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtailmarkdown.fields import MarkdownField

from .serializers import (
    BlogCategoriesField,
    BlogTagsField,
    MDContentField,
    MDContentHeadings,
    StreamFieldHeadings,
)
from wagtail_headless_preview.models import HeadlessPreviewMixin

User = user_model()


# Create your models here.
# TODO: 动态模板


@register_snippet
class BlogCategory(MPTTModel, ClusterableModel, models.Model):
    name = models.CharField(max_length=80, verbose_name="目录")
    slug = models.SlugField(max_length=80, verbose_name="目录别名", unique=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="图片",
    )
    svg = models.TextField(blank=True, null=True, verbose_name="SVG")
    parent = TreeForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name="父目录",
    )

    class Meta:
        verbose_name = "目录"
        verbose_name_plural = "目录"
        ordering = ["order", "name"]

    def __str__(self):
        names = []
        category = self
        while category is not None:
            names.append(category.name)
            category = category.parent
        return " / ".join(reversed(names))

    class MPTTMeta:
        order_insertion_by = ["name"]

    api_fields = [
        APIField("id"),
        APIField("name"),
        APIField("slug"),
        APIField("parent"),
        APIField("order"),
        APIField("description"),
        APIField("image"),
        APIField("svg"),
    ]


@register_snippet
class BlogTag(TagBase):
    class Meta:
        verbose_name = "Blog tag"

    def save(self, *args, **kwargs):
        # 如果slug为空或需要更新slug时
        if not self.slug or self.slug_is_derived_from_name():
            # 使用pypinyin将中文转换为拼音
            pinyin_string = "".join(lazy_pinyin(self.name))
            # 使用Django的slugify处理拼音字符串
            self.slug = slugify(pinyin_string)
        super(BlogTag, self).save(*args, **kwargs)

    def slug_is_derived_from_name(self):
        # 检查当前slug是否由name转换而来
        return slugify("".join(lazy_pinyin(self.name))) == self.slug

    api_fields = [
        APIField("id"),
        APIField("name"),
        APIField("slug"),
    ]


@register_snippet
class TaggedBlog(ItemBase):
    tag = models.ForeignKey(
        BlogTag, related_name="tagged_blogs", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="blog.BlogPage", on_delete=models.CASCADE, related_name="tagged_items"
    )
    api_fields = [
        APIField("tag"),
        APIField("content_object"),
    ]


from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index
from data_management.models import AllData
import requests
import json
from decimal import Decimal


class ScrollTimePage(Page):
    """صفحه حرفه‌ای برای دریافت و ذخیره داده‌های بورس از API IME"""
    
    template = "blog/scroll_time_page.html"
    
    description = RichTextField("توضیحات", blank=True)
    
    # تنظیمات API
    api_url = models.URLField(
        "آدرس API", 
        default="https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList",
        help_text="آدرس API برای دریافت داده‌های بورس"
    )
    
    # تنظیمات تاریخ
    from_date = models.CharField(
        max_length=10, 
        default="1404/04/01", 
        verbose_name="تاریخ شروع (شمسی)",
        help_text="مثال: 1404/04/01"
    )
    to_date = models.CharField(
        max_length=10, 
        default="1404/04/29", 
        verbose_name="تاریخ پایان (شمسی)",
        help_text="مثال: 1404/04/29"
    )
    
    # تنظیمات دسته‌بندی (کنسانتره سنگ آهن)
    main_cat = models.IntegerField(default=1, verbose_name="دسته اصلی")
    cat = models.IntegerField(default=49, verbose_name="دسته فرعی")
    sub_cat = models.IntegerField(default=477, verbose_name="زیردسته")
    producer = models.IntegerField(default=0, verbose_name="تولیدکننده")
    
    # تنظیمات نمایش
    last_fetch_time = models.DateTimeField(null=True, blank=True, verbose_name="آخرین دریافت")
    last_fetch_count = models.IntegerField(default=0, verbose_name="تعداد رکورد آخرین دریافت")
    auto_fetch = models.BooleanField(default=False, verbose_name="دریافت خودکار")
    
    # تنظیمات ذخیره خودکار
    auto_save_to_database = models.BooleanField(
        default=False, 
        verbose_name="ذخیره خودکار در پایگاه داده",
        help_text="اگر فعال باشد، هنگام ذخیره صفحه، داده‌ها از API دریافت و در پایگاه داده ذخیره خواهد شد"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('api_url'),
        MultiFieldPanel([
            FieldPanel('from_date'),
            FieldPanel('to_date'),
        ], heading="محدوده تاریخ"),
        MultiFieldPanel([
            FieldPanel('main_cat'),
            FieldPanel('cat'),
            FieldPanel('sub_cat'),
            FieldPanel('producer'),
        ], heading="تنظیمات دسته‌بندی"),
        MultiFieldPanel([
            FieldPanel('auto_fetch'),
            FieldPanel('auto_save_to_database'),
        ], heading="وضعیت و تنظیمات"),
    ]
    
    search_fields = Page.search_fields + [
        index.SearchField('description'),
    ]
    
    def save_data_from_api(self):
        """دریافت حرفه‌ای و ذخیره داده‌ها از API IME (مبتنی بر کدهای شما)"""
        if not self.api_url:
            return False, "آدرس API تنظیم نشده است"
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Payload مطابق کدهای شما
        payload = {
            "Language": 8,
            "fari": False,
            "GregorianFromDate": self.from_date,
            "GregorianToDate": self.to_date,
            "MainCat": self.main_cat,
            "Cat": self.cat,
            "SubCat": self.sub_cat,
            "Producer": self.producer
        }
        
        # Headers مطابق کدهای شما
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "text/plain, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept-Language": "fa-IR,fa;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6"
        }
        
        try:
            # درخواست POST مطابق کدهای شما
            logger.info(f"درخواست به API با پارامترهای: {payload}")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"خطای HTTP: {response.status_code}, پاسخ: {response.text[:500]}")
                return False, f"خطای HTTP {response.status_code}: سرور پاسخ نامعتبر داد"
            
            # پردازش پاسخ JSON
            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"خطا در پردازش JSON: {e}, محتوا: {response.text[:500]}")
                return False, f"خطا در پردازش پاسخ: محتوای دریافتی JSON معتبر نیست"
            
            if not response_data.get("d"):
                logger.error(f"خطا در ساختار JSON: کلید 'd' یافت نشد. پاسخ: {response_data}")
                return False, "خطا در ساختار پاسخ: داده‌های مورد انتظار یافت نشد"
            
            try:
                data = json.loads(response_data.get("d", "[]"))
            except ValueError as e:
                logger.error(f"خطا در پردازش محتوای d: {e}, محتوا: {response_data.get('d')[:500]}")
                return False, "خطا در پردازش داده‌های دریافتی"
            
            if not isinstance(data, list):
                logger.error(f"داده دریافتی لیست نیست: {type(data)}")
                return False, f"فرمت پاسخ API نامعتبر است: {type(data)}"
            
            total_records = len(data)
            saved_count = 0
            errors_count = 0
            
            if total_records == 0:
                logger.warning("هیچ داده‌ای از API دریافت نشد")
                return False, "هیچ داده‌ای برای ذخیره‌سازی یافت نشد"
            
            for item in data:
                try:
                    # بررسی فیلدهای ضروری
                    if not all([item.get('GoodsName'), item.get('Symbol'), item.get('date')]):
                        logger.warning(f"داده ناقص: {item}")
                        errors_count += 1
                        continue
                    
                    # ذخیره در AllData
                    all_data, created = AllData.objects.update_or_create(
                        symbol=item.get('Symbol', ''),
                        transaction_date=item.get('date', ''),
                        defaults={
                            'commodity_name': item.get('GoodsName', ''),
                            'final_price': float(item.get('Price')) if item.get('Price') else None,
                            'source': f'scroll-time-{self.id}',
                            # استفاده از Quantity به عنوان جایگزین Volume
                            'contract_volume': float(item.get('Quantity')) if item.get('Quantity') else float(item.get('Volume')) if item.get('Volume') else None,
                            # استفاده از TotalPrice به عنوان جایگزین Value
                            'transaction_value': float(item.get('TotalPrice')) if item.get('TotalPrice') else float(item.get('Value')) if item.get('Value') else None,
                            'producer': item.get('ProducerName', '') or item.get('Producer', ''),
                            'hall': item.get('Talar', '') or item.get('Hall', ''),
                            'raw_data': item,
                            # اطلاعات اضافی
                            'supplier': item.get('ArzehKonandeh', ''),
                            'broker': item.get('cBrokerSpcName', ''),
                            'warehouse': item.get('Warehouse', ''),
                            'delivery_date': item.get('DeliveryDate'),
                            'settlement_date': item.get('SettlementDate'),
                            'contract_type': item.get('ContractType', ''),
                            'settlement_type': item.get('Tasvieh', ''),
                            'unit': item.get('Unit', ''),
                        }
                    )
                    if created:
                        saved_count += 1
                except Exception as item_error:
                    logger.error(f"خطا در ذخیره آیتم {item.get('Symbol')}: {str(item_error)}")
                    errors_count += 1
                    continue
            
            if errors_count > 0:
                return True, f"تعداد {saved_count} رکورد جدید از {total_records} ذخیره شد. {errors_count} خطا رخ داد."
            else:
                return True, f"تعداد {saved_count} رکورد جدید از {total_records} با موفقیت ذخیره شد."
            
        except requests.RequestException as e:
            logger.error(f"خطا در ارتباط با API: {str(e)}")
            return False, f"خطا در ارتباط با API: {str(e)}"
        except Exception as e:
            import traceback
            logger.error(f"خطای پیش‌بینی نشده: {str(e)}, جزییات: {traceback.format_exc()}")
            return False, f"خطای پیش‌بینی نشده: {str(e)}"
    
    @staticmethod
    def safe_decimal(value):
        """تبدیل امن به Decimal"""
        if value is None or value == '':
            return None
        try:
            return Decimal(str(value))
        except:
            return None
            
    @staticmethod
    def shamsi_to_gregorian(shamsi_date):
        """تبدیل ساده تاریخ شمسی به میلادی (بدون jdatetime)"""
        # برای سادگی فقط string برگردانیم
        return shamsi_date
    
    def get_context(self, request, *args, **kwargs):
        """اضافه کردن داده‌های ذخیره شده به context"""
        context = super().get_context(request, *args, **kwargs)
        
        # Get the saved data for this page
        saved_data = AllData.objects.filter(source=f'scroll-time-{self.id}').order_by('-created_at')[:50]
        context['saved_data'] = saved_data
        
        return context
    
    def save(self, *args, **kwargs):
        """Override save method to auto-save data from API if checkbox is checked"""
        # First save the page normally
        super().save(*args, **kwargs)
        
        # If auto save is enabled, fetch and save API data
        if self.auto_save_to_database:
            try:
                success, message = self.save_data_from_api()
                if success:
                    # Update last fetch information
                    from django.utils import timezone
                    self.last_fetch_time = timezone.now()
                    # Save again but without triggering auto-save to avoid infinite loop
                    temp_auto_save = self.auto_save_to_database
                    self.auto_save_to_database = False
                    super().save(update_fields=['last_fetch_time', 'auto_save_to_database'])
                    self.auto_save_to_database = temp_auto_save
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"خطا در ذخیره خودکار داده‌ها: {str(e)}")


class BlogPage(Page):
    template = "blog/detail.html"
    subpage_types = []
    parent_page_types = ["blog.BlogPageIndex"]
    tags = ClusterTaggableManager(through="blog.TaggedBlog", blank=False, help_text="")
    categories = ParentalManyToManyField("blog.BlogCategory", blank=False)
    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    content = StreamField(
        [
            ("richtext", stream_blocks.RichText()),
        ],
        use_json_field=True,
        blank=True,
    )
    md_content = MarkdownField(blank=True, null=True, verbose_name="Markdown内容")
    view_count = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    search_fields = Page.search_fields + [
        index.SearchField("content"),
        index.SearchField("title"),
        index.SearchField("md_content"),
        index.SearchField("search_description"),
        index.SearchField("seo_title"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        return context

    def serializer_heading_tags(self, content):
        headings = []
        if not content:
            return headings
        for block in content:
            if block.block_type == "richtext":
                print(block.value.get("value").get("headings"))
        return headings

    content_panels = Page.content_panels + [
        FieldPanel("tags", heading="关键词"),
        FieldPanel("categories", heading="目录"),
        FieldPanel("header_image", heading="头图"),
        FieldPanel("content", heading="内容"),
        FieldPanel("md_content", heading="Markdown内容"),
    ]

    def get_absolute_url(self):
        return self.url

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Blog page"
        verbose_name_plural = "Blog page"

    api_fields = [
        APIField("tags", serializer=BlogTagsField()),
        APIField("categories", serializer=BlogCategoriesField()),
        APIField("header_image"),
        APIField("content"),
        APIField("md_content", serializer=MDContentField()),
        APIField("seo_title"),
        APIField("search_description"),
        # APIField(
        #     "published_date_display",
        #     serializer=DateField(format="%A %d %B %Y", source="first_published_at"),
        # ),
        # APIField("tagged_blogs"),
        APIField("headings", serializer=StreamFieldHeadings(source="content")),
        APIField("owner"),
        APIField("view_count"),
        APIField("md_headings", serializer=MDContentHeadings(source="md_content")),
        APIField("last_published_at"),
    ]


class BlogPageView(models.Model):
    blog_page = models.ForeignKey(
        BlogPage, on_delete=models.CASCADE, related_name="views"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP地址"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="用户"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Blog page view"
        verbose_name_plural = "Blog page views"

    def __str__(self):
        return self.blog_page.title


class BlogPageIndex(Page):
    intro = RichTextField(blank=True, verbose_name="简介")
    template = "blog/index.html"
    max_count = 1
    subpage_types = ["blog.BlogPage"]

    api_fields = [
        APIField("intro"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["blog_pages"] = BlogPage.objects.live().order_by("-first_published_at")
        return context

    class Meta:
        verbose_name = "Blog index"
        verbose_name_plural = "Blog indexes"


class CategoryIndexPage(Page):
    template = "blog/category_index.html"
    max_count = 1
    subpage_types = ["blog.BlogPage"]

    def get_context(self, request):
        context = super().get_context(request)
        context["categories"] = BlogCategory.objects.all()
        return context

    class Meta:
        verbose_name = "Category index"
        verbose_name_plural = "Category indexes"
