from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "مرد"
        FEMALE = "F", "زن"
        OTHER = "O", "سایر"
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    national_id = models.CharField("کد ملی", max_length=10, unique=True)
    first_name = models.CharField("نام", max_length=80)
    last_name = models.CharField("نام خانوادگی", max_length=100)
    birth_date = models.DateField("تاریخ تولد", null=True, blank=True)
    gender = models.CharField("جنسیت", max_length=1, choices=Gender.choices)
    phone = models.CharField("موبایل", max_length=20)
    address = models.TextField("نشانی", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.first_name} {self.last_name} - {self.national_id}"

class Test(models.Model):
    code = models.CharField("کد آزمایش", max_length=30, unique=True)
    name = models.CharField("نام آزمایش", max_length=150)
    category = models.CharField("دسته‌بندی", max_length=100, blank=True)
    price = models.DecimalField("هزینه", max_digits=12, decimal_places=0, default=0)
    unit = models.CharField("واحد", max_length=30, blank=True)
    reference_range = models.CharField("محدوده مرجع", max_length=200, blank=True)
    is_active = models.BooleanField("فعال", default=True)
    def __str__(self): return f"{self.code} - {self.name}"

class Order(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "registered", "پذیرش‌شده"
        SAMPLING = "sampling", "نمونه‌گیری‌شده"
        PROCESSING = "processing", "در حال انجام"
        WAITING_APPROVAL = "waiting_approval", "در انتظار تأیید"
        APPROVED = "approved", "تأیید نهایی"
        CANCELLED = "cancelled", "لغوشده"
    tracking_code = models.CharField("کد رهگیری", max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="orders")
    physician = models.CharField("پزشک درخواست‌کننده", max_length=150, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.REGISTERED)
    notes = models.TextField("یادداشت", blank=True)
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
    def __str__(self): return f"{self.order.tracking_code} / {self.test.name}"

class Result(models.Model):
    item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name="result")
    value = models.CharField("نتیجه", max_length=500, blank=True)
    numeric_value = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    comment = models.TextField("توضیحات", blank=True)
    entered_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="entered_results")
    entered_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField("تأییدشده", default=False)
    def __str__(self): return self.item.test.name
