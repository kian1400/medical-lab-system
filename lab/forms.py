from django import forms
from django.contrib.auth.models import User
from .models import Patient, Order, OrderItem, Test, Appointment

class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="تکرار رمز عبور")
    email = forms.EmailField(label="ایمیل")
    
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "national_id", "birth_date", "gender", "phone", "email", "address", "city"]
        labels = {
            "first_name": "نام", "last_name": "نام خانوادگی", "national_id": "کد ملی",
            "birth_date": "تاریخ تولد", "gender": "جنسیت", "phone": "موبایل",
            "email": "ایمیل", "address": "نشانی", "city": "شهر"
        }
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("رمزهای عبور مطابقت ندارند.")
        return cleaned_data

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "birth_date", "gender", "phone", "email", "address", "city", "emergency_contact", "insurance_number"]
        labels = {
            "first_name": "نام", "last_name": "نام خانوادگی", "birth_date": "تاریخ تولد",
            "gender": "جنسیت", "phone": "موبایل", "email": "ایمیل",
            "address": "نشانی", "city": "شهر", "emergency_contact": "تماس اضطراری", "insurance_number": "شماره بیمه"
        }
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}

class LoginForm(forms.Form):
    username = forms.CharField(label="نام کاربری", max_length=150)
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)

class NewOrderForm(forms.ModelForm):
    tests = forms.ModelMultipleChoiceField(queryset=Test.objects.filter(is_active=True), label="آزمایش‌ها", widget=forms.CheckboxSelectMultiple)
    
    class Meta:
        model = Order
        fields = ["order_type", "notes"]
        labels = {"order_type": "نوع سفارش", "notes": "یادداشت"}

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["appointment_date", "appointment_time"]
        labels = {"appointment_date": "تاریخ", "appointment_time": "ساعت"}
        widgets = {"appointment_date": forms.DateInput(attrs={"type": "date"}), "appointment_time": forms.TimeInput(attrs={"type": "time"})}
