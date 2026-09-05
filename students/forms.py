from django import forms
from .models import Student, Course, Enrollment


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'age', 'bio']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name (e.g., John Doe)',
                'autofocus': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age (between 16 and 100)',
                'min': '16',
                'max': '100',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Brief background or bio (optional)...',
                'rows': 4,
            }),
        }
        labels = {
            'name': 'Student Name',
            'email': 'Email Address',
            'age': 'Age (Years)',
            'bio': 'Biography',
        }
        help_texts = {
            'email': 'We will never share your email with anyone else.',
            'age': 'Students must be at least 16 years old.',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        if any(char.isdigit() for char in name):
            raise forms.ValidationError("Name should not contain numbers.")
        return name

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None:
            if age < 16:
                raise forms.ValidationError("Student must be at least 16 years old.")
            if age > 100:
                raise forms.ValidationError("Please enter a valid age under 100.")
        return age

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        # Check uniqueness excluding current instance if updating
        existing = Student.all_objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError(f"A student with email '{email}' already exists.")
        return email


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'duration']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS101'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python Programming'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Course overview...'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weeks'}),
        }
        labels = {
            'code': 'Course Code',
            'name': 'Course Name',
            'description': 'Description',
            'duration': 'Duration (Weeks)',
        }

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        if len(code) < 3:
            raise forms.ValidationError("Course code must be at least 3 characters.")
        existing = Course.objects.filter(code__iexact=code)
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError(f"Course code '{code}' is already in use.")
        return code


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'status', 'grade']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A, B+, Pass (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active students in the dropdown
        self.fields['student'].queryset = Student.objects.filter(is_deleted=False)

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        course = cleaned_data.get('course')

        if student and course:
            existing = Enrollment.objects.filter(student=student, course=course)
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(f"{student.name} is already enrolled in {course.name}.")

        return cleaned_data
