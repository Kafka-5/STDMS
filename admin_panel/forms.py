from django import forms
from django.contrib.auth.models import User
from student.models import StudentProfile, Subject
from teacher.models import TeacherProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'branch', 'semester', 'phone']

class TeacherProfileForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = TeacherProfile
        fields = ['department', 'contact_number', 'subjects']

    def __init__(self, *args, **kwargs):
        super(TeacherProfileForm, self).__init__(*args, **kwargs)
        self.fields['department'].widget.attrs.update({'placeholder': 'Enter Department'})
        self.fields['contact_number'].widget.attrs.update({'placeholder': 'Enter Contact Number'})

    def save(self, commit=True):
        # Save the instance without committing it to the database yet
        instance = super(TeacherProfileForm, self).save(commit=False)
        
        if commit:
            instance.save()  # Save the instance

        # Save many-to-many fields (subjects)
        self.save_m2m()

        return instance

class StudentForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'branch', 'semester', 'phone', 'subjects']
