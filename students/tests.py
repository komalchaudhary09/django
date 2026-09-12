from django.test import TestCase, Client
from django.urls import reverse
from .models import Student, Course, Enrollment, Department
from .forms import StudentForm, CourseForm, EnrollmentForm, DepartmentForm
from .orm_practice import run_all_orm_exercises


class ModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            code="CS",
            name="Computer Science",
            description="Software and Computing"
        )
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
            department=self.department,
            bio="Test student bio"
        )

    def test_department_creation_and_str(self):
        self.assertEqual(str(self.department), "Computer Science (CS)")
        self.assertEqual(self.department.student_count, 1)

    def test_course_creation_and_str(self):
        self.assertEqual(str(self.course), "CS101 - Computer Science 101")
        self.assertEqual(self.course.student_count, 0)

    def test_student_creation_and_relationships(self):
        self.assertEqual(str(self.student), "John Doe")
        self.assertFalse(self.student.is_deleted)
        self.assertIn(self.student, Student.objects.all())
        # Forward lookup: student -> department
        self.assertEqual(self.student.department.code, "CS")
        # Reverse lookup: department -> students
        self.assertIn(self.student, self.department.students.all())

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
        self.dept = Department.objects.create(code="EE", name="Electrical Eng")
        self.student = Student.objects.create(
            name="Existing Student",
            email="existing@example.com",
            age=20,
            department=self.dept
        )
        self.course = Course.objects.create(
            code="PY101",
            name="Python Basics",
            duration=4
        )

    def test_department_form_valid(self):
        form = DepartmentForm(data={
            'code': 'BA',
            'name': 'Business Administration',
            'description': 'Business School'
        })
        self.assertTrue(form.is_valid())

    def test_department_form_duplicate_code(self):
        form = DepartmentForm(data={
            'code': 'EE',
            'name': 'Duplicate EE',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)

    def test_student_form_valid(self):
        form = StudentForm(data={
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'age': 25,
            'department': self.dept.id,
            'bio': 'Learning web dev'
        })
        self.assertTrue(form.is_valid())

    def test_student_form_age_validation(self):
        form = StudentForm(data={
            'name': 'Young Student',
            'email': 'young@example.com',
            'age': 12,  # below min 16
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
        self.dept_cs = Department.objects.create(code="CS", name="Computer Science")
        self.dept_ee = Department.objects.create(code="EE", name="Electrical Eng")
        self.course1 = Course.objects.create(code="CS101", name="CS Basics", duration=8)
        self.course2 = Course.objects.create(code="PY201", name="Python Basics", duration=6)

        # Create 7 students to test 5-per-page pagination
        for i in range(1, 8):
            Student.objects.create(
                name=f"Student {i}",
                email=f"student{i}@test.com",
                age=18 + i,
                department=self.dept_cs if i <= 4 else self.dept_ee
            )

        self.student_deleted = Student.all_objects.create(
            name="Charlie (Deleted)",
            email="charlie@test.com",
            age=30,
            department=self.dept_cs,
            is_deleted=True
        )
        Enrollment.objects.create(student=Student.objects.first(), course=self.course1, status="ACTIVE")

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Academy Dashboard")
        self.assertContains(response, "Computer Science")

    def test_student_list_pagination_five_per_page(self):
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        # Should contain 5 students on page 1
        self.assertEqual(len(response.context['students']), 5)
        self.assertTrue(response.context['page_obj'].has_next())

    def test_student_search_and_filters(self):
        # Search by name
        response = self.client.get(reverse('student_list') + '?q=Student 1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student 1")

        # Filter by department
        response = self.client.get(reverse('student_list') + f'?department={self.dept_ee.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_matching'], 3)

        # Filter by age range
        response = self.client.get(reverse('student_list') + '?min_age=20&max_age=23')
        self.assertEqual(response.status_code, 200)
        for s in response.context['students']:
            self.assertTrue(20 <= s.age <= 23)

    def test_department_crud_views(self):
        # List
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Computer Science")

        # Detail
        response = self.client.get(reverse('department_detail', kwargs={'pk': self.dept_cs.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Computer Science")
        self.assertContains(response, "Student 1")

        # Create
        response = self.client.post(reverse('department_create'), {
            'code': 'MATH',
            'name': 'Mathematics',
            'description': 'Math Dept'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Department.objects.filter(code='MATH').exists())

        # Update
        response = self.client.post(reverse('department_update', kwargs={'pk': self.dept_cs.pk}), {
            'code': 'CS',
            'name': 'Computer Science & AI',
            'description': 'Updated'
        })
        self.assertEqual(response.status_code, 302)
        self.dept_cs.refresh_from_db()
        self.assertEqual(self.dept_cs.name, 'Computer Science & AI')

        # Delete
        dept_to_del = Department.objects.create(code='TEMP', name='Temporary')
        response = self.client.post(reverse('department_delete', kwargs={'pk': dept_to_del.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Department.objects.filter(code='TEMP').exists())

    def test_orm_lab_view(self):
        response = self.client.get(reverse('orm_lab'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django ORM Practice &amp; Query Laboratory")
        self.assertIn('sections', response.context)
        self.assertEqual(len(response.context['sections']), 11)


class ORMExerciseFunctionTests(TestCase):
    def setUp(self):
        dept = Department.objects.create(code="CS", name="Computer Science")
        Student.objects.create(name="Alice", email="alice@test.com", age=21, department=dept)
        Student.objects.create(name="Bob", email="bob@test.com", age=24, department=dept)

    def test_run_all_orm_exercises(self):
        sections = run_all_orm_exercises()
        self.assertTrue(len(sections) >= 10)
        section_ids = [s['id'] for s in sections]
        self.assertIn('1-insert-data', section_ids)
        self.assertIn('2-retrieve-data', section_ids)
        self.assertIn('3-field-lookups', section_ids)
        self.assertIn('4-ordering-data', section_ids)
        self.assertIn('5-aggregation-functions', section_ids)
        self.assertIn('6-relationships-querying', section_ids)
        self.assertIn('7-q-objects', section_ids)
        self.assertIn('8-f-expressions', section_ids)
        self.assertIn('9-pagination', section_ids)
        self.assertIn('10-search-filter-system', section_ids)
        self.assertIn('bonus-tasks', section_ids)
