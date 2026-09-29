{% extends 'base.html' %}
{% block title %}گزارش‌ها | آزمایشگاه مهر{% endblock %}
{% block content %}
<h2 class="page-title">گزارش‌های مدیریتی</h2>
<div class="stats">
    <div class="stat"><h3>{{ stats.total_orders }}</h3><small>کل سفارش‌ها</small></div>
    <div class="stat"><h3>{{ stats.waiting_approval }}</h3><small>در انتظار تأیید</small></div>
    <div class="stat"><h3>{{ stats.approved }}</h3><small>تأیید شده</small></div>
    <div class="stat"><h3>{{ stats.revenue|floatformat:0 }}</h3><small>درآمد</small></div>
</div>

<div class="card" style="padding:20px; margin-top:24px;">
    <h3>پرفروش‌ترین آزمایش‌ها</h3>
    <table>
        <tr><th>نام آزمایش</th><th>تعداد درخواست</th></tr>
        {% for item in top_tests %}
        <tr><td>{{ item.test__name }}</td><td>{{ item.count }}</td></tr>
        {% empty %}<tr><td colspan="2">داده‌ای وجود ندارد.</td></tr>{% endfor %}
    </table>
</div>

<div class="card" style="padding:20px; margin-top:24px;">
    <h3>آخرین سفارش‌ها</h3>
    <a class="btn" href="{% url 'export_orders_csv' %}">دانلود CSV</a>
    <table>
        <tr><th>کد رهگیری</th><th>بیمار</th><th>تاریخ</th><th>مبلغ</th><th>وضعیت</th></tr>
        {% for order in recent %}
        <tr>
            <td>{{ order.tracking_code }}</td>
            <td>{{ order.patient.first_name }} {{ order.patient.last_name }}</td>
            <td>{{ order.registered_at|date:'Y/m/d H:i' }}</td>
            <td>{{ order.total_price }}</td>
            <td>{{ order.get_status_display }}</td>
        </tr>
        {% endfor %}
    </table>
</div>
{% endblock %}
