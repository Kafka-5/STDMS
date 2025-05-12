from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from stdms.decorators import student_required
from teacher.models import AttendanceToken, Assignment, Announcement
from django.utils import timezone
from .models import StudentProfile, Attendance, Marks, Subject
from collections import defaultdict
from django.db.models import Count, Q
from django.db import IntegrityError
import math
from math import radians, sin, cos, sqrt, atan2
import logging

from django.shortcuts import render
logger = logging.getLogger(__name__)

def student_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'student/student_login.html')

def student_logout(request):
    logout(request)
    return redirect('student_login')

@login_required
def student_dashboard(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return redirect('student_login')
    
    subjects = profile.subjects.all().select_related('teacher')
    attendance_data = Attendance.objects.filter(student=profile)
    marks_data = Marks.objects.filter(student=profile)
    announcements = Announcement.objects.filter(subject__in=subjects).order_by('-date_posted')
    assignments = Assignment.objects.filter(subject__in=subjects)
    
    context = {
        'profile': profile,
        'subjects': subjects,
        'attendance_data': attendance_data,
        'marks_data': marks_data,
        'announcements': announcements,
        'assignments': assignments,
    }
    return render(request, 'student/student_dashboard.html', context)

@login_required
@student_required
def view_subjects(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        return redirect('student_login')
    
    subjects = profile.subjects.all().select_related('teacher')
    return render(request, 'student/view_subjects.html', {'subjects': subjects})

@login_required
@student_required
def view_marks(request):
    student = StudentProfile.objects.get(user=request.user)
    marks_data = Marks.objects.filter(student=student).order_by('-date')
    
    marks_with_percentage = [
        {
            'subject': mark.subject,
            'assessment_name': mark.assessment_name,
            'marks_obtained': mark.marks_obtained,
            'total_marks': mark.total_marks,
            'percentage': (mark.marks_obtained / mark.total_marks * 100) if mark.total_marks > 0 else 0,
            'date': mark.date,
        }
        for mark in marks_data
    ]
    return render(request, 'student/view_marks.html', {
        'marks_data': marks_with_percentage,
    })

@login_required
@student_required
def view_announcements(request):
    student = StudentProfile.objects.get(user=request.user)
    announcements = Announcement.objects.filter(subject__in=student.subjects.all()).order_by('-date_posted')
    return render(request, 'student/view_announcements.html', {
        'announcements': announcements,
    })

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance

@login_required
def mark_attendance(request, token):
    logger.info(f"Mark attendance called with token: {token}")
    try:
        token_obj = AttendanceToken.objects.get(token=token)
        logger.info(f"Token found: {token_obj.token}, created at {token_obj.created_at}")

        try:
            student = StudentProfile.objects.get(user=request.user)
            logger.info(f"Student: {student.user.username}")
        except StudentProfile.DoesNotExist:
            logger.error(f"Student profile not found for user {request.user.username}")
            return render(request, 'student/attendance_failed.html', {'message': 'Student profile not found.'})

        subject = token_obj.subject
        today = timezone.now().date()

        # Check student enrollment
        if subject not in student.subjects.all():
            logger.error(f"Student {student.user.username} not enrolled in subject {subject.name}")
            return render(request, 'student/attendance_failed.html', {
                'message': f'You are not enrolled in {subject.name}.'
            })

        # Check if attendance is already marked
        already_marked = Attendance.objects.filter(
            student=student,
            subject=subject,
            date=today
        ).exists()
        if already_marked:
            logger.info(f"Attendance already marked for {student.user.username} in {subject.name}")
            return render(request, 'student/attendance_failed.html', {
                'message': 'Attendance already marked for today.'
            })

        if request.method == 'GET':
            logger.info("Rendering mark_attendance.html")
            return render(request, 'student/mark_attendance.html', {'subject': subject})

        elif request.method == 'POST':
            # Check QR code expiration 
            expiration_time = token_obj.created_at + timezone.timedelta(minutes=7)  # Extended to 7 minutes
            if timezone.now() > expiration_time:
                logger.info(f"QR code expired for token {token}, marking absent")
                Attendance.objects.get_or_create(
                    student=student,
                    subject=subject,
                    date=today,
                    defaults={'present': False}
                )
                return render(request, 'student/attendance_failed.html', {
                    'message': 'QR code expired. You have been marked absent.'
                })

            lat = request.POST.get('latitude')
            lon = request.POST.get('longitude')
            logger.info(f"Student location: lat={lat}, lon={lon}")

            if not lat or not lon:
                logger.error("Location not provided")
                return render(request, 'student/attendance_failed.html', {
                    'message': 'Location not provided. Please enable location services.'
                })

            try:
                student_lat = float(lat)
                student_lon = float(lon)
            except ValueError:
                logger.error(f"Invalid location format: lat={lat}, lon={lon}")
                return render(request, 'student/attendance_failed.html', {
                    'message': 'Invalid location data.'
                })

            if token_obj.latitude is None or token_obj.longitude is None:
                logger.error("QR location not available")
                return render(request, 'student/attendance_failed.html', {
                    'message': 'QR code location not available.'
                })

            distance = haversine(student_lat, student_lon, token_obj.latitude, token_obj.longitude)
            logger.info(f"Distance calculated: {distance:.2f} meters")
            max_distance = 200  # Corrected to 200 meters
            if distance > max_distance:
                logger.error(f"Distance too far: {distance:.2f} meters")
                return render(request, 'student/attendance_failed.html', {
                    'message': f'You must be within {max_distance} meters of the QR point. You are {int(distance)} meters away.'
                })

            try:
                attendance = Attendance.objects.create(
                    student=student,
                    subject=subject,
                    date=today,
                    present=True
                )
                token_obj.used_by.add(student)
                logger.info(f"Attendance marked successfully for {student.user.username} in {subject.name}")
                return render(request, 'student/attendance_success.html', {'subject': subject})
            except IntegrityError as e:
                logger.error(f"Database integrity error: {str(e)}")
                return render(request, 'student/attendance_failed.html', {
                    'message': 'Attendance could not be marked due to a database conflict.'
                })
            except Exception as e:
                logger.error(f"Failed to create attendance: {str(e)}")
                return render(request, 'student/attendance_failed.html', {
                    'message': 'Failed to mark attendance due to a server error.'
                })

    except AttendanceToken.DoesNotExist:
        logger.error(f"Invalid QR code: {token}")
        return render(request, 'student/attendance_failed.html', {'message': 'Invalid QR code.'})

@login_required
@student_required
def student_attendance(request):
    student = StudentProfile.objects.get(user=request.user)
    attendance_data = Attendance.objects.filter(student=student)
    summary = defaultdict(lambda: {'present': 0, 'total': 0})
    for record in attendance_data:
        summary[record.subject.name]['total'] += 1
        if record.present:
            summary[record.subject.name]['present'] += 1
    for subject in summary:
        p = summary[subject]['present']
        t = summary[subject]['total']
        summary[subject]['percentage'] = round((p / t) * 100, 2) if t else 0
    return render(request, 'student/view_attendance.html', {'summary': summary})

@login_required
def attendance_dashboard(request):
    student = StudentProfile.objects.get(user=request.user)
    subjects = student.subjects.all()
    labels = []
    percentages = []
    attendance_data = []
    for subject in subjects:
        total_classes = Attendance.objects.filter(subject=subject).count()
        present = Attendance.objects.filter(subject=subject, student=student, present=True).count()
        percentage = (present / total_classes) * 100 if total_classes > 0 else 0
        labels.append(subject.name)
        percentages.append(round(percentage, 2))
        attendance_data.append({
            'subject': subject.name,
            'total': total_classes,
            'present': present,
            'percentage': round(percentage, 2)
        })
    if not attendance_data:
        return render(request, 'student/view_attendance.html', {
            'message': 'No attendance data found for the subjects.'
        })
    return render(request, 'student/view_attendance.html', {
        'labels': labels,
        'percentages': percentages,
        'attendance_data': attendance_data
    })
from django.shortcuts import render

def contact_us(request):
    return render(request, 'contact.html')
