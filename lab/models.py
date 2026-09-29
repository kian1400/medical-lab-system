from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class UserRole(models.Model):
    """نقش‌های کاربری"""
    ROLE_CHOICES = [
        ("patient", "بیمار"),
        ("receptionist", "منشی"),
        ("technician", "کارشناس"),
        ("doctor", "پزشک"),
        ("tech_manager", "مسئول فنی"),
        ("admin", "مدیر سیستم"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="role")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="patient")
    phone = models.CharField("تلفن", max_length=20, blank=True)
    address = models.TextField("نشانی", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"

class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "مرد"
        FEMALE = "F", "زن"
        OTHER = "O", "سایر"
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="patient")
    national_id = models.CharField("کد ملی", max_length=10, unique=True)
    first_name = models.CharField("نام", max_length=80)
    last_name = models.CharField("نام خانوادگی", max_length=100)
    birth_date = models.DateField("تاریخ تولد", null=True, blank=True)
    gender = models.CharField("جنسیت", max_length=1, choices=Gender.choices)
    phone = models.CharField("موبایل", max_length=20)
    email = models.EmailField("ایمیل", blank=True)
    address = models.TextField("نشانی", blank=True)
    city = models.CharField("شهر", max_length=100, blank=True)
    insurance_number = models.CharField("شماره بیمه", max_length=50, blank=True)
    emergency_contact = models.CharField("تماس اضطراری", max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.first_name} {self.last_name} - {self.national_id}"
    def full_name(self): return f"{self.first_name} {self.last_name}"

class Test(models.Model):
    code = models.CharField("کد آزمایش", max_length=30, unique=True)
    name = models.CharField("نام آزمایش", max_length=150)
    description = models.TextField("توضیحات", blank=True)
    category = models.CharField("دسته‌بندی", max_length=100, blank=True)
    price = models.DecimalField("هزینه", max_digits=12, decimal_places=0, default=0)
    discount_percentage = models.IntegerField("درصد تخفیف", default=0)
    unit = models.CharField("واحد", max_length=30, blank=True)
    reference_range = models.CharField("محدوده مرجع", max_length=200, blank=True)
    sample_type = models.CharField("نوع نمونه پیش‌فرض", max_length=80, default="خون")
    requires_fasting = models.BooleanField("نیاز به ناشتایی", default=False)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.code} - {self.name}"
    def final_price(self): return self.price * (100 - self.discount_percentage) // 100

class Appointment(models.Model):
    """��وبت‌های آزمایش"""
    STATUS_CHOICES = [
        ("available", "آزاد"),
        ("booked", "رزرو‌شده"),
        ("completed", "انجام‌شده"),
        ("cancelled", "لغوشده"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_date = models.DateField("تاریخ نوبت")
    appointment_time = models.TimeField("ساعت نوبت")
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, null=True, blank=True, related_name="appointments")
    status = models.CharField("وضعیت", max_length=20, choices=STATUS_CHOICES, default="available")
    notes = models.TextField("یادداشت", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.appointment_date} {self.appointment_time}"

class Order(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "registered", "پذیرش‌شده"
        SAMPLING = "sampling", "نمونه‌گیری‌شده"
        PROCESSING = "processing", "در حال انجام"
        WAITING_APPROVAL = "waiting_approval", "در انتظار تأیید"
        APPROVED = "approved", "تأیید نهایی"
        CANCELLED = "cancelled", "لغوشده"
    
    class Type(models.TextChoices):
        CLINIC = "clinic", "کلینیک"
        HOME = "home", "منزل"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracking_code = models.CharField("کد رهگیری", max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="orders")
    physician = models.CharField("پزشک درخواست‌کننده", max_length=150, blank=True)
    order_type = models.CharField("نوع سفارش", max_length=20, choices=Type.choices, default=Type.CLINIC)
    status = models.CharField("وضعیت", max_length=30, choices=Status.choices, default=Status.REGISTERED)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    notes = models.TextField("یادداشت", blank=True)
    total_price = models.DecimalField("قیمت کل", max_digits=12, decimal_places=0, default=0)
    is_paid = models.BooleanField("پرداخت‌شده", default=False)
    registered_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="registered_orders")
    registered_at = models.DateTimeField(auto_now_add=True)
    sampled_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="approved_orders")
    def __str__(self): return self.tracking_code

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    test = models.ForeignKey(Test, on_delete=models.PROTECT)
    sample_type = models.CharField("نوع نمونه", max_length=80, default="خون")
    price = models.DecimalField("قیمت", max_digits=12, decimal_places=0, default=0)
    def __str__(self): return f"{self.order.tracking_code} / {self.test.name}"

class Result(models.Model):
    item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name="result")
    value = models.CharField("نتیجه", max_length=500, blank=True)
    numeric_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    comment = models.TextField("توضیحات", blank=True)
    entered_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="entered_results")
    entered_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField("تأیید‌شده", default=False)
    def __str__(self): return self.item.test.name

class ActivityLog(models.Model):
    """ثبت لاگ فعالیت‌های حساس"""
    ACTION_CHOICES = [
        ("create", "ایجاد"),
        ("update", "بروزرسانی"),
        ("delete", "حذف"),
        ("approve", "تأیید"),
        ("payment", "پرداخت"),
        ("view", "مشاهده"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField("عملیات", max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField("مدل", max_length=100)
    object_id = models.CharField("شناسه شی", max_length=255)
    description = models.TextField("توضیحات")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.user} - {self.get_action_display()} - {self.model_name}"

class Payment(models.Model):
    """مدیریت پرداخت‌ها"""
    STATUS_CHOICES = [
        ("pending", "درانتظار"),
        ("completed", "تکمیل‌شده"),
        ("failed", "ناموفق"),
        ("refunded", "برگشت‌داده‌شده"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField("مبلغ", max_digits=12, decimal_places=0)
    status = models.CharField("وضعیت", max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_gateway = models.CharField("درگاه پرداخت", max_length=50, blank=True)
    transaction_id = models.CharField("شناسه تراکنش", max_length=255, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"{self.order.tracking_code} - {self.amount}"
