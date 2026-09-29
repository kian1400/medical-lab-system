from django.contrib import admin
from .models import Patient, Test, Order, OrderItem, Result

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("national_id", "first_name", "last_name", "phone", "created_at")
    search_fields = ("national_id", "first_name", "last_name", "phone")

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "price", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("code", "name")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("tracking_code", "patient", "status", "registered_at", "approved_at")
    list_filter = ("status", "registered_at")
    search_fields = ("tracking_code", "patient__national_id", "patient__last_name")
    readonly_fields = ("registered_at", "approved_at")
    inlines = (OrderItemInline,)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("item", "value", "verified", "entered_by", "entered_at")
    list_filter = ("verified",)
    search_fields = ("item__order__tracking_code", "item__test__name")
