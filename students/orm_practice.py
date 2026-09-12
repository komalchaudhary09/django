"""
Django ORM Comprehensive Practice Suite
Contains modular functions demonstrating all 10 core ORM topics + Bonus tasks.
Can be executed via CLI (`python manage.py run_orm_practice`) or rendered in the Web UI (`/orm-lab/`).
"""

from django.db.models import Q, F, Count, Avg, Max, Min, Sum
from django.core.paginator import Paginator
from students.models import Student, Department, Course, Enrollment


def run_all_orm_exercises():
    """
    Executes and returns structured results for each of the 10 practice topics + Bonus tasks.
    """
    sections = []

    # =========================================================================
    # 1. Insert Data Using ORM
    # =========================================================================
    # Note: Sample data loader already demonstrated create(), save(), bulk_create().
    # Here we show their syntax and inspect the created records.
    insert_demo = {
        'id': '1-insert-data',
        'title': '1. Insert Data Using ORM',
        'description': "Demonstrates create(), .save(), and bulk_create().",
        'examples': [
            {
                'subtitle': "A. Model.objects.create()",
                'code': "Student.objects.create(name='Example One', email='ex1@test.com', age=20, department=dept)",
                'explanation': "Instantiates and saves a single record to the database in a single step.",
                'result': f"Sample students created via create(): {list(Student.objects.filter(email__in=['alice.johnson@example.com', 'aaron.miller@example.com']).values('name', 'email', 'age'))}",
            },
            {
                'subtitle': "B. Model instance .save()",
                'code': "student = Student(name='Example Two', email='ex2@test.com', age=22)\nstudent.save()",
                'explanation': "Instantiates the model object in Python memory first, then writes it to SQL via .save().",
                'result': f"Sample students created via .save(): {list(Student.objects.filter(email__in=['emma.davis@example.com', 'frank.miller@example.com']).values('name', 'email', 'age'))}",
            },
            {
                'subtitle': "C. Model.objects.bulk_create()",
                'code': "Student.objects.bulk_create([\n    Student(name='Student A', email='a@test.com', age=21),\n    Student(name='Student B', email='b@test.com', age=22),\n])",
                'explanation': "Executes a single multi-row SQL INSERT statement, highly optimized for importing batches.",
                'result': f"Sample students created via bulk_create(): {list(Student.objects.filter(email__in=['austin.wright@example.com', 'liam.evans@example.com']).values('name', 'email', 'age'))}",
            },
        ]
    }
    sections.append(insert_demo)

    # =========================================================================
    # 2. Retrieve Data
    # =========================================================================
    all_students = Student.objects.all()
    first_student = Student.objects.first()
    last_student = Student.objects.last()
    exists_check = Student.objects.filter(age__gt=25).exists()
    above_18 = Student.objects.filter(age__gt=18)
    exclude_cs = Student.objects.exclude(department__code='CS')

    target_student = Student.objects.filter(email='alice.johnson@example.com').first() or Student.objects.first()
    if target_student:
        single_student = Student.objects.get(id=target_student.id)
        get_code = f"Student.objects.get(id={target_student.id})  # Retrieve single record"
        get_result = f"Found: {single_student.name}, Email: {single_student.email}, Age: {single_student.age}"
    else:
        get_code = "Student.objects.get(id=1)"
        get_result = "No student record found to retrieve"

    retrieve_demo = {
        'id': '2-retrieve-data',
        'title': '2. Retrieve Data',
        'description': "Practice all(), get(), filter(), exclude(), first(), last(), and exists().",
        'examples': [
            {
                'subtitle': "all() - Display all active students",
                'code': "Student.objects.all()",
                'sql': str(all_students.query) if all_students.exists() else "SELECT ... FROM students_student",
                'result': [f"{s.name} (Age: {s.age})" for s in all_students[:6]] + ([f"... and {all_students.count() - 6} more"] if all_students.count() > 6 else []),
            },
            {
                'subtitle': "get() - Retrieve exact single record",
                'code': get_code,
                'result': get_result,
            },
            {
                'subtitle': "filter() - Display students above age 18",
                'code': "Student.objects.filter(age__gt=18)",
                'sql': str(above_18.query) if above_18.exists() else "SELECT ... WHERE age > 18",
                'result': [f"{s.name} ({s.age} yrs)" for s in above_18],
            },
            {
                'subtitle': "exclude() - Exclude students from Computer Science (CS) department",
                'code': "Student.objects.exclude(department__code='CS')",
                'sql': str(exclude_cs.query) if exclude_cs.exists() else "SELECT ... WHERE NOT (dept = CS)",
                'result': [f"{s.name} ({s.department.code if s.department else 'None'})" for s in exclude_cs],
            },
            {
                'subtitle': "first() & last()",
                'code': "first = Student.objects.first()\nlast = Student.objects.last()",
                'result': f"First: {first_student.name if first_student else 'None'} | Last: {last_student.name if last_student else 'None'}",
            },
            {
                'subtitle': "exists() - Check if any student above age 25 exists",
                'code': "Student.objects.filter(age__gt=25).exists()",
                'result': f"Exists check returned: {exists_check}",
            },
        ]
    }
    sections.append(retrieve_demo)

    # =========================================================================
    # 3. Field Lookups
    # =========================================================================
    starts_with_a = Student.objects.filter(name__startswith='A')
    ends_with_n = Student.objects.filter(name__endswith='n')
    icontains_john = Student.objects.filter(name__icontains='john')
    age_gt_20 = Student.objects.filter(age__gt=20)
    age_lt_20 = Student.objects.filter(age__lt=20)
    age_gte_22 = Student.objects.filter(age__gte=22)
    age_lte_19 = Student.objects.filter(age__lte=19)
    age_18_to_25 = Student.objects.filter(age__range=(18, 25))
    in_dept_list = Student.objects.filter(department__code__in=['CS', 'MATH'])

    lookups_demo = {
        'id': '3-field-lookups',
        'title': '3. Field Lookups',
        'description': "Practice icontains, startswith, endswith, gt, lt, gte, lte, range, in.",
        'examples': [
            {
                'subtitle': "startswith - Find students whose name starts with 'A'",
                'code': "Student.objects.filter(name__startswith='A')",
                'sql': str(starts_with_a.query),
                'result': [f"{s.name} (Age: {s.age})" for s in starts_with_a],
            },
            {
                'subtitle': "range - Find students aged between 18 and 25",
                'code': "Student.objects.filter(age__range=(18, 25))",
                'sql': str(age_18_to_25.query),
                'result': [f"{s.name} ({s.age})" for s in age_18_to_25],
            },
            {
                'subtitle': "icontains - Case-insensitive substring match ('john')",
                'code': "Student.objects.filter(name__icontains='john')",
                'result': [s.name for s in icontains_john],
            },
            {
                'subtitle': "endswith - Name ending with 'n'",
                'code': "Student.objects.filter(name__endswith='n')",
                'result': [s.name for s in ends_with_n],
            },
            {
                'subtitle': "gt, lt, gte, lte - Comparisons",
                'code': "gt(20), lt(20), gte(22), lte(19)",
                'result': (
                    f"age > 20: {age_gt_20.count()} students | "
                    f"age < 20: {age_lt_20.count()} students | "
                    f"age >= 22: {age_gte_22.count()} students | "
                    f"age <= 19: {age_lte_19.count()} students"
                ),
            },
            {
                'subtitle': "in - Department code in ['CS', 'MATH']",
                'code': "Student.objects.filter(department__code__in=['CS', 'MATH'])",
                'result': [f"{s.name} ({s.department.code})" for s in in_dept_list],
            },
        ]
    }
    sections.append(lookups_demo)

    # =========================================================================
    # 4. Ordering Data
    # =========================================================================
    age_asc = Student.objects.order_by('age')
    age_desc = Student.objects.order_by('-age')

    ordering_demo = {
        'id': '4-ordering-data',
        'title': '4. Ordering Data',
        'description': "Use order_by() to sort students by age ascending and descending.",
        'examples': [
            {
                'subtitle': "Sort students by age ascending (order_by('age'))",
                'code': "Student.objects.order_by('age')",
                'sql': str(age_asc.query),
                'result': [f"{s.name} ({s.age})" for s in age_asc[:8]],
            },
            {
                'subtitle': "Sort students by age descending (order_by('-age'))",
                'code': "Student.objects.order_by('-age')",
                'sql': str(age_desc.query),
                'result': [f"{s.name} ({s.age})" for s in age_desc[:8]],
            },
        ]
    }
    sections.append(ordering_demo)

    # =========================================================================
    # 5. Aggregation Functions
    # =========================================================================
    agg_results = Student.objects.aggregate(
        total_students=Count('id'),
        average_age=Avg('age'),
        max_age=Max('age'),
        min_age=Min('age'),
        sum_ages=Sum('age'),
    )

    aggregation_demo = {
        'id': '5-aggregation-functions',
        'title': '5. Aggregation Functions',
        'description': "Compute count(), sum(), avg(), max(), min() using Django models aggregations.",
        'examples': [
            {
                'subtitle': "Count, Avg, Max, Min, Sum across Student table",
                'code': (
                    "from django.db.models import Count, Avg, Max, Min, Sum\n"
                    "Student.objects.aggregate(\n"
                    "    total_students=Count('id'),\n"
                    "    average_age=Avg('age'),\n"
                    "    max_age=Max('age'),\n"
                    "    min_age=Min('age'),\n"
                    "    sum_ages=Sum('age')\n"
                    ")"
                ),
                'result': {
                    'Total Students': agg_results['total_students'],
                    'Average Age': round(agg_results['average_age'], 2) if agg_results['average_age'] else None,
                    'Max Age': agg_results['max_age'],
                    'Min Age': agg_results['min_age'],
                    'Sum of Ages': agg_results['sum_ages'],
                }
            },
        ]
    }
    sections.append(aggregation_demo)

    # =========================================================================
    # 6. Relationships Querying
    # =========================================================================
    sample_student = Student.objects.filter(department__isnull=False).first() or Student.objects.first()
    forward_lookup = sample_student.department.name if sample_student and sample_student.department else "None"
    dept_code = sample_student.department.code if sample_student and sample_student.department else "N/A"
    student_name = sample_student.name if sample_student else "None"

    sample_dept = Department.objects.filter(code='CS').first() or Department.objects.first()
    reverse_students = sample_dept.students.filter(is_deleted=False) if sample_dept else []
    dept_name = sample_dept.name if sample_dept else "Department"

    relationships_demo = {
        'id': '6-relationships-querying',
        'title': '6. Relationships Querying',
        'description': "Forward lookup, reverse lookup, and related manager filtering.",
        'examples': [
            {
                'subtitle': "Forward Lookup: Show department of a student",
                'code': "student = Student.objects.select_related('department').first()\ndepartment_name = student.department.name",
                'result': f"Student '{student_name}' belongs to department '{forward_lookup}' ({dept_code})",
            },
            {
                'subtitle': f"Reverse Lookup: Show all students in a department ({dept_name})",
                'code': "department = Department.objects.first()\nstudents = department.students.filter(is_deleted=False)",
                'result': [f"{s.name} (Age {s.age})" for s in reverse_students],
            },
            {
                'subtitle': "Related Manager Filter: Active enrollments for a course",
                'code': "course = Course.objects.first()\nenrolled_students = [e.student.name for e in course.enrollments.filter(status='ACTIVE')]",
                'result': [
                    f"{e.student.name} (Grade: {e.grade or 'In Progress'})"
                    for e in Enrollment.objects.filter(status='ACTIVE')[:5]
                ],
            },
        ]
    }
    sections.append(relationships_demo)

    # =========================================================================
    # 7. Q Objects (Complex Filtering)
    # =========================================================================
    q_query = Student.objects.filter(Q(age__gt=20) | Q(name__icontains='a'))

    q_demo = {
        'id': '7-q-objects',
        'title': '7. Q Objects (Complex Filtering)',
        'description': "Perform complex boolean OR / AND / NOT conditions using Q objects.",
        'examples': [
            {
                'subtitle': "Example: age > 20 OR name contains 'a' (case-insensitive)",
                'code': "from django.db.models import Q\nStudent.objects.filter(Q(age__gt=20) | Q(name__icontains='a'))",
                'sql': str(q_query.query),
                'result': [f"{s.name} (Age: {s.age})" for s in q_query[:10]],
            },
            {
                'subtitle': "Example: Department CS AND (age < 20 OR name starts with 'A')",
                'code': "Student.objects.filter(Q(department__code='CS') & (Q(age__lt=20) | Q(name__startswith='A')))",
                'result': [
                    f"{s.name} (Age: {s.age}, Dept: {s.department.code})"
                    for s in Student.objects.filter(
                        Q(department__code='CS') & (Q(age__lt=20) | Q(name__startswith='A'))
                    )
                ],
            },
        ]
    }
    sections.append(q_demo)

    # =========================================================================
    # 8. F Expressions
    # =========================================================================
    # Demonstrate F expression safely without corrupting base data
    # (e.g. increase age of a temporary or single student and revert)
    demo_s = Student.objects.order_by('id').first()
    original_age = demo_s.age if demo_s else 20
    if demo_s:
        Student.objects.filter(id=demo_s.id).update(age=F('age') + 1)
        demo_s.refresh_from_db()
        incremented_age = demo_s.age
        # Revert back to original age
        Student.objects.filter(id=demo_s.id).update(age=original_age)

    f_demo = {
        'id': '8-f-expressions',
        'title': '8. F Expressions',
        'description': "In-database atomic calculations, field increments, and comparisons without race conditions.",
        'examples': [
            {
                'subtitle': "Increase student age by 1 directly in database",
                'code': (
                    "from django.db.models import F\n"
                    "# Atomic database level increment without pulling into Python memory:\n"
                    "Student.objects.filter(id=student_id).update(age=F('age') + 1)"
                ),
                'explanation': "Generates: UPDATE students_student SET age = age + 1 WHERE id = ...",
                'result': f"Tested on '{demo_s.name if demo_s else 'Demo'}': Original age {original_age} -> Incremented to {incremented_age} -> Restored to {original_age}",
            },
        ]
    }
    sections.append(f_demo)

    # =========================================================================
    # 9. Pagination
    # =========================================================================
    paginator = Paginator(Student.objects.all().order_by('id'), 5)
    page_1 = paginator.get_page(1)
    page_2 = paginator.get_page(2)

    pagination_demo = {
        'id': '9-pagination',
        'title': '9. Pagination',
        'description': "Django Paginator configured with 5 students per page.",
        'examples': [
            {
                'subtitle': "Display 5 students per page",
                'code': (
                    "from django.core.paginator import Paginator\n"
                    "paginator = Paginator(Student.objects.all().order_by('id'), 5)\n"
                    "page_1 = paginator.get_page(1)"
                ),
                'result': {
                    'Total Students': paginator.count,
                    'Total Pages': paginator.num_pages,
                    'Page 1 items': [s.name for s in page_1],
                    'Page 2 items': [s.name for s in page_2],
                }
            },
        ]
    }
    sections.append(pagination_demo)

    # =========================================================================
    # 10. Search + Filter System
    # =========================================================================
    search_q = 'miller'
    dept_f = 'CS'
    age_min_f = 19
    age_max_f = 22

    search_filter_qs = Student.objects.filter(
        Q(name__icontains=search_q) | Q(email__icontains=search_q),
        department__code=dept_f,
        age__gte=age_min_f,
        age__lte=age_max_f
    )

    search_filter_demo = {
        'id': '10-search-filter-system',
        'title': '10. Search + Filter System',
        'description': "Multi-parameter filtering combining name search, department filter, and age range.",
        'examples': [
            {
                'subtitle': "Combined Search & Filter (Name search + Dept filter + Age range)",
                'code': (
                    "Student.objects.filter(\n"
                    "    Q(name__icontains='miller') | Q(email__icontains='miller'),\n"
                    "    department__code='CS',\n"
                    "    age__gte=19,\n"
                    "    age__lte=22\n"
                    ")"
                ),
                'sql': str(search_filter_qs.query),
                'result': [f"{s.name} (Dept: {s.department.code}, Age: {s.age})" for s in search_filter_qs],
            }
        ]
    }
    sections.append(search_filter_demo)

    # =========================================================================
    # Bonus Tasks
    # =========================================================================
    annotated_depts = Department.objects.annotate(
        active_student_count=Count('students', filter=Q(students__is_deleted=False))
    )
    values_data = list(Student.objects.values('id', 'name', 'age')[:4])
    values_list_data = list(Student.objects.values_list('name', flat=True)[:4])
    distinct_ages = list(Student.objects.order_by('age').values_list('age', flat=True).distinct()[:8])
    select_related_demo = list(Student.objects.select_related('department')[:4])
    prefetch_related_demo = list(Course.objects.prefetch_related('enrollments__student')[:3])

    bonus_demo = {
        'id': 'bonus-tasks',
        'title': 'Bonus Tasks: Advanced ORM Optimization',
        'description': "Practice annotate(), values(), values_list(), distinct(), select_related(), prefetch_related().",
        'examples': [
            {
                'subtitle': "annotate() - Count students per department via SQL GROUP BY",
                'code': "Department.objects.annotate(active_student_count=Count('students', filter=Q(students__is_deleted=False)))",
                'result': [f"{d.name} ({d.code}): {d.active_student_count} students" for d in annotated_depts],
            },
            {
                'subtitle': "values() - Return query results as dictionaries instead of model instances",
                'code': "Student.objects.values('id', 'name', 'age')[:4]",
                'result': values_data,
            },
            {
                'subtitle': "values_list(flat=True) - Return single-column scalar list",
                'code': "Student.objects.values_list('name', flat=True)[:4]",
                'result': values_list_data,
            },
            {
                'subtitle': "distinct() - Unique values",
                'code': "Student.objects.order_by('age').values_list('age', flat=True).distinct()",
                'result': distinct_ages,
            },
            {
                'subtitle': "select_related('department') - SQL INNER/LEFT JOIN for ForeignKey (Single Query)",
                'code': "Student.objects.select_related('department').all()",
                'explanation': "Avoids N+1 query problem by joining the related single-object department table in the same SQL statement.",
                'result': [f"{s.name} -> {s.department.name if s.department else 'N/A'}" for s in select_related_demo],
            },
            {
                'subtitle': "prefetch_related('enrollments__student') - Multi-table batching for M2M / Reverse ForeignKey",
                'code': "Course.objects.prefetch_related('enrollments__student').all()",
                'explanation': "Executes separate queries and joins records in Python, ideal for many-to-many and reverse lookups.",
                'result': [f"Course: {c.code} ({c.name}) - {c.enrollments.count()} enrollments" for c in prefetch_related_demo],
            },
        ]
    }
    sections.append(bonus_demo)

    return sections
