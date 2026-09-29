from django.urls import path
from . import views
app_name = "lab"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("intake/", views.intake, name="intake"),
    path("orders/<str:tracking_code>/", views.order_detail, name="order_detail"),
    path("orders/<str:tracking_code>/results/", views.enter_results, name="enter_results"),
    path("orders/<str:tracking_code>/approve/", views.approve_order, name="approve_order"),
]
