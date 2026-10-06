from users.permissions import IsAuthorOrReadOnly, IsTeacherOrReadOnly

__all__ = ['IsAuthorOrReadOnly', 'IsTeacherOrReadOnly']

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Чтение доступно всем.
    Изменения доступны преподавателю или администратору,
    а для существующего объекта — только автору курса или администратору.
    """

    message = (
        'Редактировать может только автор курса '
        'или администратор.'
    )

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('teacher', 'admin')
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role == 'admin' or request.user.is_superuser:
            return True

        return self._resolve_author(obj) == request.user

    @staticmethod
    def _resolve_author(obj):
        """Находит автора курса для курса и связанных с ним объектов."""
        if hasattr(obj, 'author'):       # Course
            return obj.author
        if hasattr(obj, 'module'):        # Lesson
            return IsAuthorOrReadOnly._resolve_author(obj.module)
        if hasattr(obj, 'course'):        # Module
            return obj.course.author
        if hasattr(obj, 'lesson'):        # Quiz
            return IsAuthorOrReadOnly._resolve_author(obj.lesson)
        if hasattr(obj, 'quiz'):          # Question
            return IsAuthorOrReadOnly._resolve_author(obj.quiz)
        if hasattr(obj, 'question'):      # Answer
            return IsAuthorOrReadOnly._resolve_author(obj.question)
        return None


class IsTeacherOrReadOnly(IsAuthorOrReadOnly):
    """Разрешения на изменение объектов преподавателем или администратором."""