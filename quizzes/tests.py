from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, Lesson, Module
from learning.models import Progress
from quizzes.models import Answer, Attempt, Question, Quiz


User = get_user_model()


class QuizApiTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="quiz_teacher",
            email="teacher@example.com",
            password="TestPass123!",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="quiz_student",
            email="student@example.com",
            password="TestPass123!",
            role="student",
        )

        course = Course.objects.create(
            title="Quiz test course",
            description="Course for quiz API tests",
            author=self.teacher,
            is_published=True,
        )
        module = Module.objects.create(
            course=course,
            title="Test module",
            order=1,
        )
        lesson = Lesson.objects.create(
            module=module,
            title="Test lesson",
            order=1,
        )
        self.quiz = Quiz.objects.create(
            lesson=lesson,
            title="Test quiz",
            pass_score=70,
        )
        question = Question.objects.create(
            quiz=self.quiz,
            text="What is 2 + 2?",
        )
        self.correct_answer = Answer.objects.create(
            question=question,
            text="4",
            is_correct=True,
        )
        self.wrong_answer = Answer.objects.create(
            question=question,
            text="5",
            is_correct=False,
        )

        self.client.force_authenticate(user=self.student)

    def test_passing_quiz_creates_attempt_and_completes_lesson(self):
        response = self.client.post(
            f"/api/v1/quizzes/{self.quiz.id}/attempt/",
            {"answers": {str(self.correct_answer.question_id): self.correct_answer.id}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 100)
        self.assertTrue(response.data["passed"])
        self.assertTrue(
            Attempt.objects.filter(
                user=self.student,
                quiz=self.quiz,
                score=100,
                passed=True,
            ).exists()
        )
        self.assertTrue(
            Progress.objects.filter(
                student=self.student,
                lesson=self.quiz.lesson,
                is_completed=True,
            ).exists()
        )

    def test_failing_quiz_does_not_complete_lesson(self):
        response = self.client.post(
            f"/api/v1/quizzes/{self.quiz.id}/attempt/",
            {"answers": {str(self.wrong_answer.question_id): self.wrong_answer.id}},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["score"], 0)
        self.assertFalse(response.data["passed"])
        self.assertFalse(
            Progress.objects.filter(
                student=self.student,
                lesson=self.quiz.lesson,
                is_completed=True,
            ).exists()
        )

    def test_student_does_not_see_correct_answer_flags(self):
        response = self.client.get(f"/api/v1/quizzes/{self.quiz.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        answer = response.data["questions"][0]["answers"][0]
        self.assertNotIn("is_correct", answer)
