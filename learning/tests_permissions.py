from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Course, Lesson, Module

User = get_user_model()


class CoursesPermissionTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='t1', email='t1@x.ru', password='pass', role='teacher')
        self.other = User.objects.create_user(
            username='t2', email='t2@x.ru', password='pass', role='teacher')
        self.student = User.objects.create_user(
            username='s1', email='s1@x.ru', password='pass', role='student')
        self.course = Course.objects.create(
            title='C1', author=self.teacher, is_published=True)
        self.module = Module.objects.create(course=self.course, title='M1', order=1)
        self.lesson = Lesson.objects.create(module=self.module, title='L1', order=1)

    def test_student_cannot_create_course(self):
        self.client.force_authenticate(self.student)
        r = self.client.post('/api/courses/', {'title': 'Hack', 'level': 'beginner'})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_patch_foreign_course(self):
        self.client.force_authenticate(self.student)
        r = self.client.patch(f'/api/courses/{self.course.id}/', {'title': 'X'})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_delete_module(self):
        self.client.force_authenticate(self.student)
        r = self.client.delete(f'/api/modules/{self.module.id}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_delete_lesson(self):
        self.client.force_authenticate(self.student)
        r = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_teacher_cannot_delete_lesson(self):
        self.client.force_authenticate(self.other)
        r = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_patch_own_course(self):
        self.client.force_authenticate(self.teacher)
        r = self.client.patch(f'/api/courses/{self.course.id}/', {'title': 'New'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_author_can_delete_lesson(self):
        self.client.force_authenticate(self.teacher)
        r = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_guest_can_list_courses(self):
        r = self.client.get('/api/courses/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_guest_sees_only_published(self):
        Course.objects.create(title='Draft', author=self.teacher, is_published=False)
        r = self.client.get('/api/courses/')
        titles = [c['title'] for c in r.data['results']] if 'results' in r.data else [c['title'] for c in r.data]
        self.assertIn('C1', titles)
        self.assertNotIn('Draft', titles)
