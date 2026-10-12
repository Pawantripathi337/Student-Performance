from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("predict/", views.predict_view, name="predict"),
    path("result/<int:pk>/", views.result, name="result"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("students/", views.students, name="students"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
]
