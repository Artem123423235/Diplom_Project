from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from quizzes.models import Attempt


class AttemptScoreValidatorTests(SimpleTestCase):
    def test_score_accepts_100(self):
        field = Attempt._meta.get_field("score")
        self.assertEqual(field.clean(100, None), 100)

    def test_score_rejects_101(self):
        field = Attempt._meta.get_field("score")

        with self.assertRaises(ValidationError):
            field.clean(101, None)
