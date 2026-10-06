from rest_framework import serializers

from courses.models import Lesson
from .models import Enrollment, Progress


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    progress_percent = serializers.FloatField(read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            'id', 'student', 'student_email',
            'course', 'course_title',
            'enrolled_at', 'is_active', 'progress_percent',
        )
        read_only_fields = ('id', 'student', 'student_email', 'enrolled_at', 'progress_percent')

    def validate_course(self, course):
        if not course.is_published:
            raise serializers.ValidationError('Курс ещё не опубликован.')
        user = self.context['request'].user
        if Enrollment.objects.filter(student=user, course=course).exists():
            raise serializers.ValidationError('Вы уже записаны на этот курс.')
        return course

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class ProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.module.course.title', read_only=True)

    class Meta:
        model = Progress
        fields = (
            'id', 'student', 'lesson', 'lesson_title', 'course_title',
            'is_completed', 'completed_at',
        )
        read_only_fields = ('id', 'student', 'completed_at')

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)

class ToggleProgressSerializer(serializers.Serializer):
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())
