"""Hornet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lessons import views

from lessons.views import UserListView, EditRequestView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('feed/', views.feed, name='feed'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('account_info/',views.account_info, name='account_info'),
    path('make_request/', views.make_request, name='make_request'),
    path('pending_requests/',views.pending_requests, name='pending_requests'),
    path('booked_lessons/',views.booked_lessons, name='booked_lessons'),
    path('show_all_requests/',views.show_all_requests, name='show_all_requests'),
    path('submit_payment/', views.submit_payment, name="submit_payment"),
    path('edit_request/<int:request_id>', EditRequestView.as_view(), name="edit_request"),
    path('invoices/', views.invoices, name="invoices"),
    path('make_admin/', views.make_admin, name="make_admin"),
    path('show_all_admins/', views.show_all_admins, name="show_all_admins"),
    path('edit_admin/<int:user_id>', views.edit_admin, name="edit_admin"),
    path('delete_user/<int:user_id>', views.delete_user, name="delete_user"),
    path('payment_history/', views.payment_history, name="payment_history"),
    path('delete_request/<int:request_id>', views.delete_request, name="delete_request"),
    path('user_list/', UserListView.as_view(), name="user_list"),
    path('user_payment_history/<int:user_id>', views.user_payment_history, name="user_payment_history")
]
