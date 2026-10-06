from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course

from .models import Enrollment, Progress
from .serializers import EnrollmentSerializer, ProgressSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    # queryset нужен DRF-схеме; реальный набор фильтруем в get_queryset()
    queryset = Enrollment.objects.none()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Enrollment.objects.none()
        role = getattr(user, 'role', None)
        base = Enrollment.objects.select_related('course', 'student')
        if role == 'student':
            return base.filter(student=user)
        if role == 'teacher':
            return base.filter(course__author=user)
        return base

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class ProgressViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Progress.objects.none()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Progress.objects.none()
        role = getattr(user, 'role', None)
        base = Progress.objects.select_related(
            'lesson', 'lesson__module', 'lesson__module__course', 'student',
        )
        if role == 'student':
            return base.filter(student=user)
        if role == 'teacher':
            return base.filter(lesson__module__course__author=user)
        return base

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


@extend_schema(request=None, responses={201: EnrollmentSerializer})
class EnrollInCourseView(APIView):
    """Записать текущего студента на курс по его id."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, course=course,
        )
        if not created:
            return Response(
                {'detail': 'Вы уже записаны на этот курс.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )
