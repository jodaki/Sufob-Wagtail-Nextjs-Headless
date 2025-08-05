# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prices', '0002_add_price_data_models'),
    ]

    operations = [
        # MainCategory Model
        migrations.CreateModel(
            name='MainCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(unique=True, verbose_name='مقدار (API Value)')),
                ('name', models.CharField(max_length=100, verbose_name='نام گروه اصلی')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('order', models.IntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
            ],
            options={
                'verbose_name': 'گروه اصلی',
                'verbose_name_plural': 'گروه‌های اصلی',
                'ordering': ['order', 'name'],
            },
        ),
        
        # Category Model
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(verbose_name='مقدار (API Value)')),
                ('name', models.CharField(max_length=100, verbose_name='نام گروه')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('order', models.IntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('main_category', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='categories',
                    to='prices.maincategory',
                    verbose_name='گروه اصلی'
                )),
            ],
            options={
                'verbose_name': 'گروه',
                'verbose_name_plural': 'گروه‌ها',
                'ordering': ['main_category', 'order', 'name'],
            },
        ),
        
        # SubCategory Model
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(verbose_name='مقدار (API Value)')),
                ('name', models.CharField(max_length=100, verbose_name='نام زیرگروه')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('order', models.IntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subcategories',
                    to='prices.category',
                    verbose_name='گروه'
                )),
            ],
            options={
                'verbose_name': 'زیرگروه',
                'verbose_name_plural': 'زیرگروه‌ها',
                'ordering': ['category', 'order', 'name'],
            },
        ),
        
        # ScrollTimeRequest Model
        migrations.CreateModel(
            name='ScrollTimeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date_shamsi', models.CharField(max_length=10, verbose_name='تاریخ شروع (شمسی)')),
                ('end_date_shamsi', models.CharField(max_length=10, verbose_name='تاریخ پایان (شمسی)')),
                ('duplicate_handling', models.CharField(
                    max_length=20,
                    choices=[
                        ('skip', 'رد کردن رکوردهای تکراری'),
                        ('replace', 'جایگزینی رکوردهای تکراری'),
                        ('update', 'بروزرسانی رکوردهای موجود'),
                    ],
                    default='skip',
                    verbose_name='نحوه مواجهه با داده‌های تکراری'
                )),
                ('auto_save', models.BooleanField(default=False, verbose_name='ذخیره خودکار در پایگاه داده')),
                ('status', models.CharField(
                    max_length=20,
                    choices=[
                        ('pending', 'در انتظار'),
                        ('processing', 'در حال پردازش'),
                        ('preview', 'پیش‌نمایش'),
                        ('completed', 'تکمیل شده'),
                        ('failed', 'ناموفق'),
                    ],
                    default='pending',
                    verbose_name='وضعیت درخواست'
                )),
                ('response_data', models.JSONField(null=True, blank=True, verbose_name='داده‌های پاسخ')),
                ('total_records', models.IntegerField(default=0, verbose_name='تعداد کل رکوردها')),
                ('processed_records', models.IntegerField(default=0, verbose_name='رکوردهای پردازش شده')),
                ('error_message', models.TextField(blank=True, verbose_name='پیام خطا')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('created_by', models.CharField(max_length=100, blank=True, verbose_name='ایجاد شده توسط')),
                ('main_category', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='prices.maincategory',
                    verbose_name='گروه اصلی'
                )),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='prices.category',
                    verbose_name='گروه'
                )),
                ('subcategory', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='prices.subcategory',
                    verbose_name='زیرگروه'
                )),
            ],
            options={
                'verbose_name': 'درخواست Scroll Time',
                'verbose_name_plural': 'درخواست‌های Scroll Time',
                'ordering': ['-created_at'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='maincategory',
            index=models.Index(fields=['value'], name='prices_main_value_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['main_category', 'value'], name='prices_cat_main_value_idx'),
        ),
        migrations.AddIndex(
            model_name='subcategory',
            index=models.Index(fields=['category', 'value'], name='prices_subcat_cat_value_idx'),
        ),
        migrations.AddIndex(
            model_name='scrolltimerequest',
            index=models.Index(fields=['status', 'created_at'], name='prices_scroll_status_date_idx'),
        ),
        
        # Add unique constraints
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('main_category', 'value')},
        ),
        migrations.AlterUniqueTogether(
            name='subcategory',
            unique_together={('category', 'value')},
        ),
    ]
