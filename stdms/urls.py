from django.contrib import admin
from django.urls import path,include
from student.views import mark_attendance,contact_us


urlpatterns = [
    path('',include('home.urls')),
    path('admin/', admin.site.urls),
    path('admin_panel/', include('admin_panel.urls')),
    path('student/',include('student.urls')),
    path('teacher/',include('teacher.urls')),
    path('mark_attendance/<str:token>/', mark_attendance, name='mark_attendance'),
    
    
]
