from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.utils import timezone
from .models import Student, Course, Enrollment
from .forms import StudentForm, CourseForm, EnrollmentForm


def home(request):
    """Dashboard homepage showing summary statistics and recent records."""
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    recent_students = Student.objects.order_by('-joined_date')[:5]
    recent_courses = Course.objects.annotate(active_count=Count('enrollments')).order_by('-created_at')[:4]

    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'recent_students': recent_students,
        'recent_courses': recent_courses,
        'today': timezone.now(),
    }
    return render(request, 'students/home.html', context)


def about(request):
    """About project page."""
    context = {
        'project_name': 'Student Management System',
        'version': '2.0 (Full CRUD & Relationships)',
        'features': [
            'Django Model Architecture with 3 Interconnected Models',
            'Full CRUD (Create, Read, Update, Delete) Operations',
            'Django ModelForms with Custom Field Validations',
            'ForeignKey & Reverse ForeignKey Relationships',
            'Dynamic Search (?q=) & Multi-criteria Filtering',
            'Robust Pagination via Django Paginator',
            'Soft Delete Pattern with Manager & QuerySet Customizations',
            'Admin Panel with Inlines, Search, and Bulk Actions',
            'Responsive Bootstrap 5 UI with Alerts & Badges',
        ],
    }
    return render(request, 'students/about.html', context)


def contact(request):
    """Contact page."""
    context = {
        'email': 'support@studentacademy.example',
        'phone': '+1 (555) 019-2834',
        'address': '123 Education Plaza, Tech Hub, Suite 400',
        'office_hours': 'Monday – Friday: 9:00 AM – 5:00 PM (EST)',
    }
    return render(request, 'students/contact.html', context)


# ==========================================
# Student CRUD Views
# ==========================================

def student_list(request):
    """
    List students with:
    - Search (?q=)
    - Filtering by Course (?course=)
    - Filtering by Status (?status=active|deleted|all)
    - Sorting (?sort=name|date|age)
    - Pagination (Django Paginator)
    """
    search_query = request.GET.get('q', '').strip()
    course_filter = request.GET.get('course', '').strip()
    status_filter = request.GET.get('status', 'active').strip()
    sort_by = request.GET.get('sort', '-joined_date').strip()

    # 1. Base Queryset based on soft-delete status
    if status_filter == 'deleted':
        queryset = Student.all_objects.filter(is_deleted=True)
    elif status_filter == 'all':
        queryset = Student.all_objects.all()
    else:
        status_filter = 'active'
        queryset = Student.objects.all()

    # 2. Search filtering (?q=)
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(bio__icontains=search_query)
        )

    # 3. Course filtering (?course=)
    if course_filter:
        queryset = queryset.filter(enrollments__course_id=course_filter)

    # 4. Sorting
    valid_sorts = {
        'name': 'name',
        '-name': '-name',
        'age': 'age',
        '-age': '-age',
        'date': 'joined_date',
        '-date': '-joined_date',
        '-joined_date': '-joined_date',
    }
    order_field = valid_sorts.get(sort_by, '-joined_date')
    queryset = queryset.order_by(order_field).prefetch_related('enrollments__course').distinct()

    # 5. Pagination
    paginator = Paginator(queryset, 6)  # 6 students per page
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    courses = Course.objects.all()
    total_active = Student.objects.count()
    total_deleted = Student.all_objects.filter(is_deleted=True).count()

    context = {
        'students': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_course': course_filter,
        'selected_status': status_filter,
        'selected_sort': sort_by,
        'courses': courses,
        'total_active': total_active,
        'total_deleted': total_deleted,
        'total_matching': queryset.count(),
    }
    return render(request, 'students/student_list.html', context)


def student_detail(request, pk):
    """
    Read/Detail view: Displays student information along with all
    associated course enrollments via ForeignKey relationship.
    """
    student = get_object_or_404(Student.all_objects.prefetch_related('enrollments__course'), pk=pk)
    enrollments = student.enrollments.select_related('course').all()

    context = {
        'student': student,
        'enrollments': enrollments,
        'available_courses': Course.objects.exclude(enrollments__student=student),
    }
    return render(request, 'students/student_detail.html', context)


def student_create(request):
    """
    Create view: Handles GET (render empty ModelForm) and POST (validate & save).
    """
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student "{student.name}" has been successfully added!')
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, 'Please correct the errors in the form below.')
    else:
        form = StudentForm()

    context = {
        'form': form,
        'title': 'Add New Student',
        'button_text': 'Create Student',
    }
    return render(request, 'students/student_form.html', context)


def student_update(request, pk):
    """
    Update view: Pre-populates ModelForm with existing instance, validates and saves.
    """
    student = get_object_or_404(Student.all_objects, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student "{student.name}" details updated successfully!')
            return redirect('student_detail', pk=student.pk)
        else:
            messages.error(request, 'Please fix the errors below to update the student.')
    else:
        form = StudentForm(instance=student)

    context = {
        'form': form,
        'student': student,
        'title': f'Edit Student: {student.name}',
        'button_text': 'Update Student',
    }
    return render(request, 'students/student_form.html', context)


def student_delete(request, pk):
    """
    Delete view: Performs soft delete by default, setting is_deleted=True.
    """
    student = get_object_or_404(Student.all_objects, pk=pk)

    if request.method == 'POST':
        # Soft delete
        student.soft_delete()
        messages.warning(request, f'Student "{student.name}" was moved to trash (soft deleted).')
        return redirect('student_list')

    context = {
        'student': student,
    }
    return render(request, 'students/student_confirm_delete.html', context)


def student_restore(request, pk):
    """
    Restore view: Restores a soft-deleted student.
    """
    student = get_object_or_404(Student.all_objects, pk=pk)
    if request.method == 'POST':
        student.restore()
        messages.success(request, f'Student "{student.name}" was restored successfully!')
        return redirect('student_detail', pk=student.pk)

    return redirect('student_detail', pk=student.pk)


def student_hard_delete(request, pk):
    """
    Permanent deletion view: removes student record completely from database.
    """
    student = get_object_or_404(Student.all_objects, pk=pk)
    if request.method == 'POST':
        name = student.name
        student.delete()
        messages.error(request, f'Student "{name}" was permanently removed from database.')
        return redirect('student_list')

    return redirect('student_detail', pk=pk)


# ==========================================
# Course & Enrollment Views
# ==========================================

def course_list(request):
    """List all courses with enrolled student count and search."""
    search_query = request.GET.get('q', '').strip()
    courses = Course.objects.all().annotate(active_students=Count('enrollments', filter=Q(enrollments__student__is_deleted=False)))

    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'courses': courses,
        'search_query': search_query,
    }
    return render(request, 'students/course_list.html', context)


def course_detail(request, pk):
    """
    Reverse ForeignKey relationship view: Displays course info along with all
    enrolled students (Course → Students).
    """
    course = get_object_or_404(Course, pk=pk)
    enrollments = course.enrollments.select_related('student').filter(student__is_deleted=False)

    context = {
        'course': course,
        'enrollments': enrollments,
    }
    return render(request, 'students/course_detail.html', context)


def course_create(request):
    """Create a new course."""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course "{course.name}" created successfully!')
            return redirect('course_detail', pk=course.pk)
        else:
            messages.error(request, 'Please correct the errors in the course form.')
    else:
        form = CourseForm()

    context = {
        'form': form,
        'title': 'Add New Course',
        'button_text': 'Create Course',
    }
    return render(request, 'students/course_form.html', context)


def enrollment_create(request):
    """
    Enroll a student into a course. Pre-selects student if ?student=<id> is present.
    """
    initial_data = {}
    student_id = request.GET.get('student')
    if student_id:
        initial_data['student'] = student_id

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(
                request,
                f'Enrolled {enrollment.student.name} into {enrollment.course.name}!'
            )
            return redirect('student_detail', pk=enrollment.student.pk)
        else:
            messages.error(request, 'Please correct the enrollment errors below.')
    else:
        form = EnrollmentForm(initial=initial_data)

    context = {
        'form': form,
        'title': 'Enroll Student in Course',
        'button_text': 'Confirm Enrollment',
    }
    return render(request, 'students/enrollment_form.html', context)


def enrollment_delete(request, pk):
    """Remove/drop an enrollment."""
    enrollment = get_object_or_404(Enrollment, pk=pk)
    student_id = enrollment.student_id
    if request.method == 'POST':
        course_name = enrollment.course.name
        enrollment.delete()
        messages.info(request, f'Removed enrollment for {course_name}.')
    return redirect('student_detail', pk=student_id)


def custom_404(request, exception=None):
    """Custom 404 error page."""
    context = {
        'requested_path': request.path,
    }
    return render(request, 'students/404.html', context, status=404)
