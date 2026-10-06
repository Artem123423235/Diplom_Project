from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from courses.models import Course, Lesson, Module
from learning.models import Progress
from quizzes.models import Answer, Attempt, Question, Quiz


class QuizAttemptApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="test-password",
            role="student",
        )

        course = Course.objects.create(
            title="Тестовый курс",
            author=self.student,
        )
        module = Module.objects.create(
            course=course,
            title="Тестовый модуль",
        )
        self.lesson = Lesson.objects.create(
            module=module,
            title="Тестовый урок",
        )
        self.quiz = Quiz.objects.create(
            lesson=self.lesson,
            title="Тест",
            pass_score=50,
        )

        self.questions = []
        for number in range(2):
            question = Question.objects.create(
                quiz=self.quiz,
                text=f"Вопрос {number + 1}",
            )
            correct_answer = Answer.objects.create(
                question=question,
                text="Правильный ответ",
                is_correct=True,
            )
            wrong_answer = Answer.objects.create(
                question=question,
                text="Неправильный ответ",
                is_correct=False,
            )
            self.questions.append((question, correct_answer, wrong_answer))

        self.client.force_authenticate(user=self.student)
        self.url = reverse("quiz-attempt", kwargs={"pk": self.quiz.pk})

    def test_passing_attempt_completes_lesson(self):
        first_question, correct_answer, _ = self.questions[0]

        response = self.client.post(
            self.url,
            {"answers": {str(first_question.pk): correct_answer.pk}},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["score"], 50)
        self.assertTrue(response.data["passed"])

        progress = Progress.objects.get(
            student=self.student,
            lesson=self.lesson,
        )
        self.assertTrue(progress.is_completed)

    def test_failing_attempt_does_not_complete_lesson(self):
        answers = {
            str(question.pk): wrong_answer.pk
            for question, _, wrong_answer in self.questions
        }

        response = self.client.post(
            self.url,
            {"answers": answers},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["score"], 0)
        self.assertFalse(response.data["passed"])
        self.assertFalse(
            Progress.objects.filter(
                student=self.student,
                lesson=self.lesson,
                is_completed=True,
            ).exists()
        )

    def test_attempt_is_saved(self):
        first_question, correct_answer, _ = self.questions[0]

        self.client.post(
            self.url,
            {"answers": {str(first_question.pk): correct_answer.pk}},
            format="json",
        )

        self.assertEqual(
            Attempt.objects.filter(user=self.student, quiz=self.quiz).count(),
            1,
        )

    def test_public_quiz_does_not_reveal_correct_answers(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("quiz-detail", kwargs={"pk": self.quiz.pk})
        )

        self.assertEqual(response.status_code, 200)
        answers = response.data["questions"][0]["answers"]
        self.assertTrue(answers)
        self.assertNotIn("is_correct", answers[0])

    def test_unauthenticated_user_cannot_submit_attempt(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url,
            {"answers": {str(self.questions[0][0].pk): self.questions[0][1].pk}},
            format="json",
        )

        self.assertIn(response.status_code, (401, 403))
