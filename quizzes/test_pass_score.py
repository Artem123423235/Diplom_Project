from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from quizzes.models import Quiz


class QuizPassScoreValidatorTests(SimpleTestCase):
    def test_pass_score_accepts_100(self):
        field = Quiz._meta.get_field("pass_score")
        self.assertEqual(field.clean(100, None), 100)

    def test_pass_score_rejects_101(self):
        field = Quiz._meta.get_field("pass_score")

        with self.assertRaises(ValidationError):
            field.clean(101, None)
