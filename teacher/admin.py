from django.contrib import admin
from .models import TeacherProfile, Assignment, Announcement

admin.site.register(TeacherProfile)
admin.site.register(Assignment)
admin.site.register(Announcement)
