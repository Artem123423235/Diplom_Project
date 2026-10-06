from django.db.models import Q
from rest_framework import viewsets

from users.permissions import IsTeacherOrReadOnly, IsAuthorOrReadOnly, get_role

from .models import Course, Lesson, Module
from .serializers import (
    CourseDetailSerializer, CourseListSerializer,
    LessonSerializer, ModuleSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('author').prefetch_related('modules__lessons')
    permission_classes = [IsTeacherOrReadOnly, IsAuthorOrReadOnly]
    filterset_fields = ['level', 'is_published', 'author']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        return CourseListSerializer if self.action == 'list' else CourseDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        role = get_role(user)
        if role == 'admin':
            return qs
        if role == 'teacher':
            return qs.filter(Q(is_published=True) | Q(author=user))
        return qs.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsTeacherOrReadOnly, IsAuthorOrReadOnly]
    filterset_fields = ['course']
    ordering = ['order']

    def get_queryset(self):
        qs = Module.objects.select_related('course__author').prefetch_related('lessons')
        user = self.request.user
        role = get_role(user)
        if role == 'admin':
            return qs
        if role == 'teacher':
            return qs.filter(Q(course__is_published=True) | Q(course__author=user))
        return qs.filter(course__is_published=True)


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsTeacherOrReadOnly, IsAuthorOrReadOnly]
    filterset_fields = ['module']
    ordering = ['order']

    def get_queryset(self):
        qs = Lesson.objects.select_related('module__course__author')
        user = self.request.user
        role = get_role(user)
        if role == 'admin':
            return qs
        if role == 'teacher':
            return qs.filter(
                Q(module__course__is_published=True) | Q(module__course__author=user)
            )
        return qs.filter(module__course__is_published=True)
