from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_view, name='upload'),
    path('profile/', views.profile_view, name='my_profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),

    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('follow/<int:user_id>/', views.toggle_follow, name='toggle_follow'),
    path('report/<int:post_id>/', views.report_post, name='report_post'),
    path('confirm-age/', views.confirm_age, name='confirm_age'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
