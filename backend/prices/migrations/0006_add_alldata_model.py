# Generated manually for AllData model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prices', '0005_pricedataimportproxy_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commodity_name', models.CharField(blank=True, max_length=100, verbose_name='نام کالا')),
                ('symbol', models.CharField(blank=True, max_length=50, verbose_name='نماد')),
                ('hall', models.CharField(blank=True, max_length=100, verbose_name='تالار')),
                ('producer', models.CharField(blank=True, max_length=200, verbose_name='تولیدکننده')),
                ('contract_type', models.CharField(blank=True, max_length=50, verbose_name='نوع قرارداد')),
                ('final_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='قیمت نهایی')),
                ('transaction_value', models.BigIntegerField(blank=True, default=0, null=True, verbose_name='ارزش معامله')),
                ('lowest_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='کمترین قیمت')),
                ('highest_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='بیشترین قیمت')),
                ('base_price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='قیمت پایه')),
                ('offer_volume', models.IntegerField(default=0, verbose_name='حجم عرضه')),
                ('demand_volume', models.IntegerField(default=0, verbose_name='حجم تقاضا')),
                ('contract_volume', models.IntegerField(blank=True, default=0, null=True, verbose_name='حجم قرارداد')),
                ('unit', models.CharField(blank=True, max_length=20, verbose_name='واحد')),
                ('transaction_date', models.CharField(blank=True, max_length=10, verbose_name='تاریخ معامله شمسی')),
                ('supplier', models.CharField(blank=True, max_length=200, verbose_name='عرضه‌کننده')),
                ('broker', models.CharField(blank=True, max_length=100, verbose_name='کارگزار')),
                ('settlement_type', models.CharField(blank=True, max_length=50, verbose_name='نحوه تسویه')),
                ('delivery_date', models.CharField(blank=True, max_length=10, null=True, verbose_name='تاریخ تحویل')),
                ('warehouse', models.CharField(blank=True, max_length=100, null=True, verbose_name='انبار')),
                ('settlement_date', models.CharField(blank=True, max_length=10, null=True, verbose_name='تاریخ تسویه')),
                ('x_talar_report_pk', models.IntegerField(blank=True, null=True, verbose_name='شناسه گزارش تالار')),
                ('currency', models.CharField(blank=True, max_length=20, null=True, verbose_name='ارز')),
                ('packet_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='نام بسته')),
                ('arzeh_pk', models.IntegerField(blank=True, null=True, verbose_name='شناسه عرضه')),
                ('raw_data', models.JSONField(blank=True, null=True, verbose_name='داده خام')),
                ('source', models.CharField(default='scroll-time', max_length=100, verbose_name='منبع داده')),
                ('api_endpoint', models.CharField(blank=True, max_length=200, null=True, verbose_name='نقطه انتهایی API')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')),
            ],
            options={
                'verbose_name': 'تمام داده‌ها',
                'verbose_name_plural': 'تمام داده‌ها',
                'ordering': ['-transaction_date', 'symbol'],
            },
        ),
        migrations.AddIndex(
            model_name='alldata',
            index=models.Index(fields=['commodity_name', 'transaction_date'], name='prices_alldata_comm_trans_idx'),
        ),
        migrations.AddIndex(
            model_name='alldata',
            index=models.Index(fields=['transaction_date'], name='prices_alldata_trans_date_idx'),
        ),
        migrations.AddIndex(
            model_name='alldata',
            index=models.Index(fields=['source'], name='prices_alldata_source_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='alldata',
            unique_together={('commodity_name', 'transaction_date')},
        ),
    ]
