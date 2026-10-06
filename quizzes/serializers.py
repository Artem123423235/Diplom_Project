import json

from django.utils import timezone
from rest_framework import serializers

from learning.models import Progress
from .models import Quiz, Question, Answer, Attempt


def _normalize_answer_ids(value):
    if value is None:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise serializers.ValidationError("answers must be valid JSON.") from exc
    if isinstance(value, dict):
        value = list(value.values())
    if not isinstance(value, list):
        raise serializers.ValidationError("answers must be a list or a dict.")
    try:
        return [int(x) for x in value]
    except (TypeError, ValueError) as exc:
        raise serializers.ValidationError("answer ids must be integers.") from exc


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "answers"]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "lesson", "title", "pass_score", "questions"]


class AttemptSerializer(serializers.ModelSerializer):
    answers = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = Attempt
        fields = ["id", "quiz", "score", "passed", "created_at", "answers"]
        read_only_fields = ["score", "passed", "created_at"]

    def validate_answers(self, value):
        return _normalize_answer_ids(value)

    def validate(self, attrs):
        quiz = attrs.get("quiz")
        answers = attrs.get("answers")
        if quiz is None or answers is None:
            return attrs
        valid_ids = set(
            Answer.objects.filter(question__quiz=quiz).values_list("id", flat=True)
        )
        unknown = [i for i in answers if i not in valid_ids]
        if unknown:
            raise serializers.ValidationError(
                {"answers": f"Answers {unknown} do not belong to this quiz."}
            )
        return attrs

    def create(self, validated_data):
        quiz = validated_data["quiz"]
        user = self.context["request"].user
        answer_ids = validated_data.get("answers") or []

        selected = list(
            Answer.objects.filter(id__in=answer_ids).select_related("question")
        )
        by_question = {}
        for a in selected:
            by_question.setdefault(a.question_id, []).append(a)

        correct_count = 0
        for q_id in quiz.questions.values_list("id", flat=True):
            correct_ids = set(
                Answer.objects.filter(question_id=q_id, is_correct=True)
                .values_list("id", flat=True)
            )
            chosen_ids = {a.id for a in by_question.get(q_id, [])}
            if correct_ids and chosen_ids == correct_ids:
                correct_count += 1

        total = quiz.questions.count() or 1
        score = round(correct_count / total * 100)
        passed = score >= (quiz.pass_score or 0)

        attempt = Attempt.objects.create(
            user=user, quiz=quiz, score=score, passed=passed,
        )

        if passed and quiz.lesson_id:
            Progress.objects.update_or_create(
                student=user,
                lesson=quiz.lesson,
                defaults={"is_completed": True, "completed_at": timezone.now()},
            )

        return attempt
