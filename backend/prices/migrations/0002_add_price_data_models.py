# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commodity_name', models.CharField(choices=[('کنسانتره آهن', 'کنسانتره آهن'), ('سنگ آهن', 'سنگ آهن'), ('کاتد مس', 'کاتد مس'), ('شمش آلومینیوم', 'شمش آلومینیوم'), ('کک متالورژی', 'کک متالورژی'), ('طلا', 'طلا'), ('نقره', 'نقره'), ('مس', 'مس'), ('آلومینیوم', 'آلومینیوم'), ('روی', 'روی')], max_length=100, verbose_name='نام کالا')),
                ('symbol', models.CharField(blank=True, max_length=50, verbose_name='نماد')),
                ('price_date', models.DateField(verbose_name='تاریخ قیمت')),
                ('final_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='قیمت نهایی')),
                ('avg_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='قیمت متوسط')),
                ('lowest_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='کمترین قیمت')),
                ('highest_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='بیشترین قیمت')),
                ('volume', models.BigIntegerField(blank=True, null=True, verbose_name='حجم معاملات')),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='ارزش معاملات')),
                ('unit', models.CharField(blank=True, max_length=20, verbose_name='واحد')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('source', models.CharField(default='manual', max_length=100, verbose_name='منبع داده')),
            ],
            options={
                'verbose_name': 'داده قیمت',
                'verbose_name_plural': 'داده‌های قیمت',
                'ordering': ['-price_date', 'commodity_name'],
            },
        ),
        migrations.CreateModel(
            name='DataImportLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commodity_name', models.CharField(max_length=100, verbose_name='نام کالا')),
                ('start_date', models.DateField(verbose_name='تاریخ شروع')),
                ('end_date', models.DateField(verbose_name='تاریخ پایان')),
                ('total_records', models.IntegerField(default=0, verbose_name='تعداد کل رکوردها')),
                ('imported_records', models.IntegerField(default=0, verbose_name='رکوردهای وارد شده')),
                ('updated_records', models.IntegerField(default=0, verbose_name='رکوردهای بروزرسانی شده')),
                ('duplicate_records', models.IntegerField(default=0, verbose_name='رکوردهای تکراری')),
                ('error_records', models.IntegerField(default=0, verbose_name='رکوردهای خطا')),
                ('status', models.CharField(choices=[('success', 'موفق'), ('error', 'خطا'), ('partial', 'جزئی')], max_length=20, verbose_name='وضعیت')),
                ('error_message', models.TextField(blank=True, verbose_name='پیام خطا')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('created_by', models.CharField(blank=True, max_length=100, verbose_name='ایجاد شده توسط')),
            ],
            options={
                'verbose_name': 'لاگ وارد کردن داده',
                'verbose_name_plural': 'لاگ‌های وارد کردن داده',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pricedata',
            index=models.Index(fields=['commodity_name', 'price_date'], name='prices_pric_commodi_7c7b6b_idx'),
        ),
        migrations.AddIndex(
            model_name='pricedata',
            index=models.Index(fields=['price_date'], name='prices_pric_price_d_4a7c3f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='pricedata',
            unique_together={('commodity_name', 'price_date')},
        ),
    ]
