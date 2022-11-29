from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout, name="logout"),

    path('', views.home, name="home"),
    path('add/new/url/', views.add_new_url, name="add_new_url"),
    path('edit/url/<int:url_id>/', views.edit_url, name="edit_url"),
    path('delete/url/<int:url_id>/', views.delete_url, name="delete_url"),
    path('monitor/url/<int:url_id>/', views.monitor_url, name="monitor_url"),
]
