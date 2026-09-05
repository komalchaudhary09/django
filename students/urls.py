from django.urls import path
from . import views

urlpatterns = [
    # Static & Dashboard Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Student CRUD & Actions
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:pk>/restore/', views.student_restore, name='student_restore'),
    path('students/<int:pk>/permanent-delete/', views.student_hard_delete, name='student_hard_delete'),

    # Course Views
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),

    # Enrollment Views
    path('enrollments/create/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/<int:pk>/delete/', views.enrollment_delete, name='enrollment_delete'),
]
