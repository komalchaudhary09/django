from django.core.management.base import BaseCommand
from django.utils import timezone
from students.models import Student, Course, Enrollment


class Command(BaseCommand):
    help = 'Load sample courses, students, and enrollments into the database'

    def handle(self, *args, **options):
        self.stdout.write('Clearing old sample records...')
        Enrollment.objects.all().delete()
        Student.all_objects.all().delete()
        Course.objects.all().delete()

        # 1. Create Courses
        courses_data = [
            {'code': 'CS101', 'name': 'Introduction to Computer Science', 'duration': 12, 'description': 'Foundational principles of algorithms, data structures, and computing systems.'},
            {'code': 'PY201', 'name': 'Python & Django Web Development', 'duration': 8, 'description': 'Full-stack web application development using Python, Django, ORM, and Bootstrap.'},
            {'code': 'DB301', 'name': 'Relational Databases & SQL', 'duration': 6, 'description': 'Schema design, indexing, foreign keys, query optimization, and transactions.'},
            {'code': 'WD102', 'name': 'Frontend UI & Modern JavaScript', 'duration': 8, 'description': 'Responsive design, HTML5, CSS3, ES6+ JavaScript, and component libraries.'},
            {'code': 'AI401', 'name': 'Applied Machine Learning', 'duration': 10, 'description': 'Supervised and unsupervised learning, model evaluation, and predictive analytics.'},
        ]

        created_courses = {}
        for data in courses_data:
            course = Course.objects.create(**data)
            created_courses[course.code] = course
        self.stdout.write(self.style.SUCCESS(f'Created {len(created_courses)} courses.'))

        # 2. Create Students
        students_data = [
            {'name': 'Alice Johnson', 'email': 'alice.johnson@example.com', 'age': 21, 'bio': 'Passionate about backend architectures and distributed databases.'},
            {'name': 'Bob Smith', 'email': 'bob.smith@example.com', 'age': 24, 'bio': 'Aspiring Python developer with a passion for open-source software.'},
            {'name': 'Carol Williams', 'email': 'carol.williams@example.com', 'age': 20, 'bio': 'Frontend developer learning full-stack Django.'},
            {'name': 'David Brown', 'email': 'david.brown@example.com', 'age': 22, 'bio': 'Data science enthusiast and machine learning researcher.'},
            {'name': 'Emma Davis', 'email': 'emma.davis@example.com', 'age': 19, 'bio': 'First-year CS student interested in software engineering.'},
            {'name': 'Frank Miller', 'email': 'frank.miller@example.com', 'age': 26, 'bio': 'Career switcher transitioning into backend web development.'},
            {'name': 'Grace Wilson', 'email': 'grace.wilson@example.com', 'age': 23, 'bio': 'Cybersecurity enthusiast exploring web application security.'},
            {'name': 'Henry Taylor', 'email': 'henry.taylor@example.com', 'age': 25, 'bio': 'Mobile and web developer focusing on scalable APIs.'},
            {'name': 'Isabella Martinez', 'email': 'isabella.martinez@example.com', 'age': 22, 'bio': 'UI/UX designer learning full-stack development.'},
            {'name': 'Jack Anderson', 'email': 'jack.anderson@example.com', 'age': 28, 'bio': 'Database administrator mastering Django ORM.'},
            {'name': 'Katherine Thomas', 'email': 'katherine.thomas@example.com', 'age': 21, 'bio': 'Soft-deleted demo student account for testing trash recovery.', 'is_deleted': True},
        ]

        created_students = []
        for data in students_data:
            is_del = data.pop('is_deleted', False)
            student = Student.all_objects.create(**data, is_deleted=is_del)
            created_students.append(student)
        self.stdout.write(self.style.SUCCESS(f'Created {len(created_students)} students (including 1 soft-deleted).'))

        # 3. Create Enrollments (Relationships)
        enrollments_data = [
            (created_students[0], created_courses['CS101'], 'ACTIVE', 'A'),
            (created_students[0], created_courses['PY201'], 'ACTIVE', 'A+'),
            (created_students[1], created_courses['PY201'], 'ACTIVE', 'B+'),
            (created_students[1], created_courses['DB301'], 'COMPLETED', 'A'),
            (created_students[2], created_courses['WD102'], 'ACTIVE', 'A'),
            (created_students[2], created_courses['PY201'], 'ACTIVE', None),
            (created_students[3], created_courses['AI401'], 'ACTIVE', 'A+'),
            (created_students[3], created_courses['CS101'], 'COMPLETED', 'A'),
            (created_students[4], created_courses['CS101'], 'ACTIVE', None),
            (created_students[5], created_courses['PY201'], 'ACTIVE', 'B'),
            (created_students[5], created_courses['DB301'], 'ACTIVE', None),
            (created_students[6], created_courses['CS101'], 'ACTIVE', 'A-'),
            (created_students[7], created_courses['WD102'], 'COMPLETED', 'A'),
            (created_students[8], created_courses['WD102'], 'ACTIVE', None),
            (created_students[9], created_courses['DB301'], 'ACTIVE', 'A+'),
            (created_students[9], created_courses['PY201'], 'DROPPED', 'W'),
        ]

        for student, course, status, grade in enrollments_data:
            Enrollment.objects.create(
                student=student,
                course=course,
                status=status,
                grade=grade
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(enrollments_data)} course enrollments.'))
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
