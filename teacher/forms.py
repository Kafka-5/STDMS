from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['subject', 'title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            # Limit subject choices to teacher's assigned subjects
            self.fields['subject'].queryset = teacher.subjects.all()



# Marks 
from student.models import Marks, StudentProfile

class MarksForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=StudentProfile.objects.none())

    class Meta:
        model = Marks
        fields = ['student', 'assessment_name', 'marks_obtained', 'total_marks', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, subject=None, **kwargs):
        super().__init__(*args, **kwargs)
        if subject:
            # Limit students to those enrolled in the subject
            self.fields['student'].queryset = StudentProfile.objects.filter(subjects=subject)
#---- Announcement ---
from django import forms
from .models import Announcement

from django import forms
from .models import Announcement

from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['subject'].queryset = teacher.subjects.all()