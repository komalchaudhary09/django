from django.db import models
from django.utils import timezone


class StudentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class StudentManager(models.Manager):
    def get_queryset(self):
        # By default, only return active (non-deleted) students
        return StudentQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self):
        return StudentQuerySet(self.model, using=self._db)

    def deleted_only(self):
        return StudentQuerySet(self.model, using=self._db).filter(is_deleted=True)


class Course(models.Model):
    code = models.CharField(max_length=20, default="CRS101", help_text="e.g. CS101, PY202")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in weeks", default=4)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['code', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def student_count(self):
        return self.enrollments.filter(student__is_deleted=False).count()


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField()
    bio = models.TextField(blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(
        default=False,
        help_text="Designates whether this student is soft-deleted."
    )

    # Managers
    objects = StudentManager()           # Default manager filters out soft-deleted
    all_objects = models.Manager()       # Returns all students including soft-deleted

    class Meta:
        ordering = ['-joined_date']

    def __str__(self):
        return self.name

    def soft_delete(self):
        """Soft delete student by setting is_deleted=True."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

    def restore(self):
        """Restore soft-deleted student."""
        self.is_deleted = False
        self.save(update_fields=['is_deleted'])

    @property
    def active_courses(self):
        """Return courses student is actively enrolled in."""
        return [
            enrollment.course
            for enrollment in self.enrollments.select_related('course').filter(status='ACTIVE')
        ]


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DROPPED', 'Dropped'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    grade = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        help_text="Optional grade (e.g., A+, B, Pass)"
    )

    class Meta:
        ordering = ['-enrolled_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'],
                name='unique_student_course_enrollment'
            )
        ]

    def __str__(self):
        return f"{self.student.name} → {self.course.name} ({self.get_status_display()})"