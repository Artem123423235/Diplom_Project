from rest_framework.routers import DefaultRouter

from .views import QuizViewSet, QuestionViewSet, AttemptViewSet

router = DefaultRouter()
router.register("quizzes", QuizViewSet, basename="quiz")
router.register("questions", QuestionViewSet, basename="question")
router.register("attempts", AttemptViewSet, basename="attempt")

urlpatterns = router.urls
