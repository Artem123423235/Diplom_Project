from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

# надёжный пароль, проходит django-валидаторы (CommonPassword его не знает)
STRONG = "Zx9!Qw2#Fp7"


class AuthTests(APITestCase):
    def test_register(self):
        r = self.client.post('/api/auth/register/', {
            'username': 'new',
            'email': 'new@x.ru',
            'full_name': 'Новый Пользователь',
            'password': STRONG,
            'password2': STRONG,
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.data)
        self.assertTrue(User.objects.filter(email='new@x.ru').exists())

    def test_register_passwords_dont_match(self):
        r = self.client.post('/api/auth/register/', {
            'username': 'new2',
            'email': 'new2@x.ru',
            'password': STRONG,
            'password2': STRONG + 'x',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', r.data)

    def test_register_duplicate_email(self):
        User.objects.create_user(username='u1', email='dup@x.ru', password=STRONG)
        r = self.client.post('/api/auth/register/', {
            'username': 'u2',
            'email': 'dup@x.ru',
            'password': STRONG,
            'password2': STRONG,
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', r.data)

    def test_login_returns_jwt(self):
        # USERNAME_FIELD = email → логинимся email'ом
        User.objects.create_user(username='u', email='u@x.ru', password=STRONG)
        r = self.client.post('/api/auth/token/', {
            'email': 'u@x.ru',
            'password': STRONG,
        })
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)

    def test_me_requires_auth(self):
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        u = User.objects.create_user(username='u', email='u@x.ru', password=STRONG)
        self.client.force_authenticate(u)
        r = self.client.get('/api/auth/me/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['username'], 'u')

    def test_user_cannot_escalate_role(self):
        u = User.objects.create_user(
            username='u', email='u@x.ru', password=STRONG, role='student')
        self.client.force_authenticate(u)
        r = self.client.patch('/api/auth/me/', {'role': 'teacher'})
        # role — read_only, значит либо 200 (поле проигнорировано), либо 400
        self.assertIn(r.status_code, (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST))
        u.refresh_from_db()
        self.assertEqual(u.role, 'student', "Пользователь повысил себе роль!")
