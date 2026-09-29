import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Count, Sum
from django.utils import timezone

from .models import Order, Patient, Test


@login_required
def admin_reports(request):
    if not request.user.is_staff:
        messages.error(request, "دسترسی شما محدود است.")
        return redirect("home")

    revenue = Order.objects.filter(is_paid=True).aggregate(total=Sum('total_price'))['total'] or 0
    counts = Order.objects.aggregate(
        total_orders=Count('id'),
        waiting_approval=Count('id', filter=models.Q(status=Order.Status.WAITING_APPROVAL)),
        approved=Count('id', filter=models.Q(status=Order.Status.APPROVED)),
    )
    top_tests = (
        Order.objects.filter(items__isnull=False)
        .values('items__test__name')
        .annotate(total=Count('items__test__name'))
        .order_by('-total')[:5]
    )
    recent = Order.objects.select_related('patient').order_by('-registered_at')[:15]
    return render(request, 'admin/reports.html', {
        'revenue': revenue,
        'counts': counts,
        'top_tests': top_tests,
        'recent': recent,
        'today': timezone.localdate(),
    })


@login_required
def export_orders_csv(request):
    if not request.user.is_staff:
        messages.error(request, "دسترسی شما محدود است.")
        return redirect("home")

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="lab_orders_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['کد رهگیری', 'بیمار', 'تاریخ ثبت', 'وضعیت', 'جمع کل', 'پرداخت'])
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
