from django.urls import path
from . import views
app_name = "lab"
urlpatterns = [
    # صفحات عمومی
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    
    # احراز هویت
    path("register/", views.register_patient, name="register"),
    path("login/", views.patient_login, name="login"),
    path("logout/", views.patient_logout, name="logout"),
    
    # پنل بیمار
    path("dashboard/", views.patient_dashboard, name="patient_dashboard"),
    path("profile/", views.patient_profile, name="patient_profile"),
    path("orders/", views.patient_orders, name="patient_orders"),
    path("orders/<str:tracking_code>/", views.order_detail, name="order_detail"),
    
    # پنل مدیریت
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/intake/", views.staff_intake, name="staff_intake"),
    path("orders/<str:tracking_code>/results/", views.enter_results, name="enter_results"),
    path("orders/<str:tracking_code>/approve/", views.approve_order, name="approve_order"),
]
