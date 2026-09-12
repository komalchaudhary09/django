from django.contrib import admin
from .models import Student, Course, Enrollment, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "created_at", "student_count_display")
    search_fields = ("name", "code")
    ordering = ("code",)

    @admin.display(description="Students")
    def student_count_display(self, obj):
        return obj.students.filter(is_deleted=False).count()


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    fields = ('course', 'student', 'status', 'grade')
    autocomplete_fields = ()


@admin.action(description="Soft delete selected students")
def soft_delete_selected(modeladmin, request, queryset):
    updated = queryset.update(is_deleted=True)
    modeladmin.message_user(request, f"{updated} student(s) successfully marked as deleted (soft delete).")


@admin.action(description="Restore selected soft-deleted students")
def restore_selected(modeladmin, request, queryset):
    updated = queryset.update(is_deleted=False)
    modeladmin.message_user(request, f"{updated} student(s) successfully restored.")


@admin.action(description="Mark selected enrollments as Active")
def mark_active(modeladmin, request, queryset):
    updated = queryset.update(status='ACTIVE')
    modeladmin.message_user(request, f"{updated} enrollment(s) marked as Active.")


@admin.action(description="Mark selected enrollments as Completed")
def mark_completed(modeladmin, request, queryset):
    updated = queryset.update(status='COMPLETED')
    modeladmin.message_user(request, f"{updated} enrollment(s) marked as Completed.")


@admin.action(description="Mark selected enrollments as Dropped")
def mark_dropped(modeladmin, request, queryset):
    updated = queryset.update(status='DROPPED')
    modeladmin.message_user(request, f"{updated} enrollment(s) marked as Dropped.")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # Use all_objects to allow viewing/managing both active and soft-deleted students
    def get_queryset(self, request):
        return Student.all_objects.all()

    list_display = ("id", "name", "email", "age", "department", "joined_date", "is_deleted", "enrollment_count")
    search_fields = ("name", "email")
    list_filter = ("department", "is_deleted", "joined_date", "age")
    actions = [soft_delete_selected, restore_selected]
    inlines = [EnrollmentInline]
    ordering = ("-joined_date",)

    @admin.display(description="Enrollments")
    def enrollment_count(self, obj):
        return obj.enrollments.count()


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "duration", "student_count", "created_at")
    search_fields = ("code", "name", "description")
    list_filter = ("duration", "created_at")
    inlines = [EnrollmentInline]
    ordering = ("code",)

    @admin.display(description="Enrolled Students")
    def student_count(self, obj):
        return obj.student_count


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "status", "grade", "enrolled_at")
    search_fields = ("student__name", "student__email", "course__name", "course__code")
    list_filter = ("status", "course", "enrolled_at")
    actions = [mark_active, mark_completed, mark_dropped]
    ordering = ("-enrolled_at",)