from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('national_id', models.CharField(max_length=10, unique=True, verbose_name='کد ملی')),
                ('first_name', models.CharField(max_length=80, verbose_name='نام')),
                ('last_name', models.CharField(max_length=100, verbose_name='نام خانوادگی')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='تاریخ تولد')),
                ('gender', models.CharField(choices=[('M', 'مرد'), ('F', 'زن'), ('O', 'سایر')], max_length=1, verbose_name='جنسیت')),
                ('phone', models.CharField(max_length=20, verbose_name='موبایل')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='ایمیل')),
                ('address', models.TextField(blank=True, verbose_name='نشانی')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='شهر')),
                ('insurance_number', models.CharField(blank=True, max_length=50, verbose_name='شماره بیمه')),
                ('emergency_contact', models.CharField(blank=True, max_length=100, verbose_name='تماس اضطراری')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='patient', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=30, unique=True, verbose_name='کد آزمایش')),
                ('name', models.CharField(max_length=150, verbose_name='نام آزمایش')),
                ('description', models.TextField(blank=True, verbose_name='توضیحات')),
                ('category', models.CharField(blank=True, max_length=100, verbose_name='دسته‌بندی')),
                ('price', models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='هزینه')),
                ('discount_percentage', models.IntegerField(default=0, verbose_name='درصد تخفیف')),
                ('unit', models.CharField(blank=True, max_length=30, verbose_name='واحد')),
                ('reference_range', models.CharField(blank=True, max_length=200, verbose_name='محدوده مرجع')),
                ('sample_type', models.CharField(default='خون', max_length=80, verbose_name='نوع نمونه پیش‌فرض')),
                ('requires_fasting', models.BooleanField(default=False, verbose_name='نیاز به ناشتایی')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('patient', 'بیمار'), ('receptionist', 'منشی'), ('technician', 'کارشناس'), ('doctor', 'پزشک'), ('tech_manager', 'مسئول فنی'), ('admin', 'مدیر سیستم')], default='patient', max_length=20)),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='تلفن')),
                ('address', models.TextField(blank=True, verbose_name='نشانی')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='role', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.UUIDField(default=django.db.models.deletion.uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('appointment_date', models.DateField(verbose_name='تاریخ نوبت')),
                ('appointment_time', models.TimeField(verbose_name='ساعت نوبت')),
                ('status', models.CharField(choices=[('available', 'آزاد'), ('booked', 'رزرو‌شده'), ('completed', 'انجام‌شده'), ('cancelled', 'لغوشده')], default='available', max_length=20, verbose_name='وضعیت')),
                ('notes', models.TextField(blank=True, verbose_name='یادداشت')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='lab.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=django.db.models.deletion.uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tracking_code', models.CharField(max_length=20, unique=True, verbose_name='کد رهگیری')),
                ('physician', models.CharField(blank=True, max_length=150, verbose_name='پزشک درخواست‌کننده')),
                ('order_type', models.CharField(choices=[('clinic', 'کلینیک'), ('home', 'منزل')], default='clinic', max_length=20, verbose_name='نوع سفارش')),
                ('status', models.CharField(choices=[('registered', 'پذیرش‌شده'), ('sampling', 'نمونه‌گیری‌شده'), ('processing', 'در حال انجام'), ('waiting_approval', 'در انتظار تأیید'), ('approved', 'تأیید نهایی'), ('cancelled', 'لغوشده')], default='registered', max_length=30, verbose_name='وضعیت')),
                ('notes', models.TextField(blank=True, verbose_name='یادداشت')),
                ('total_price', models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='قیمت کل')),
                ('is_paid', models.BooleanField(default=False, verbose_name='پرداخت‌شده')),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('sampled_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='lab.appointment')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='approved_orders', to='auth.user')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='lab.patient')),
                ('registered_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='registered_orders', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_type', models.CharField(default='خون', max_length=80, verbose_name='نوع نمونه')),
                ('price', models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='قیمت')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='lab.order')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='lab.test')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(blank=True, max_length=500, verbose_name='نتیجه')),
                ('numeric_value', models.DecimalField(blank=True, decimal_places=4, max_digits=12, null=True)),
                ('comment', models.TextField(blank=True, verbose_name='توضیحات')),
                ('entered_at', models.DateTimeField(auto_now=True)),
                ('verified', models.BooleanField(default=False, verbose_name='تأیید‌شده')),
                ('entered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='entered_results', to='auth.user')),
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='lab.orderitem')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.UUIDField(default=django.db.models.deletion.uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[('create', 'ایجاد'), ('update', 'بروزرسانی'), ('delete', 'حذف'), ('approve', 'تأیید'), ('payment', 'پرداخت'), ('view', 'مشاهده')], max_length=20, verbose_name='عملیات')),
                ('model_name', models.CharField(max_length=100, verbose_name='مدل')),
                ('object_id', models.CharField(max_length=255, verbose_name='شناسه شی')),
                ('description', models.TextField(verbose_name='توضیحات')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=django.db.models.deletion.uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='مبلغ')),
                ('status', models.CharField(choices=[('pending', 'درانتظار'), ('completed', 'تکمیل‌شده'), ('failed', 'ناموفق'), ('refunded', 'برگشت‌داده‌شده')], default='pending', max_length=20, verbose_name='وضعیت')),
                ('payment_gateway', models.CharField(blank=True, max_length=50, verbose_name='درگاه پرداخت')),
                ('transaction_id', models.CharField(blank=True, max_length=255, unique=True, verbose_name='شناسه تراکنش')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='lab.order')),
            ],
        ),
    ]
