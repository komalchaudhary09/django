from django.test import TestCase, Client
from django.urls import reverse
from .models import Student, Course, Enrollment
from .forms import StudentForm, CourseForm, EnrollmentForm


class ModelTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            code="CS101",
            name="Computer Science 101",
            duration=10,
            description="Basics of Computer Science"
        )
        self.student = Student.objects.create(
            name="John Doe",
            email="john@example.com",
            age=22,
            bio="Test student bio"
        )

    def test_course_creation_and_str(self):
        self.assertEqual(str(self.course), "CS101 - Computer Science 101")
        self.assertEqual(self.course.student_count, 0)

    def test_student_creation_and_str(self):
        self.assertEqual(str(self.student), "John Doe")
        self.assertFalse(self.student.is_deleted)
        self.assertIn(self.student, Student.objects.all())

    def test_enrollment_creation_and_str(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            status="ACTIVE",
            grade="A"
        )
        self.assertEqual(str(enrollment), "John Doe → Computer Science 101 (Active)")
        self.assertEqual(self.course.student_count, 1)
        self.assertEqual(len(self.student.active_courses), 1)
        self.assertEqual(self.student.active_courses[0], self.course)

    def test_soft_delete_and_restore(self):
        # Soft delete
        self.student.soft_delete()
        self.assertTrue(self.student.is_deleted)
        # Should NOT appear in default manager
        self.assertNotIn(self.student, Student.objects.all())
        # Should appear in all_objects and deleted_only
        self.assertIn(self.student, Student.all_objects.all())
        self.assertIn(self.student, Student.objects.deleted_only())

        # Restore
        self.student.restore()
        self.assertFalse(self.student.is_deleted)
        self.assertIn(self.student, Student.objects.all())


class FormTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Existing Student",
            email="existing@example.com",
            age=20
        )
        self.course = Course.objects.create(
            code="PY101",
            name="Python Basics",
            duration=4
        )

    def test_student_form_valid(self):
        form = StudentForm(data={
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'age': 25,
            'bio': 'Learning web dev'
        })
        self.assertTrue(form.is_valid())

    def test_student_form_age_validation(self):
        form = StudentForm(data={
            'name': 'Young Student',
            'email': 'young@example.com',
            'age': 12, # below min 16
        })
        self.assertFalse(form.is_valid())
        self.assertIn('age', form.errors)

    def test_student_form_duplicate_email(self):
        form = StudentForm(data={
            'name': 'Duplicate Email',
            'email': 'existing@example.com',
            'age': 22,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_enrollment_form_prevent_duplicate(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        form = EnrollmentForm(data={
            'student': self.student.id,
            'course': self.course.id,
            'status': 'ACTIVE'
        })
        self.assertFalse(form.is_valid())


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.course1 = Course.objects.create(code="CS101", name="CS Basics", duration=8)
        self.course2 = Course.objects.create(code="PY201", name="Python Basics", duration=6)
        self.student1 = Student.objects.create(name="Alice", email="alice@test.com", age=20)
        self.student2 = Student.objects.create(name="Bob", email="bob@test.com", age=25)
        self.student_deleted = Student.all_objects.create(
            name="Charlie (Deleted)",
            email="charlie@test.com",
            age=30,
            is_deleted=True
        )
        Enrollment.objects.create(student=self.student1, course=self.course1, status="ACTIVE")

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Academy Dashboard")
        self.assertContains(response, "Alice")

    def test_student_list_view(self):
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertContains(response, "Bob")
        # Soft-deleted student should not show by default
        self.assertNotContains(response, "Charlie (Deleted)")

    def test_student_search(self):
        response = self.client.get(reverse('student_list') + '?q=Alice')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertNotContains(response, "Bob")

    def test_student_course_filter(self):
        response = self.client.get(reverse('student_list') + f'?course={self.course1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertNotContains(response, "Bob")

    def test_student_status_filter_deleted(self):
        response = self.client.get(reverse('student_list') + '?status=deleted')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Charlie (Deleted)")
        self.assertNotContains(response, "Alice")

    def test_student_detail_view(self):
        response = self.client.get(reverse('student_detail', kwargs={'pk': self.student1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
        self.assertContains(response, "CS101")

    def test_student_create_post(self):
        response = self.client.post(reverse('student_create'), {
            'name': 'David Clark',
            'email': 'david.clark@test.com',
            'age': 23,
            'bio': 'New bio'
        })
        self.assertEqual(response.status_code, 302)
        new_student = Student.objects.get(email='david.clark@test.com')
        self.assertEqual(new_student.name, 'David Clark')

    def test_student_update_post(self):
        response = self.client.post(reverse('student_update', kwargs={'pk': self.student1.pk}), {
            'name': 'Alice Updated',
            'email': 'alice@test.com',
            'age': 21,
            'bio': 'Updated bio'
        })
        self.assertEqual(response.status_code, 302)
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.name, 'Alice Updated')
        self.assertEqual(self.student1.age, 21)

    def test_student_soft_delete_post(self):
        response = self.client.post(reverse('student_delete', kwargs={'pk': self.student1.pk}))
        self.assertEqual(response.status_code, 302)
        self.student1.refresh_from_db()
        self.assertTrue(self.student1.is_deleted)

    def test_student_restore_post(self):
        response = self.client.post(reverse('student_restore', kwargs={'pk': self.student_deleted.pk}))
        self.assertEqual(response.status_code, 302)
        self.student_deleted.refresh_from_db()
        self.assertFalse(self.student_deleted.is_deleted)

    def test_course_views(self):
        # List
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS Basics")

        # Detail with reverse relationship
        response = self.client.get(reverse('course_detail', kwargs={'pk': self.course1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")
