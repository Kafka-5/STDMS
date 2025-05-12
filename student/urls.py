from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.student_login, name='student_login'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.student_logout, name='student_logout'),
    path('mark_attendance/<str:token>/', views.mark_attendance, name='mark_attendance'),
    path('view_attendance/', views.student_attendance, name='view_attendance'),
    path('attendance/dashboard/', views.attendance_dashboard, name='attendance_dashboard'),
    path('subjects/', views.view_subjects, name='view_subjects'),
    path('marks/', views.view_marks, name='view_marks'),
    path('announcements/', views.view_announcements, name='view_announcements'),
    path('reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('contact/', views.contact_us, name='contact_us'),

]