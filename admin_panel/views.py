import io
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from student.models import StudentProfile, Subject, Marks
from teacher.models import TeacherProfile
from .forms import UserForm, StudentProfileForm, TeacherProfileForm
from .forms import StudentForm
from django.contrib.auth.models import User
from io import TextIOWrapper
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages


from datetime import datetime

# Helper function to check if user is admin/staff
def is_admin(user):
    return user.is_authenticated and user.is_staff

# ---------------------- LOGIN ----------------------
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin.')
    return render(request, 'admin_panel/admin_login.html')

# ---------------------- LOGOUT ----------------------
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

# ---------------------- DASHBOARD ----------------------
@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard(request):
    total_students = StudentProfile.objects.count()
    total_teachers = TeacherProfile.objects.count()

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
    }
    return render(request, 'admin_panel/admin_dashboard.html', context)

# ---------------------- MANAGE STUDENTS ----------------------
@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def manage_students(request):
    students = StudentProfile.objects.select_related('user').all()
    return render(request, 'admin_panel/manage_students.html', {'students': students})

# ---------------------- MANAGE TEACHERS ----------------------
@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def manage_teachers(request):
    teachers = TeacherProfile.objects.select_related('user').all()
    return render(request, 'admin_panel/manage_teachers.html', {'teachers': teachers})

# ---------------------- ADD STUDENT ----------------------
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def add_student(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        student_form = StudentProfileForm(request.POST)
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            messages.success(request, "Student created successfully.")
            return redirect('manage_students')
    else:
        user_form = UserForm()
        student_form = StudentProfileForm()
    return render(request, 'admin_panel/add_student.html', {'user_form': user_form, 'student_form': student_form})

# ---------------------- ADD TEACHER ----------------------
@login_required(login_url='admin_login')
@user_passes_test(is_admin)






# Correct import from the admin_panel/forms.py file



def add_teacher(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        teacher_form = TeacherProfileForm(request.POST)

        if user_form.is_valid() and teacher_form.is_valid():
            # Save the user object (User)
            user = user_form.save(commit=False)
            user.set_password(user.password)  # Hash the password
            user.is_staff = True  # Mark user as staff (indicating teacher)
            user.save()  # Save the user to create a User instance

            # Now that the user is saved, get the teacher profile
            teacher = teacher_form.save(commit=False)
            teacher.user = user  # Link teacher profile with the created user
            teacher.save()  # Save the teacher profile to the database

            # Save many-to-many relationships (subjects)
            teacher_form.save_m2m()  # This saves any many-to-many fields (subjects)

            messages.success(request, "Teacher created successfully.")
            return redirect('manage_teachers')  # Redirect to manage_teachers page
        else:
            messages.error(request, "There was an error with the form. Please try again.")
    else:
        user_form = UserForm()
        teacher_form = TeacherProfileForm()

    return render(request, 'admin_panel/add_teacher.html', {'user_form': user_form, 'teacher_form': teacher_form})



# ---------------------- EDIT STUDENT ----------------------
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def edit_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student details updated successfully.")
            return redirect('manage_students')  # Redirect back to the students list
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'admin_panel/edit_student.html', {'form': form, 'student': student})

# ---------------------- EDIT TEACHER ----------------------
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    
    if request.method == 'POST':
        # Use TeacherProfileForm instead of TeacherForm to include subjects
        form = TeacherProfileForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save(commit=True)  # Save the teacher profile
            form.save_m2m()  # Save the subjects (Many-to-Many relationship)
            messages.success(request, "Teacher details updated successfully.")
            return redirect('manage_teachers')  # Redirect back to the teachers list
    else:
        form = TeacherProfileForm(instance=teacher)
    
    return render(request, 'admin_panel/edit_teacher.html', {'form': form, 'teacher': teacher})

# ---------------------- DELETE TEACHER ----------------------
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    teacher.delete()
    messages.success(request, "Teacher deleted successfully.")
    return redirect('manage_teachers')

# ---------------------- DELETE STUDENT ----------------------
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def delete_student(request, student_id):
    student = get_object_or_404(StudentProfile, id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully.")
    return redirect('manage_students')

# ---------------------- CSV UPLOAD VIEW ----------------------



@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def upload_csv_center(request):
    if request.method == 'POST':
        upload_type = request.POST.get('upload_type')
        csv_file = request.FILES.get('csv_file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Invalid file format.')
            return redirect('upload_csv_center')

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        try:
            if upload_type == 'student':
                for row in reader:
                    
                    password = 'student@123'

                    # Create user for student
                    user = User.objects.create_user(
                        username=row['username'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        email=row['email'],
                        password=password
                    )

                    # Create student profile
                    StudentProfile.objects.create(
                        user=user,
                        roll_number=row['roll_number'],
                        branch=row['branch'],
                        semester=int(row['semester']),
                        phone=row['phone']
                    )

                messages.success(request, "Students uploaded successfully.")
            
            elif upload_type == 'teacher':
                for row in reader:
                    # Hash password for teacher
                    password = 'teacher@123'

                    # Create user for teacher
                    user = User.objects.create_user(
                        username=row['username'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        email=row['email'],
                        password=password
                    )
                    user.is_staff = True  # Mark as teacher (staff)
                    user.save()

                    # Create teacher profile
                    TeacherProfile.objects.create(
                        user=user,
                        department=row['department'],
                        contact_number=row['contact_number']
                    )

                messages.success(request, "Teachers uploaded successfully.")
            
            elif upload_type == 'marks':
                for row in reader:
                    try:
                        student = StudentProfile.objects.get(roll_number=row['student_roll_number'])
                        subject = Subject.objects.get(code=row['subject_code'])

                        if not Marks.objects.filter(student=student, subject=subject, assessment_name=row['assessment_name']).exists():
                            Marks.objects.create(
                                student=student,
                                subject=subject,
                                assessment_name=row['assessment_name'],
                                marks_obtained=float(row['marks_obtained']),
                                total_marks=float(row['total_marks']),
                                date=datetime.strptime(row['date'], '%Y-%m-%d').date()
                            )
                    except StudentProfile.DoesNotExist:
                        messages.error(request, f"Student with roll number {row['student_roll_number']} does not exist.")
                        continue
                    except Subject.DoesNotExist:
                        messages.error(request, f"Subject with code {row['subject_code']} does not exist.")
                        continue
                    except Exception as e:
                        messages.error(request, f"Error processing marks: {str(e)}")
                        continue

                messages.success(request, "Marks uploaded successfully.")
            
            else:
                messages.error(request, "Invalid upload type selected.")

        except Exception as e:
            messages.error(request, f"Error during upload: {str(e)}")

        return redirect('upload_csv_center')

    return render(request, 'admin_panel/upload_csv_center.html')



