from django.db import models
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class StudentProfile(models.Model):
    DEPARTMENT_CHOICES = [
        ('ECE', 'Electronics and Communication Engineering'),
        ('CSE', 'Computer Science and Engineering'),
        ('AI', 'Artificial Intelligence'),
        ('EEE', 'Electrical Engineering'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    semester = models.IntegerField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subjects = models.ManyToManyField('Subject', blank=True)

    def save(self, *args, **kwargs):
        # Save the instance first to ensure it exists in the database
        super().save(*args, **kwargs)
        
        # Log the student details
        logger.info(f"Saving StudentProfile: user={self.user.username}, branch={self.branch}, semester={self.semester}")
        
        # Assign subjects that match branch and semester and have a teacher
        subjects_to_add = Subject.objects.filter(
            department=self.branch,
            semester=self.semester,
            teacher__isnull=False
        )
        
        # Log the subjects found
        if subjects_to_add.exists():
            logger.info(f"Found {subjects_to_add.count()} subjects for {self.branch}, semester {self.semester}: {list(subjects_to_add.values('name', 'code'))}")
        else:
            logger.warning(f"No subjects found for {self.branch}, semester {self.semester} with assigned teachers")
        
        # Update the subjects ManyToManyField
        self.subjects.set(subjects_to_add)
        
        # No need to call super().save again

    def __str__(self):
        return f"{self.user.username} - {self.roll_number}"

class Marks(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    assessment_name = models.CharField(max_length=100)
    marks_obtained = models.FloatField()
    total_marks = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} - {self.assessment_name}"

class Attendance(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'subject', 'date')

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} - {self.date} - {'Present' if self.present else 'Absent'}"

class Subject(models.Model):
    DEPARTMENT_CHOICES = [
        ('ECE', 'Electronics and Communication Engineering'),
        ('CSE', 'Computer Science and Engineering'),
        ('AI', 'Artifical Intelligence'),
        ('EEE', 'ELectrical Engineering'),
    ]
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    semester = models.IntegerField()
    teacher = models.ForeignKey(
        'teacher.TeacherProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.teacher:
            logger.warning(f"Subject {self.name} (Code: {self.code}) has no teacher assigned.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"