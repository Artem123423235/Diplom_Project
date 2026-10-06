from rest_framework import permissions, viewsets

from .models import Quiz, Question, Attempt
from .serializers import QuizSerializer, QuestionSerializer, AttemptSerializer


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Quiz.objects.all()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Quiz.objects.none()
        qs = Quiz.objects.select_related("lesson").prefetch_related(
            "questions__answers"
        )
        role = getattr(user, "role", None)
        if role == "teacher":
            return qs.filter(lesson__module__course__author=user)
        return qs


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Question.objects.all()


class AttemptViewSet(viewsets.ModelViewSet):
    serializer_class = AttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Attempt.objects.none()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Attempt.objects.none()
        base = Attempt.objects.select_related("quiz", "quiz__lesson", "user")
        role = getattr(user, "role", None)
        if role == "student":
            return base.filter(user=user)
        if role == "teacher":
            return base.filter(quiz__lesson__module__course__author=user)
        return base
