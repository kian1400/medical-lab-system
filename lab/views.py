import secrets
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Order, OrderItem, Patient, Result, Test

@login_required
def dashboard(request):
    context = {"orders": Order.objects.select_related("patient").order_by("-registered_at")[:20],
               "counts": {"today": Order.objects.filter(registered_at__date=timezone.localdate()).count(),
                          "pending": Order.objects.filter(status=Order.Status.WAITING_APPROVAL).count(),
                          "patients": Patient.objects.count()}}
    return render(request, "lab/dashboard.html", context)

@login_required
def intake(request):
    if request.method == "POST":
        national_id = request.POST["national_id"].strip()
        patient, _ = Patient.objects.get_or_create(national_id=national_id, defaults={
            "first_name": request.POST["first_name"], "last_name": request.POST["last_name"],
            "gender": request.POST.get("gender", Patient.Gender.OTHER), "phone": request.POST["phone"]})
        codes = request.POST.getlist("tests")
        with transaction.atomic():
            order = Order.objects.create(tracking_code=secrets.token_hex(5).upper(), patient=patient,
                physician=request.POST.get("physician", ""), registered_by=request.user)
            OrderItem.objects.bulk_create([OrderItem(order=order, test_id=code) for code in codes])
        messages.success(request, f"پذیرش با کد {order.tracking_code} ثبت شد.")
        return redirect("lab:order_detail", order.tracking_code)
    return render(request, "lab/intake.html", {"tests": Test.objects.filter(is_active=True)})

@login_required
def order_detail(request, tracking_code):
    order = get_object_or_404(Order.objects.prefetch_related("items__test", "items__result"), tracking_code=tracking_code)
    return render(request, "lab/order_detail.html", {"order": order})

@login_required
def enter_results(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    if request.method == "POST":
        for item in order.items.all():
            Result.objects.update_or_create(item=item, defaults={"value": request.POST.get(f"value_{item.pk}", ""), "comment": request.POST.get(f"comment_{item.pk}", ""), "entered_by": request.user})
        order.status = Order.Status.WAITING_APPROVAL
        order.save(update_fields=["status"])
        messages.success(request, "نتایج ثبت و برای تأیید مسئول فنی ارسال شد.")
        return redirect("lab:order_detail", tracking_code)
    return render(request, "lab/enter_results.html", {"order": order})

@login_required
def approve_order(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    if not request.user.is_staff:
        messages.error(request, "فقط مسئول فنی مجاز به تأیید نتیجه است.")
        return redirect("lab:order_detail", tracking_code)
    if request.method == "POST":
        order.status, order.approved_by, order.approved_at = Order.Status.APPROVED, request.user, timezone.now()
        order.items.filter(result__isnull=False).update(result__verified=True)
        order.save(update_fields=["status", "approved_by", "approved_at"])
        messages.success(request, "نتیجه با موفقیت تأیید شد.")
    return redirect("lab:order_detail", tracking_code)
