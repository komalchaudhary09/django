from django.core.management.base import BaseCommand
from django.utils import timezone
from students.models import Department, Student, Course, Enrollment


class Command(BaseCommand):
    help = 'Load sample departments, courses, students (via create, save, bulk_create), and enrollments.'

    def handle(self, *args, **options):
        self.stdout.write('Clearing old records...')
        Enrollment.objects.all().delete()
        Student.all_objects.all().delete()
        Course.objects.all().delete()
        Department.objects.all().delete()

        # -------------------------------------------------------------
        # 1. Create Academic Departments
        # -------------------------------------------------------------
        dept_data = [
            {'code': 'CS', 'name': 'Computer Science', 'description': 'Software Engineering, Systems, and AI.'},
            {'code': 'EE', 'name': 'Electrical Engineering', 'description': 'Electronics, Embedded Systems, and Robotics.'},
            {'code': 'BA', 'name': 'Business Administration', 'description': 'Finance, Management, and Analytics.'},
            {'code': 'MATH', 'name': 'Mathematics', 'description': 'Pure & Applied Mathematics, Statistics.'},
        ]
        departments = {}
        for d in dept_data:
            dept = Department.objects.create(**d)
            departments[dept.code] = dept
        self.stdout.write(self.style.SUCCESS(f'Created {len(departments)} departments.'))

        # -------------------------------------------------------------
        # 2. Create Courses
        # -------------------------------------------------------------
        courses_data = [
            {'code': 'CS101', 'name': 'Introduction to Computer Science', 'duration': 12, 'description': 'Foundations of computing, data structures, and algorithms.'},
            {'code': 'PY201', 'name': 'Python & Django Web Development', 'duration': 8, 'description': 'Full-stack web application development using Python & Django.'},
            {'code': 'DB301', 'name': 'Relational Databases & SQL', 'duration': 6, 'description': 'Schema design, indexing, ORM optimization, and SQL transactions.'},
            {'code': 'WD102', 'name': 'Frontend UI & Modern JavaScript', 'duration': 8, 'description': 'Responsive design, HTML5, CSS3, ES6+ JavaScript.'},
            {'code': 'AI401', 'name': 'Applied Machine Learning', 'duration': 10, 'description': 'Supervised learning, deep neural nets, and predictive modeling.'},
        ]
        courses = {}
        for c in courses_data:
            course = Course.objects.create(**c)
            courses[course.code] = course
        self.stdout.write(self.style.SUCCESS(f'Created {len(courses)} courses.'))

        # -------------------------------------------------------------
        # 3. Create Students using ORM Methods:
        #    • create()
        #    • .save()
        #    • bulk_create()
        # -------------------------------------------------------------

        # Method A: create()
        self.stdout.write("Inserting students using Model.objects.create()...")
        s1 = Student.objects.create(
            name='Alice Johnson', email='alice.johnson@example.com', age=21,
            department=departments['CS'], bio='Passionate about backend architectures and algorithms.'
        )
        s2 = Student.objects.create(
            name='Aaron Miller', email='aaron.miller@example.com', age=19,
            department=departments['CS'], bio='First-year student learning Python and Web dev.'
        )
        s3 = Student.objects.create(
            name='Adam Clark', email='adam.clark@example.com', age=23,
            department=departments['EE'], bio='Embedded systems and IoT device firmware builder.'
        )
        s4 = Student.objects.create(
            name='Bob Smith', email='bob.smith@example.com', age=24,
            department=departments['BA'], bio='Business analyst mastering SQL and financial modeling.'
        )
        s5 = Student.objects.create(
            name='Carol Williams', email='carol.williams@example.com', age=20,
            department=departments['CS'], bio='Full-stack web development and UI enthusiast.'
        )
        s6 = Student.objects.create(
            name='David Brown', email='david.brown@example.com', age=22,
            department=departments['MATH'], bio='Applied math and predictive analytics researcher.'
        )

        # Method B: Instantiation + .save()
        self.stdout.write("Inserting students using model instance .save()...")
        s7 = Student(name='Emma Davis', email='emma.davis@example.com', age=18,
                     department=departments['CS'], bio='High-achieving freshman studying CS.')
        s7.save()

        s8 = Student(name='Frank Miller', email='frank.miller@example.com', age=26,
                     department=departments['EE'], bio='Career switcher learning robotics and Python.')
        s8.save()

        s9 = Student(name='Grace Wilson', email='grace.wilson@example.com', age=23,
                     department=departments['BA'], bio='Entrepreneurship and product management.')
        s9.save()

        s10 = Student(name='Henry Taylor', email='henry.taylor@example.com', age=25,
                      department=departments['MATH'], bio='Cryptographic mathematics and algorithms.')
        s10.save()

        s11 = Student(name='Isabella Martinez', email='isabella.martinez@example.com', age=22,
                      department=departments['CS'], bio='UI/UX designer mastering backend API integration.')
        s11.save()

        s12 = Student(name='Jack Anderson', email='jack.anderson@example.com', age=28,
                      department=departments['EE'], bio='Senior engineer brushing up on modern frameworks.')
        s12.save()

        # Method C: bulk_create()
        self.stdout.write("Inserting students using Model.objects.bulk_create()...")
        bulk_students = [
            Student(name='Austin Wright', email='austin.wright@example.com', age=21,
                    department=departments['CS'], bio='AI student and open source contributor.'),
            Student(name='Liam Evans', email='liam.evans@example.com', age=27,
                    department=departments['BA'], bio='MBA candidate focusing on fintech innovations.'),
            Student(name='Mia White', email='mia.white@example.com', age=17,
                    department=departments['MATH'], bio='Undergraduate prodigy in numerical analysis.'),
            Student(name='Noah Scott', email='noah.scott@example.com', age=24,
                    department=departments['EE'], bio='Signal processing and hardware design.'),
            Student(name='Olivia King', email='olivia.king@example.com', age=18,
                    department=departments['CS'], bio='Cybersecurity and web pentesting hobbyist.'),
            Student(name='Sophia Green', email='sophia.green@example.com', age=20,
                    department=departments['BA'], bio='Marketing analytics and customer retention data.'),
            Student(name='Katherine Thomas', email='katherine.thomas@example.com', age=21,
                    department=departments['CS'], bio='Soft-deleted student account for trash testing.', is_deleted=True),
        ]
        Student.all_objects.bulk_create(bulk_students)

        all_students = list(Student.all_objects.all().order_by('id'))
        self.stdout.write(self.style.SUCCESS(
            f'Created {len(all_students)} total students (6 via create(), 6 via .save(), 7 via bulk_create()).'
        ))

        # -------------------------------------------------------------
        # 4. Create Enrollments
        # -------------------------------------------------------------
        enrollments_data = [
            (all_students[0], courses['CS101'], 'ACTIVE', 'A'),
            (all_students[0], courses['PY201'], 'ACTIVE', 'A+'),
            (all_students[1], courses['CS101'], 'ACTIVE', 'B+'),
            (all_students[2], courses['PY201'], 'ACTIVE', 'A-'),
            (all_students[3], courses['DB301'], 'COMPLETED', 'A'),
            (all_students[4], courses['WD102'], 'ACTIVE', 'A'),
            (all_students[4], courses['PY201'], 'ACTIVE', None),
            (all_students[5], courses['AI401'], 'ACTIVE', 'A+'),
            (all_students[5], courses['CS101'], 'COMPLETED', 'A'),
            (all_students[6], courses['CS101'], 'ACTIVE', None),
            (all_students[7], courses['PY201'], 'ACTIVE', 'B'),
            (all_students[8], courses['DB301'], 'ACTIVE', 'B+'),
            (all_students[9], courses['CS101'], 'ACTIVE', 'A'),
            (all_students[10], courses['WD102'], 'ACTIVE', None),
            (all_students[11], courses['DB301'], 'ACTIVE', 'A+'),
            (all_students[12], courses['AI401'], 'ACTIVE', 'A'),
            (all_students[13], courses['DB301'], 'ACTIVE', None),
            (all_students[14], courses['CS101'], 'ACTIVE', 'Pass'),
            (all_students[15], courses['PY201'], 'COMPLETED', 'A'),
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
