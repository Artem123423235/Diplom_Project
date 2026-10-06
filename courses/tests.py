from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Course, Lesson, Module

User = get_user_model()

# URL-префиксы. Если у тебя роутер подключён иначе — замени строки (3 шт.).
COURSES_URL = '/api/courses/'
MODULES_URL = '/api/modules/'
LESSONS_URL = '/api/lessons/'


# ─────────────── Базовый класс с фикстурами ───────────────
class BaseCourseTestCase(APITestCase):
    """
    Общие фикстуры: два учителя, студент, админ.
    Учитель №1 — владелец курса и модуля, учитель №2 — «чужой».
    """

    @classmethod
    def setUpTestData(cls):
        cls.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.local',
            password='StrongPass123!',
            role='teacher',
            full_name='Учитель Один',
        )
        cls.other_teacher = User.objects.create_user(
            username='teacher2',
            email='teacher2@test.local',
            password='StrongPass123!',
            role='teacher',
            full_name='Учитель Два',
        )
        cls.student = User.objects.create_user(
            username='student1',
            email='student1@test.local',
            password='StrongPass123!',
            role='student',
            full_name='Студент Один',
        )
        cls.admin = User.objects.create_user(
            username='admin1',
            email='admin1@test.local',
            password='StrongPass123!',
            role='admin',
            full_name='Админ',
        )

        cls.course = Course.objects.create(
            title='Курс учителя 1',
            description='Описание',
            author=cls.teacher,
            is_published=True,
        )
        cls.module = Module.objects.create(
            course=cls.course,
            title='Модуль 1',
            order=1,
        )

    def login(self, user):
        self.client.force_authenticate(user=user)

    def logout(self):
        self.client.force_authenticate(user=None)


# ─────────────── Создание курса (роли) ───────────────
class CourseCreateTests(BaseCourseTestCase):

    def test_anonymous_cannot_create(self):
        resp = self.client.post(COURSES_URL, {'title': 'X'})
        self.assertIn(
            resp.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_student_cannot_create(self):
        self.login(self.student)
        resp = self.client.post(COURSES_URL, {
            'title': 'X', 'description': 'Y',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create(self):
        self.login(self.teacher)
        resp = self.client.post(COURSES_URL, {
            'title': 'Новый курс', 'description': 'Y',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        course = Course.objects.get(pk=resp.data['id'])
        self.assertEqual(course.author, self.teacher)

    def test_admin_can_create(self):
        self.login(self.admin)
        resp = self.client.post(COURSES_URL, {
            'title': 'Курс админа', 'description': 'Y',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(
            Course.objects.get(pk=resp.data['id']).author,
            self.admin,
        )

    def test_author_cannot_be_spoofed(self):
        """Попытка передать чужого автора игнорируется — author из request.user."""
        self.login(self.teacher)
        resp = self.client.post(COURSES_URL, {
            'title': 'X',
            'author': self.other_teacher.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.assertEqual(
            Course.objects.get(pk=resp.data['id']).author,
            self.teacher,
        )


# ─────────────── Чтение курсов ───────────────
class CourseReadTests(BaseCourseTestCase):

    def test_list_is_public(self):
        resp = self.client.get(COURSES_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_detail_contains_modules_and_lessons(self):
        """Ключевое требование ТЗ: курс -> модули -> уроки."""
        Lesson.objects.create(module=self.module, title='Урок 1', order=1)
        resp = self.client.get(f'{COURSES_URL}{self.course.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('modules', resp.data)
        self.assertEqual(len(resp.data['modules']), 1)
        self.assertEqual(len(resp.data['modules'][0]['lessons']), 1)
        self.assertEqual(resp.data['modules'][0]['lessons'][0]['title'], 'Урок 1')

    def test_author_name_falls_back_to_username(self):
        """Если full_name пуст — author_name = username."""
        u = User.objects.create_user(
            username='noname',
            email='noname@test.local',
            password='StrongPass123!',
            role='teacher',
            full_name='',
        )
        course = Course.objects.create(
            title='К', author=u, is_published=True,
        )
        resp = self.client.get(f'{COURSES_URL}{course.id}/')
        self.assertEqual(resp.data['author_name'], 'noname')


# ─────────────── Обновление / удаление курса ───────────────
class CourseUpdateDeleteTests(BaseCourseTestCase):

    def test_teacher_updates_own_course(self):
        self.login(self.teacher)
        resp = self.client.patch(
            f'{COURSES_URL}{self.course.id}/',
            {'title': 'Обновлённый'},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Обновлённый')

    def test_teacher_cannot_update_foreign_course(self):
        self.login(self.other_teacher)
        resp = self.client.patch(
            f'{COURSES_URL}{self.course.id}/',
            {'title': 'Хак'},
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Курс учителя 1')

    def test_admin_can_update_foreign_course(self):
        self.login(self.admin)
        resp = self.client.patch(
            f'{COURSES_URL}{self.course.id}/',
            {'title': 'Правка админа'},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)

    def test_teacher_deletes_own_course(self):
        self.login(self.teacher)
        resp = self.client.delete(f'{COURSES_URL}{self.course.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course.id).exists())

    def test_teacher_cannot_delete_foreign_course(self):
        self.login(self.other_teacher)
        resp = self.client.delete(f'{COURSES_URL}{self.course.id}/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Course.objects.filter(pk=self.course.id).exists())


# ─────────────── Модуль: границы владения ───────────────
class ModuleBoundaryTests(BaseCourseTestCase):
    """Модуль можно создать только в СВОЁМ курсе (см. validate_course)."""

    def test_teacher_creates_module_in_own_course(self):
        self.login(self.teacher)
        resp = self.client.post(MODULES_URL, {
            'course': self.course.id,
            'title': 'Модуль 2',
            'order': 2,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

    def test_teacher_cannot_create_module_in_foreign_course(self):
        foreign = Course.objects.create(
            title='Чужой', author=self.other_teacher, is_published=True,
        )
        self.login(self.teacher)
        resp = self.client.post(MODULES_URL, {
            'course': foreign.id,
            'title': 'Хак',
            'order': 1,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, resp.data)
        self.assertEqual(Module.objects.filter(course=foreign).count(), 0)

    def test_student_cannot_create_module(self):
        self.login(self.student)
        resp = self.client.post(MODULES_URL, {
            'course': self.course.id,
            'title': 'Хак',
            'order': 99,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_move_module_to_foreign_course(self):
        """PATCH-обход: попытка перенести СВОЙ модуль в ЧУЖОЙ курс."""
        foreign = Course.objects.create(
            title='Чужой', author=self.other_teacher, is_published=True,
        )
        self.login(self.teacher)
        resp = self.client.patch(
            f'{MODULES_URL}{self.module.id}/',
            {'course': foreign.id},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, resp.data)
        self.module.refresh_from_db()
        self.assertEqual(self.module.course_id, self.course.id)


# ─────────────── Урок: границы владения ───────────────
class LessonBoundaryTests(BaseCourseTestCase):
    """Урок можно создать только в модуле СВОЕГО курса (см. validate_module)."""

    def test_teacher_creates_lesson_in_own_module(self):
        self.login(self.teacher)
        resp = self.client.post(LESSONS_URL, {
            'module': self.module.id,
            'title': 'Урок 1',
            'order': 1,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

    def test_teacher_cannot_create_lesson_in_foreign_module(self):
        foreign_course = Course.objects.create(
            title='Чужой', author=self.other_teacher, is_published=True,
        )
        foreign_module = Module.objects.create(
            course=foreign_course, title='M', order=1,
        )
        self.login(self.teacher)
        resp = self.client.post(LESSONS_URL, {
            'module': foreign_module.id,
            'title': 'Хак',
            'order': 1,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, resp.data)
        self.assertEqual(Lesson.objects.filter(module=foreign_module).count(), 0)

    def test_student_cannot_create_lesson(self):
        self.login(self.student)
        resp = self.client.post(LESSONS_URL, {
            'module': self.module.id,
            'title': 'Хак',
            'order': 1,
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
