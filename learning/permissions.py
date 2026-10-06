from rest_framework import permissions

from users.permissions import get_role


def _course_author(obj):
    """Enrollment.course.author  или  Progress.lesson.module.course.author"""
    if hasattr(obj, 'course_id'):
        return getattr(obj.course, 'author', None)
    if hasattr(obj, 'lesson_id'):
        return getattr(obj.lesson.module.course, 'author', None)
    return None


class IsStudentOrReadOnly(permissions.BasePermission):
    """Создавать/менять Enrollment/Progress может только студент (или админ)."""
    message = "Только студент может это делать."
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return get_role(request.user) in ('student', 'admin')


class IsEnrollmentOwnerOrTeacherOrAdmin(permissions.BasePermission):
    """Object-level: студент — своё, teacher — прогресс своих курсов, admin — всё."""
    message = "Нет доступа к этому объекту."

    def has_object_permission(self, request, view, obj):
        role = get_role(request.user)
        if role == 'admin':
            return True
        if getattr(obj, 'student', None) == request.user:
            return True
        if role == 'teacher' and _course_author(obj) == request.user:
            return True
        return False
