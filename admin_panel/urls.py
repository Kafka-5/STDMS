from django.urls import path
from . import views

urlpatterns = [
    # Admin Panel URLs
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Manage Students & Teachers
    path('manage_students/', views.manage_students, name='manage_students'),
    path('manage_teachers/', views.manage_teachers, name='manage_teachers'),

    # Add and Edit Student & Teacher URLs
    path('add-student/', views.add_student, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),  # Edit student
    path('add-teacher/', views.add_teacher, name='add_teacher'),  # Add teacher
    path('edit-teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),  # Edit teacher

    path('delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('delete_teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),

    # csv 
    path('upload-csv-center/', views.upload_csv_center, name='upload_csv_center'),



]
