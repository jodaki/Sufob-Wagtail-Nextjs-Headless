# Management Commands راهنمای استفاده از

این پوشه شامل management commandهای سفارشی برای مدیریت دیتای اولیه پروژه است.

## Commands موجود

### 1. create_initial_data
این command دیتای اولیه مورد نیاز پروژه را ایجاد می‌کند.

#### استفاده:
```bash
# ایجاد تمام دیتای اولیه
python manage.py create_initial_data

# نادیده گرفتن ایجاد صفحات
python manage.py create_initial_data --skip-pages

# نادیده گرفتن ایجاد کاربران
python manage.py create_initial_data --skip-users

# نادیده گرفتن ایجاد محتوای بلاگ
python manage.py create_initial_data --skip-blog
```

#### چه چیزهایی ایجاد می‌کند:

**کاربران:**
- admin (superuser) با رمز admin123
- editor (کاربر ویرایشگر) با رمز password123
- author (نویسنده) با رمز password123
- viewer (کاربر عادی) با رمز password123

**صفحات:**
- صفحه اصلی (HomePage)
- صفحه ایندکس بلاگ (BlogPageIndex)

**محتوای بلاگ:**
- 5 دسته‌بندی: فناوری، برنامه‌نویسی، وب، دیتابیس، امنیت
- تگ‌های متنوع: Django، Python، Wagtail، JavaScript، و غیره
- 5 پست نمونه با محتوای کامل
- نظرات نمونه برای پست‌ها

### 2. clear_initial_data
این command تمام دیتای ایجاد شده توسط create_initial_data را پاک می‌کند.

#### استفاده:
```bash
# پاک کردن تمام دیتا (نیاز به تایید)
python manage.py clear_initial_data --confirm

# پاک کردن دیتا ولی نگه داشتن کاربران
python manage.py clear_initial_data --confirm --keep-users
```

⚠️ **هشدار:** این command تمام دیتای مرتبط را پاک می‌کند. حتماً از `--confirm` استفاده کنید.

## نکات مهم

1. **قبل از اجرا:** مطمئن شوید که migrations اجرا شده باشند:
   ```bash
   python manage.py migrate
   ```

2. **محیط توسعه:** این commandها برای محیط توسعه طراحی شده‌اند.

3. **کاربران:** تمام کاربران ایجاد شده رمز ساده دارند و باید در محیط تولید تغییر کنند.

4. **دیتا موجود:** اگر دیتا از قبل وجود داشته باشد، command آن را تکرار نمی‌کند.

## مثال کامل

```bash
# 1. اجرای migrations
python manage.py migrate

# 2. ایجاد دیتای اولیه
python manage.py create_initial_data

# 3. در صورت نیاز، پاک کردن دیتا
python manage.py clear_initial_data --confirm

# 4. ایجاد مجدد دیتا
python manage.py create_initial_data
```

## عیب‌یابی

اگر خطایی دریافت کردید:

1. مطمئن شوید که در virtual environment فعال هستید
2. مطمئن شوید که تمام dependencies نصب شده‌اند
3. مطمئن شوید که migrations اجرا شده‌اند
4. بررسی کنید که پایگاه داده در دسترس است

برای کمک بیشتر، خطا را بررسی کرده و مشکل را گزارش دهید.
