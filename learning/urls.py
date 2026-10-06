from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EnrollmentViewSet, ProgressViewSet, EnrollInCourseView

router = DefaultRouter()
router.register('enrollments', EnrollmentViewSet, basename='enrollment')
router.register('progress', ProgressViewSet, basename='progress')

urlpatterns = [
    # удобный шорткат: POST /api/v1/courses/{id}/enroll/
    path('courses/<int:course_id>/enroll/', EnrollInCourseView.as_view(), name='course-enroll'),
    *router.urls,
]
