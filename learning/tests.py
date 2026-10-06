from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, Lesson, Module
from learning.models import Enrollment, Progress


User = get_user_model()


class LearningApiTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='test_student',
            email='student@example.com',
            password='TestPass123!',
            role='student',
        )

        self.course = Course.objects.create(
            title='Test course',
            description='Course for API tests',
            author=self.student,
            is_published=True,
        )
        self.module = Module.objects.create(
            course=self.course,
            title='Test module',
            order=1,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Test lesson',
            order=1,
        )

        self.client.force_authenticate(user=self.student)

    def test_student_can_enroll_in_course(self):
        response = self.client.post(
            f'/api/courses/{self.course.id}/enroll/'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Enrollment.objects.filter(
                student=self.student,
                course=self.course,
            ).exists()
        )

    def test_duplicate_enrollment_is_rejected(self):
        self.client.post(f'/api/courses/{self.course.id}/enroll/')

        response = self.client.post(
            f'/api/courses/{self.course.id}/enroll/'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            Enrollment.objects.filter(
                student=self.student,
                course=self.course,
            ).count(),
            1,
        )

    def test_student_can_toggle_lesson_progress(self):
        self.client.post(f'/api/courses/{self.course.id}/enroll/')

        first_response = self.client.post(
            '/api/progress/toggle/',
            {'lesson': self.lesson.id},
            format='json',
        )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertTrue(first_response.data['is_completed'])
        self.assertEqual(
            Progress.objects.get(
                student=self.student,
                lesson=self.lesson,
            ).is_completed,
            True,
        )

        second_response = self.client.post(
            '/api/progress/toggle/',
            {'lesson': self.lesson.id},
            format='json',
        )

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertFalse(second_response.data['is_completed'])

    def test_student_must_enroll_before_toggling_progress(self):
        response = self.client.post(
            '/api/progress/toggle/',
            {'lesson': self.lesson.id},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertFalse(
            Progress.objects.filter(
                student=self.student,
                lesson=self.lesson,
            ).exists()
        )
