from django.db import models
from django.contrib.auth.models import User
from student.models import Subject, StudentProfile
import uuid
from django.utils import timezone

class TeacherProfile(models.Model):
    DEPARTMENT_CHOICES = [
        ('ECE', 'Electronics and Communication Engineering'),
        ('CSE', 'Computer Science and Engineering'),
        ('AI', 'Artificial Intelligence'),
        ('EEE', 'Electrical Engineering'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, related_name='teachers')

    def __str__(self):
        return self.user.username

class Assignment(models.Model):
    subject = models.ForeignKey('student.Subject', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()

    def __str__(self):
        return f"{self.subject.name} - {self.title}"

class Announcement(models.Model):
    subject = models.ForeignKey('student.Subject', on_delete=models.CASCADE, related_name='announcements')
    message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Announcement for {self.subject.name} on {self.date_posted}"

    class Meta:
        verbose_name_plural = "Announcements"

class AttendanceToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    subject = models.ForeignKey('student.Subject', on_delete=models.CASCADE)
    teacher = models.ForeignKey('TeacherProfile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    used_by = models.ManyToManyField(StudentProfile, blank=True)
    processed = models.BooleanField(default=False)  # New field to track if absent marking is done

    def __str__(self):
        return f"{self.teacher.user.username} - {self.subject.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"