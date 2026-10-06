"""
Общие permissions-классы. Роли: student / teacher / admin.
"""
from rest_framework import permissions


def get_role(user):
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return 'admin'
    return getattr(user, 'role', None)


class IsTeacher(permissions.BasePermission):
    message = "Требуется роль преподавателя."
    def has_permission(self, request, view):
        return get_role(request.user) in ('teacher', 'admin')


class IsAdmin(permissions.BasePermission):
    message = "Требуется роль администратора."
    def has_permission(self, request, view):
        return get_role(request.user) == 'admin'


class IsTeacherOrReadOnly(permissions.BasePermission):
    """Читать — всем, изменять — только teacher/admin."""
    message = "Изменять контент может только преподаватель."
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return get_role(request.user) in ('teacher', 'admin')


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Object-level. Владелец разворачивается по цепочке:
      Course.author
      Module.course.author
      Lesson.module.course.author
      Enrollment.student / Progress.student
    """
    message = "Редактировать может только автор."

    OWNER_PATHS = (
        ('author',),
        ('course', 'author'),
        ('module', 'course', 'author'),
        ('lesson', 'module', 'course', 'author'),
        ('quiz', 'lesson', 'module', 'course', 'author'),
    )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if get_role(request.user) == 'admin':
            return True
        owner = self._resolve_owner(obj)
        return owner is not None and owner == request.user

    def _resolve_owner(self, obj):
        for path in self.OWNER_PATHS:
            cur, ok = obj, True
            for attr in path:
                if not hasattr(cur, attr):
                    ok = False
                    break
                cur = getattr(cur, attr)
                if cur is None:
                    ok = False
                    break
            if ok:
                return cur
        return None
