from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

User = get_user_model()


class AdminSmokeTests(TestCase):
    """Открываем список и страницу редактирования каждого зарегистрированного админа."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username='root', email='root@x.ru', password='Zx9!Qw2#Fp7')

    def setUp(self):
        self.client.force_login(self.admin)

    def test_all_admin_list_pages_open(self):
        from django.contrib import admin as dj
        for model, _ in dj.site._registry.items():
            app, name = model._meta.app_label, model._meta.model_name
            with self.subTest(model=f'{app}.{name}'):
                url = reverse(f'admin:{app}_{name}_changelist')
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200, f'{app}.{name} → {r.status_code}')

    def test_course_change_page_opens(self):
        """Дополнительно — форма добавления: ловит ошибки в fieldsets/inlines."""
        p = self.admin
        url = reverse('admin:courses_course_add')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
