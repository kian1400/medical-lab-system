{% extends 'base.html' %}
{% block title %}ورود نتایج | آزمایشگاه مهر{% endblock %}
{% block content %}
<div class="card" style="padding:24px;">
    <h2 class="page-title">ورود نتایج: {{ order.tracking_code }}</h2>
    <form method="post">
        {% csrf_token %}
        {% for item in order.items.all %}
            <div class="card" style="padding:18px; margin-bottom:16px;">
                <h3>{{ item.test.name }}</h3>
                <div class="two-col">
                    <div><label>نتیجه</label><input name="value_{{ item.pk }}" value="{% if item.result %}{{ item.result.value }}{% endif %}"></div>
                    <div><label>توضیحات</label><textarea name="comment_{{ item.pk }}">{% if item.result %}{{ item.result.comment }}{% endif %}</textarea></div>
                </div>
            </div>
        {% endfor %}
        <button class="btn" type="submit">ثبت و ارسال برای تأیید</button>
    </form>
</div>
{% endblock %}
