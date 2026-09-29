import csv
import json
import secrets
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .forms import AppointmentBookingForm, LoginForm, NewOrderForm, PatientProfileForm, PatientRegistrationForm
from .models import ActivityLog, Appointment, Order, OrderItem, Patient, Payment, Result, Test, UserRole


def log_activity(user, action, model_name, object_id, description):
    ActivityLog.objects.create(user=user, action=action, model_name=model_name, object_id=str(object_id), description=description)


def register_patient(request):
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                username = form.cleaned_data["national_id"]
                user = User.objects.create_user(
                    username=username,
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                )
                UserRole.objects.create(user=user, role="patient", phone=form.cleaned_data["phone"])
                patient = form.save(commit=False)
                patient.user = user
                patient.save()
                log_activity(user, "create", "Patient", patient.id, f"ثبت‌نام بیمار جدید: {patient.full_name()}")
            messages.success(request, "ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.")
            return redirect("login")
    else:
        form = PatientRegistrationForm()
    return render(request, "auth/register.html", {"form": form})


def patient_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                log_activity(user, "view", "Login", user.id, "ورود به سیستم")
                return redirect("patient_dashboard")
            messages.error(request, "نام کاربری یا رمز عبور اشتباه است.")
    else:
        form = LoginForm()
    return render(request, "auth/login.html", {"form": form})


def patient_logout(request):
    if request.user.is_authenticated:
        log_activity(request.user, "view", "Logout", request.user.id, "خروج از سیستم")
    logout(request)
    messages.success(request, "با موفقیت خارج شدید.")
    return redirect("home")


def home(request):
    tests = Test.objects.filter(is_active=True)
    return render(request, "home.html", {"tests": tests})


def services(request):
    tests = Test.objects.filter(is_active=True).order_by("category", "name")
    grouped = {}
    for test in tests:
        grouped.setdefault(test.category or "سایر", []).append(test)
    return render(request, "services.html", {"categories": grouped})


@login_required
def patient_dashboard(request):
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, "پروفایل بیمار یافت نشد.")
        return redirect("home")

    orders = patient.orders.select_related("patient").order_by("-registered_at")
    appointments = patient.appointments.filter(status__in=["available", "booked"]).order_by("appointment_date")
    context = {
        "patient": patient,
        "orders": orders,
        "appointments": appointments,
        "recent_orders": orders[:5],
        "total_spent": sum(float(o.total_price) for o in orders if o.is_paid),
    }
    return render(request, "patient/dashboard.html", context)


@login_required
def patient_profile(request):
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, "پروفایل بیمار یافت نشد.")
        return redirect("home")

    if request.method == "POST":
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            log_activity(request.user, "update", "Patient", patient.id, "بروزرسانی پروفایل بیمار")
            messages.success(request, "پروفایل با موفقیت بروزرس��نی شد.")
            return redirect("patient_profile")
    else:
        form = PatientProfileForm(instance=patient)
    return render(request, "patient/profile.html", {"form": form, "patient": patient})


@login_required
def patient_orders(request):
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, "پروفایل بیمار یافت نشد.")
        return redirect("home")
    orders = patient.orders.select_related("patient").order_by("-registered_at")
    return render(request, "patient/orders.html", {"orders": orders})


@login_required
def order_detail(request, tracking_code):
    order = get_object_or_404(Order.objects.prefetch_related("items__test", "items__result"), tracking_code=tracking_code)
    try:
        if request.user.patient != order.patient and not request.user.is_staff:
            messages.error(request, "شما دسترسی به این سفارش را ندارید.")
            return redirect("patient_dashboard")
    except Patient.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, "شما دسترسی به این سفارش را ندارید.")
            return redirect("patient_dashboard")
    log_activity(request.user, "view", "Order", order.id, f"مشاهده سفارش: {order.tracking_code}")
    return render(request, "patient/order_detail.html", {"order": order})


@login_required
def create_order(request):
    if request.method == "POST":
        form = NewOrderForm(request.POST)
        if form.is_valid():
            patient = request.user.patient
            tests = form.cleaned_data["tests"]
            order = Order.objects.create(
                tracking_code=secrets.token_hex(5).upper(),
                patient=patient,
                registered_by=request.user,
                order_type=form.cleaned_data["order_type"],
                notes=form.cleaned_data["notes"],
            )
            total = 0
            for test in tests:
                price = test.final_price()
                OrderItem.objects.create(order=order, test=test, sample_type=test.sample_type, price=price)
                total += price
            order.total_price = total
            order.save(update_fields=["total_price"])
            log_activity(request.user, "create", "Order", order.id, f"ثبت سفارش جدید: {order.tracking_code}")
            messages.success(request, f"سفارش شما با کد رهگیری {order.tracking_code} ثبت شد.")
            return redirect("payment_checkout", order.tracking_code)
    else:
        form = NewOrderForm()
    return render(request, "patient/create_order.html", {"form": form})


@login_required
def book_appointment(request):
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, "پروفایل بیمار یافت نشد.")
        return redirect("patient_dashboard")

    if request.method == "POST":
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.status = "booked"
            appointment.save()
            messages.success(request, "نوبت شما با موفقیت ثبت شد.")
            return redirect("patient_dashboard")
    else:
        form = AppointmentBookingForm()
    return render(request, "patient/book_appointment.html", {"form": form})


@login_required
def payment_checkout(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    if request.user.patient != order.patient and not request.user.is_staff:
        messages.error(request, "شما دسترسی ندارید.")
        return redirect("patient_dashboard")

    if request.method == "POST":
        Payment.objects.create(
            order=order,
            amount=order.total_price,
            status="completed",
            payment_gateway="gateway_mock",
            transaction_id=f"TX-{secrets.token_hex(6).upper()}",
        )
        order.is_paid = True
        order.save(update_fields=["is_paid"])
        log_activity(request.user, "payment", "Payment", order.id, f"پرداخت سفارش: {order.tracking_code}")
        messages.success(request, "پرداخت با موفقیت انجام شد.")
        return redirect("order_detail", order.tracking_code)

    return render(request, "patient/payment_checkout.html", {"order": order})


@login_required
def download_result_pdf(request, tracking_code):
    order = get_object_or_404(Order.objects.prefetch_related("items__result__item__test"), tracking_code=tracking_code)
    if request.user.patient != order.patient and not request.user.is_staff:
        messages.error(request, "دسترسی به نتیجه وجود ندارد.")
        return redirect("patient_dashboard")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("گزارش نتیجه آزمایش", styles['Title']))
    story.append(Paragraph(f"کد رهگیری: {order.tracking_code}", styles['Normal']))
    story.append(Paragraph(f"بیمار: {order.patient.first_name} {order.patient.last_name}", styles['Normal']))
    story.append(Spacer(1, 20))
    data = [["نام آزمایش", "نتیجه", "توضیح", "وضعیت"]]
    for item in order.items.all():
        result = item.result
        status = "تأیید شده" if result and result.verified else "در انتظار تأیید"
        data.append([item.test.name, result.value if result else '-', result.comment if result else '-', status])
    table = Table(data, colWidths=[120, 120, 170, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f5ba7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(table)
    doc.build(story)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="result_{order.tracking_code}.pdf"'
    return response


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "شما دسترسی ندارید.")
        return redirect("home")
    today = timezone.localdate()
    context = {
        "orders_today": Order.objects.filter(registered_at__date=today).count(),
        "pending_approval": Order.objects.filter(status=Order.Status.WAITING_APPROVAL).count(),
        "total_patients": Patient.objects.count(),
        "total_revenue": sum(float(o.total_price) for o in Order.objects.filter(is_paid=True)),
        "recent_orders": Order.objects.select_related("patient").order_by("-registered_at")[:10],
    }
    return render(request, "admin/dashboard.html", context)


@login_required
def staff_intake(request):
    if not request.user.is_staff:
        messages.error(request, "شما دسترسی ندارید.")
        return redirect("home")

    if request.method == "POST":
        national_id = request.POST["national_id"].strip()
        patient, _ = Patient.objects.get_or_create(national_id=national_id, defaults={
            "first_name": request.POST["first_name"],
            "last_name": request.POST["last_name"],
            "gender": request.POST.get("gender", Patient.Gender.OTHER),
            "phone": request.POST["phone"],
        })
        test_ids = request.POST.getlist("tests")
        order_type = request.POST.get("order_type", Order.Type.CLINIC)
        with transaction.atomic():
            order = Order.objects.create(
                tracking_code=secrets.token_hex(5).upper(),
                patient=patient,
                physician=request.POST.get("physician", ""),
                registered_by=request.user,
                order_type=order_type,
            )
            total_price = 0
            for test_id in test_ids:
                test = Test.objects.get(pk=test_id)
                item = OrderItem.objects.create(order=order, test=test, price=test.final_price())
                total_price += item.price
            order.total_price = total_price
            order.save(update_fields=["total_price"])
            log_activity(request.user, "create", "Order", order.id, f"ثبت سفارش جدید: {order.tracking_code}")
        messages.success(request, f"پذیرش با کد {order.tracking_code} ثبت شد.")
        return redirect("order_detail", order.tracking_code)
    return render(request, "admin/intake.html", {"tests": Test.objects.filter(is_active=True)})


@login_required
def enter_results(request, tracking_code):
    if not request.user.is_staff:
        messages.error(request, "شما دسترسی ندارید.")
        return redirect("home")
    order = get_object_or_404(Order, tracking_code=tracking_code)
    if request.method == "POST":
        with transaction.atomic():
            for item in order.items.all():
                Result.objects.update_or_create(
                    item=item,
                    defaults={
                        "value": request.POST.get(f"value_{item.pk}", ""),
                        "comment": request.POST.get(f"comment_{item.pk}", ""),
                        "entered_by": request.user,
                    },
                )
            order.status = Order.Status.WAITING_APPROVAL
            order.save(update_fields=["status"])
            log_activity(request.user, "update", "Order", order.id, f"ورود نتایج سفارش: {order.tracking_code}")
        messages.success(request, "نتایج ثبت و برای تأیید مسئول فنی ارسال شد.")
        return redirect("order_detail", tracking_code)
    return render(request, "admin/enter_results.html", {"order": order})


@login_required
def approve_order(request, tracking_code):
    order = get_object_or_404(Order, tracking_code=tracking_code)
    if not request.user.is_staff:
        messages.error(request, "فقط مسئول فنی مجاز به تأیید نتیجه است.")
        return redirect("order_detail", tracking_code)
    if request.method == "POST":
        with transaction.atomic():
            order.status = Order.Status.APPROVED
            order.approved_by = request.user
            order.approved_at = timezone.now()
            order.save(update_fields=["status", "approved_by", "approved_at"])
            Result.objects.filter(item__order=order, verified=False).update(verified=True)
            log_activity(request.user, "approve", "Order", order.id, f"تأیید نهایی نتایج: {order.tracking_code}")
        messages.success(request, "نتیجه با موفقیت تأیید شد.")
    return redirect("order_detail", tracking_code)


@login_required
def admin_reports(request):
    if not request.user.is_staff:
        messages.error(request, "دسترسی شما محدود است.")
        return redirect("home")
    revenue = Order.objects.filter(is_paid=True).aggregate(total=Sum('total_price'))['total'] or 0
    stats = {
        'total_orders': Order.objects.count(),
        'waiting_approval': Order.objects.filter(status=Order.Status.WAITING_APPROVAL).count(),
        'approved': Order.objects.filter(status=Order.Status.APPROVED).count(),
        'patients': Patient.objects.count(),
        'revenue': revenue,
    }
    top_tests = OrderItem.objects.values('test__name').annotate(count=Count('id')).order_by('-count')[:5]
    recent = Order.objects.select_related('patient').order_by('-registered_at')[:15]
    return render(request, 'admin/reports.html', {'stats': stats, 'top_tests': top_tests, 'recent': recent})


@login_required
def export_orders_csv(request):
    if not request.user.is_staff:
        messages.error(request, "دسترسی شما محدود است.")
        return redirect("home")
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="orders_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['کد رهگیری', 'بیمار', 'تاریخ', 'وضعیت', 'جمع کل', 'پرداخت شده'])
    for order in Order.objects.select_related('patient').order_by('-registered_at'):
        writer.writerow([
            order.tracking_code,
            f"{order.patient.first_name} {order.patient.last_name}",
            order.registered_at.strftime('%Y/%m/%d %H:%M'),
            order.get_status_display(),
            order.total_price,
            'بله' if order.is_paid else 'خیر',
        ])
    return response


@login_required
def api_order_status(request, tracking_code):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    order = get_object_or_404(Order, tracking_code=tracking_code)
    return JsonResponse({
        'tracking_code': order.tracking_code,
        'status': order.status,
        'status_label': order.get_status_display(),
        'is_paid': order.is_paid,
        'total_price': str(order.total_price),
        'patient': f"{order.patient.first_name} {order.patient.last_name}",
    })


def api_tests(request):
    data = [{
        'id': test.id,
        'code': test.code,
        'name': test.name,
        'category': test.category,
        'price': int(test.final_price()),
        'sample_type': test.sample_type,
    } for test in Test.objects.filter(is_active=True)]
    return JsonResponse({'results': data})
