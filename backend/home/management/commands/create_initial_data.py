from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wagtail.models import Site, Page
from wagtail.images.models import Image as WagtailImage
from home.models import HomePage
from blog.models import BlogPageIndex, BlogPage, BlogCategory, BlogTag
from sufob_comments.models import Comment
from django.utils import timezone
from wagtail.rich_text import RichText
from wagtail.fields import StreamField
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial data for the project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-pages',
            action='store_true',
            help='Skip creating pages',
        )
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip creating users',
        )
        parser.add_argument(
            '--skip-blog',
            action='store_true',
            help='Skip creating blog content',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting initial data creation...'))
        
        if not options['skip_users']:
            self.create_users()
        
        if not options['skip_pages']:
            self.create_pages()
            
        if not options['skip_blog']:
            self.create_blog_content()
            
        self.stdout.write(self.style.SUCCESS('✅ Initial data created successfully!'))

    def create_users(self):
        """Create admin and test users"""
        self.stdout.write('Creating users...')
        
        # Create superuser if doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(f'Created superuser: {admin.username}')
        else:
            self.stdout.write('Admin user already exists')
        
        # Create test users
        test_users = [
            {'username': 'editor', 'email': 'editor@example.com', 'first_name': 'ویرایشگر', 'last_name': 'سایت'},
            {'username': 'author', 'email': 'author@example.com', 'first_name': 'نویسنده', 'last_name': 'محتوا'},
            {'username': 'viewer', 'email': 'viewer@example.com', 'first_name': 'کاربر', 'last_name': 'عادی'},
        ]
        
        for user_data in test_users:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    password='password123',
                    **user_data
                )
                self.stdout.write(f'Created user: {user.username}')
            else:
                self.stdout.write(f'User {user_data["username"]} already exists')

    def create_pages(self):
        """Create initial pages structure"""
        self.stdout.write('Creating pages...')
        
        # Get root page
        root_page = Page.objects.get(slug='root')
        
        # Create HomePage if doesn't exist
        if not HomePage.objects.exists():
            home_page = HomePage(
                title='خانه',
                slug='home',
                seo_title='صفحه اصلی سایت',
                search_description='صفحه اصلی سایت - خوش آمدید به سایت ما'
            )
            root_page.add_child(instance=home_page)
            home_page.save_revision().publish()
            
            # Set as default site homepage
            site = Site.objects.get(is_default_site=True)
            site.root_page = home_page
            site.save()
            
            self.stdout.write('Created HomePage')
        else:
            home_page = HomePage.objects.first()
            self.stdout.write('HomePage already exists')
        
        # Create BlogPageIndex if doesn't exist
        if not BlogPageIndex.objects.exists():
            blog_index = BlogPageIndex(
                title='بلاگ',
                slug='blog',
                intro='<p>به بخش بلاگ خوش آمدید. در اینجا آخرین مقالات و پست‌ها را می‌توانید مشاهده کنید.</p>',
                seo_title='بلاگ - آخرین مقالات',
                search_description='مقالات و پست‌های بلاگ در موضوعات مختلف'
            )
            home_page.add_child(instance=blog_index)
            blog_index.save_revision().publish()
            
            self.stdout.write('Created BlogPageIndex')
        else:
            self.stdout.write('BlogPageIndex already exists')

    def create_blog_content(self):
        """Create blog categories, tags, and sample posts"""
        self.stdout.write('Creating blog content...')
        
        # Create blog categories
        categories_data = [
            {'name': 'فناوری', 'slug': 'technology', 'description': 'مقالات مرتبط با فناوری و تکنولوژی'},
            {'name': 'برنامه‌نویسی', 'slug': 'programming', 'description': 'آموزش‌های برنامه‌نویسی و توسعه نرم‌افزار'},
            {'name': 'وب', 'slug': 'web', 'description': 'توسعه وب و فناوری‌های مرتبط'},
            {'name': 'دیتابیس', 'slug': 'database', 'description': 'مباحث مرتبط با پایگاه داده'},
            {'name': 'امنیت', 'slug': 'security', 'description': 'امنیت سایبری و حفاظت از اطلاعات'},
        ]
        
        created_categories = []
        for cat_data in categories_data:
            category, created = BlogCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            created_categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category {category.name} already exists')
        
        # Create blog tags
        tags_data = ['Django', 'Python', 'Wagtail', 'JavaScript', 'React', 'Vue', 'CSS', 'HTML', 'API', 'REST']
        
        created_tags = []
        for tag_name in tags_data:
            tag, created = BlogTag.objects.get_or_create(name=tag_name)
            created_tags.append(tag)
            if created:
                self.stdout.write(f'Created tag: {tag.name}')
            else:
                self.stdout.write(f'Tag {tag.name} already exists')
        
        # Create sample blog posts
        blog_index = BlogPageIndex.objects.first()
        if blog_index:
            blog_posts_data = [
                {
                    'title': 'مقدمه‌ای بر Django',
                    'slug': 'introduction-to-django',
                    'md_content': '''# مقدمه‌ای بر Django

Django یکی از محبوب‌ترین فریمورک‌های وب Python است که توسط توسعه‌دهندگان حرفه‌ای در سراسر جهان استفاده می‌شود.

## ویژگی‌های کلیدی Django

- **ORM قدرتمند**: Django یک ORM (Object-Relational Mapping) قدرتمند دارد
- **Admin Panel**: پنل مدیریت خودکار
- **Security**: امنیت بالا و محافظت در برابر حملات رایج

## شروع کار

برای شروع کار با Django:

```python
pip install django
django-admin startproject myproject
```

این فقط یک مقدمه ساده است!''',
                    'categories': [0, 1],  # فناوری، برنامه‌نویسی
                    'tags': ['Django', 'Python'],
                    'search_description': 'مقدمه‌ای جامع بر فریمورک Django برای توسعه وب'
                },
                {
                    'title': 'آموزش Wagtail CMS',
                    'slug': 'wagtail-cms-tutorial',
                    'md_content': '''# آموزش Wagtail CMS

Wagtail یک سیستم مدیریت محتوای قدرتمند است که بر روی Django ساخته شده است.

## چرا Wagtail؟

- **انعطاف‌پذیری**: امکان ساخت صفحات پیچیده
- **StreamField**: سیستم بلوک‌های انعطاف‌پذیر
- **API**: پشتیبانی کامل از REST API

## نصب و راه‌اندازی

```bash
pip install wagtail
wagtail start mysite
```

شروع به ساخت وب‌سایت حرفه‌ای کنید!''',
                    'categories': [0, 2],  # فناوری، وب
                    'tags': ['Wagtail', 'Django', 'API'],
                    'search_description': 'آموزش کامل کار با Wagtail CMS'
                },
                {
                    'title': 'بهترین روش‌های امنیت وب',
                    'slug': 'web-security-best-practices',
                    'md_content': '''# بهترین روش‌های امنیت وب

امنیت یکی از مهم‌ترین جنبه‌های توسعه وب است که نباید نادیده گرفته شود.

## نکات کلیدی امنیت

### 1. اعتبارسنجی ورودی‌ها
همیشه تمام ورودی‌های کاربر را بررسی کنید.

### 2. HTTPS
استفاده از HTTPS الزامی است.

### 3. احراز هویت قوی
از روش‌های احراز هویت دو مرحله‌ای استفاده کنید.

## ابزارهای مفید

- OWASP ZAP
- Burp Suite
- Security Headers

امنیت را جدی بگیرید!''',
                    'categories': [0, 4],  # فناوری، امنیت
                    'tags': ['امنیت', 'وب'],
                    'search_description': 'راهنمای جامع برای امنیت در توسعه وب'
                },
                {
                    'title': 'طراحی پایگاه داده موثر',
                    'slug': 'effective-database-design',
                    'md_content': '''# طراحی پایگاه داده موثر

طراحی صحیح پایگاه داده اساس هر اپلیکیشن موفق است.

## اصول کلیدی

### نرمال‌سازی
- First Normal Form (1NF)
- Second Normal Form (2NF)  
- Third Normal Form (3NF)

### ایندکس‌گذاری
ایندکس‌های مناسب عملکرد را بهبود می‌بخشند.

### روابط
انواع روابط:
- One-to-One
- One-to-Many
- Many-to-Many

## نکات عملی

```sql
CREATE INDEX idx_user_email ON users(email);
```

طراحی خوب = عملکرد بهتر!''',
                    'categories': [0, 3],  # فناوری، دیتابیس
                    'tags': ['دیتابیس', 'SQL'],
                    'search_description': 'اصول و روش‌های طراحی پایگاه داده'
                },
                {
                    'title': 'توسعه API با Django REST Framework',
                    'slug': 'django-rest-framework-api',
                    'md_content': '''# توسعه API با Django REST Framework

Django REST Framework ابزاری قدرتمند برای ساخت API های RESTful است.

## نصب و پیکربندی

```python
pip install djangorestframework
```

## ساخت اولین API

```python
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
```

## ویژگی‌های کلیدی

- Serialization
- Authentication
- Permissions
- Pagination

API های حرفه‌ای بسازید!''',
                    'categories': [1, 2],  # برنامه‌نویسی، وب
                    'tags': ['Django', 'API', 'REST'],
                    'search_description': 'آموزش کامل Django REST Framework'
                }
            ]
            
            # Get some users for assigning as owners
            users = User.objects.all()
            owner = users.first() if users.exists() else None
            
            # Get or create default blog images
            default_images = []
            image_files = ['default-blog-image.max-165x165.jpg', 'true-detective.original.jpg', 'true-detective_5jXV2LF.original.jpg']
            
            for image_file in image_files:
                try:
                    img = WagtailImage.objects.filter(title__icontains=image_file.split('.')[0]).first()
                    if img:
                        default_images.append(img)
                except:
                    pass
            
            # If no images found, try to get any available image
            if not default_images:
                default_images = list(WagtailImage.objects.all()[:3])
            
            # If still no images, create a simple one
            if not default_images:
                # For now, we'll skip image requirement - this needs to be handled properly
                self.stdout.write(self.style.WARNING('No images found for blog posts. You may need to upload images first.'))
                return
            
            for i, post_data in enumerate(blog_posts_data):
                if not BlogPage.objects.filter(slug=post_data['slug']).exists():
                    # Select image cyclically from available images
                    selected_image = default_images[i % len(default_images)] if default_images else None
                    
                    blog_page = BlogPage(
                        title=post_data['title'],
                        slug=post_data['slug'],
                        md_content=post_data['md_content'],
                        seo_title=post_data['title'],
                        search_description=post_data['search_description'],
                        header_image=selected_image,
                        owner=owner
                    )
                    blog_index.add_child(instance=blog_page)
                    
                    # Add categories
                    for cat_index in post_data['categories']:
                        if cat_index < len(created_categories):
                            blog_page.categories.add(created_categories[cat_index])
                    
                    # Add tags
                    for tag_name in post_data['tags']:
                        tag = BlogTag.objects.filter(name=tag_name).first()
                        if tag:
                            blog_page.tags.add(tag)
                    
                    blog_page.save_revision().publish()
                    self.stdout.write(f'Created blog post: {blog_page.title}')
                else:
                    self.stdout.write(f'Blog post {post_data["title"]} already exists')
            
            # Create some comments for the blog posts
            self.create_sample_comments()
    
    def create_sample_comments(self):
        """Create sample comments for blog posts"""
        blog_posts = BlogPage.objects.all()
        
        if not blog_posts.exists():
            return
        
        comments_data = [
            {'author': 'علی احمدی', 'content': 'مقاله بسیار مفیدی بود. ممنون از اشتراک‌گذاری', 'website': 'https://example.com'},
            {'author': 'سارا محمدی', 'content': 'عالی بود! منتظر مقالات بیشتر هستم.', 'website': ''},
            {'author': 'حسین رضایی', 'content': 'آیا می‌توانید در مورد موضوع بیشتر توضیح دهید؟', 'website': 'https://blog.example.com'},
            {'author': 'فاطمه کریمی', 'content': 'خیلی کاربردی بود. دستتان درد نکند!', 'website': ''},
            {'author': 'محمد صالحی', 'content': 'مطالب خوبی ارائه داده‌اید. ادامه دهید.', 'website': 'https://site.example.com'},
        ]
        
        for blog_post in blog_posts[:3]:  # Add comments to first 3 posts
            # Add 2-3 random comments to each post
            post_comments = random.sample(comments_data, random.randint(2, 3))
            
            for comment_data in post_comments:
                if not Comment.objects.filter(
                    post=blog_post, 
                    author=comment_data['author']
                ).exists():
                    Comment.objects.create(
                        post=blog_post,
                        **comment_data
                    )
                    self.stdout.write(f'Created comment by {comment_data["author"]} for {blog_post.title}')
