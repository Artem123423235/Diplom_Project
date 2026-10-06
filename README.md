# Diplom Project — платформа онлайн-обучения

Django 5 + DRF + JWT. Курсы, модули, уроки, тесты, прогресс студентов.

## Стек

- Python 3.12 / Django 5
- Django REST Framework + SimpleJWT
- drf-spectacular (Swagger/OpenAPI)
- django-filter
- SQLite (учебная БД)

## Быстрый старт

```bash
git clone <repo-url>
cd Diplom_Project

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
pip install python-dotenv

cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# вставь вывод в .env → DJANGO_SECRET_KEY

python manage.py migrate
python manage.py seed        # демо-данные
python manage.py runserver
```

## Демо-доступы (после `seed`)

| Роль | Логин | Пароль |
|---|---|---|
| Админ | `admin` | `Zx9!Qw2#Fp7` |
| Преподаватель | `teacher1` | `Zx9!Qw2#Fp7` |
| Преподаватель | `teacher2` | `Zx9!Qw2#Fp7` |
| Студент | `student1` .. `student5` | `Zx9!Qw2#Fp7` |

> Email логин: `<username>@example.com` (USERNAME_FIELD = email, но serializer принимает `email` как логин).

## API

| Метод | URL | Описание |
|---|---|---|
| POST | `/api/auth/register/` | Регистрация |
| POST | `/api/auth/token/` | JWT по `email` + `password` |
| POST | `/api/auth/token/refresh/` | Обновление access |
| GET/PATCH | `/api/auth/me/` | Профиль |
| GET | `/api/courses/` | Список курсов (`?level=`, `?search=`, `?ordering=`) |
| GET | `/api/courses/{id}/` | Детали курса |
| GET | `/api/modules/` | Модули |
| GET | `/api/lessons/` | Уроки |
| POST | `/api/courses/{id}/enroll/` | Запись на курс |
| GET | `/api/enrollments/` | Мои записи |
| GET/POST | `/api/progress/` | Прогресс |
| GET/POST | `/api/attempts/` | Попытки тестов |

Swagger: `http://127.0.0.1:8000/api/docs/`
OpenAPI JSON: `http://127.0.0.1:8000/api/schema/`

## Тесты

```bash
python manage.py test -v 2
```

## Структура

```
config/      — настройки, корневые urls
users/       — кастомный User, auth, JWT
courses/     — Course / Module / Lesson
learning/    — Enrollment / Progress
quizzes/     — Quiz / Question / Answer / Attempt
```
