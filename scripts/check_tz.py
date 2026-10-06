"""
Скрипт проверки соответствия проекта техзаданию.

Запуск:
    python scripts/check_tz.py

Выводит отчёт: что реализовано, а что нет.
"""

import os
import sys
from pathlib import Path

# --- Django bootstrap ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.apps import apps  # noqa: E402
from django.conf import settings  # noqa: E402
from django.db import connection  # noqa: E402
from django.urls import get_resolver  # noqa: E402

OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"


def header(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def check_section_1_auth() -> None:
    header("1. Авторизация и аутентификация")
    # JWT
    has_jwt_auth = any(
        "JWTAuthentication" in cls
        for cls in settings.REST_FRAMEWORK.get("DEFAULT_AUTHENTICATION_CLASSES", [])
    )
    print(f"{OK if has_jwt_auth else FAIL} JWT в DEFAULT_AUTHENTICATION_CLASSES")

    # IsAuthenticated по умолчанию
    has_is_auth = any(
        "IsAuthenticated" in cls
        for cls in settings.REST_FRAMEWORK.get("DEFAULT_PERMISSION_CLASSES", [])
    )
    print(f"{OK if has_is_auth else WARN} IsAuthenticated по умолчанию")

    # simplejwt в INSTALLED_APPS
    has_simplejwt = "rest_framework_simplejwt" in settings.INSTALLED_APPS
    print(f"{OK if has_simplejwt else FAIL} rest_framework_simplejwt в INSTALLED_APPS")

    # URL регистрации и токенов
    urls = collect_urls()
    print(f"{OK if any('/api/auth/register' in u for u in urls) else FAIL} url /api/auth/register/")
    print(f"{OK if any('/api/auth/token/refresh' in u for u in urls) else FAIL} url /api/auth/token/refresh/")


def check_section_2_content() -> None:
    header("2. Управление контентом")
    model_names = {m._meta.model_name for m in apps.get_models()}
    for name, human in [
        ("course", "Course (курс)"),
        ("section", "Section (раздел)"),
        ("material", "Material (материал)"),
    ]:
        print(f"{OK if name in model_names else FAIL} Модель {human}")

    registered_admin = set(settings.INSTALLED_APPS)
    print(f"{OK if 'django.contrib.admin' in registered_admin else FAIL} Django admin подключён")


def check_section_3_quiz() -> None:
    header("3. Тестирование знаний")
    model_names = {m._meta.model_name for m in apps.get_models()}
    for name, human in [
        ("quiz", "Quiz (тест)"),
        ("question", "Question (вопрос)"),
        ("answer", "Answer (ответ)"),
        ("attempt", "Attempt (попытка)"),
    ]:
        print(f"{OK if name in model_names else FAIL} Модель {human}")

    urls = collect_urls()
    has_submit = any("submit" in u for u in urls)
    print(f"{OK if has_submit else FAIL} URL для проверки ответов (submit)")


def check_section_4_roles() -> None:
    header("4. Роли и права")
    try:
        user_model = apps.get_model("users", "User")
        role_field = user_model._meta.get_field("role")
        choices = dict(role_field.choices or [])
        for role in ("admin", "teacher", "student"):
            print(f"{OK if role in choices else FAIL} Роль '{role}' в User.role")
    except Exception as exc:  # noqa: BLE001
        print(f"{FAIL} Не удалось проверить модель User: {exc}")

    perms = list((BASE_DIR / "users").glob("permissions.py"))
    perms += list((BASE_DIR / "courses").glob("permissions.py"))
    perms += list((BASE_DIR / "learning").glob("permissions.py"))
    perms += list((BASE_DIR / "quizzes").glob("permissions.py"))
    print(f"{OK if perms else WARN} Файлы permissions.py найдено: {len(perms)}")


def check_section_5_tech() -> None:
    header("5. Технические требования")
    print(f"{OK if connection.vendor == 'postgresql' else FAIL} БД: {connection.vendor}")

    has_swagger = any(
        name in ("drf_spectacular", "drf_yasg") for name in settings.INSTALLED_APPS
    )
    print(f"{OK if has_swagger else FAIL} Swagger (drf_spectacular / drf_yasg) в INSTALLED_APPS")

    urls = collect_urls()
    print(f"{OK if any('swagger-ui' in u for u in urls) else FAIL} URL /api/schema/swagger-ui/")

    print(f"{OK if (BASE_DIR / 'README.md').exists() else FAIL} README.md в корне")
    print(f"{OK if (BASE_DIR / 'requirements.txt').exists() else FAIL} requirements.txt")
    print(f"{OK if (BASE_DIR / '.gitignore').exists() else FAIL} .gitignore")
    print(f"{OK if (BASE_DIR / '.env.example').exists() else FAIL} .env.example")

    cors = list(getattr(settings, "CORS_ALLOWED_ORIGINS", []) or [])
    print(f"{OK if cors else WARN} CORS_ALLOWED_ORIGINS: {cors}")
    if getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False):
        print(f"{FAIL} CORS_ALLOW_ALL_ORIGINS=True — небезопасно для production!")


def check_section_6_tests() -> None:
    header("6. Тесты")
    test_files = list(BASE_DIR.rglob("test*.py")) + list(BASE_DIR.rglob("*tests.py"))
    test_files = [p for p in test_files if ".venv" not in p.parts]
    print(f"{OK if test_files else FAIL} Найдено тестовых файлов: {len(test_files)}")
    for p in test_files[:25]:
        print("   ", p.relative_to(BASE_DIR))


def collect_urls() -> list[str]:
    """Собирает все URL-паттерны проекта в список строк."""
    result: list[str] = []

    def walk(patterns, prefix: str = "") -> None:
        for p in patterns:
            if hasattr(p, "url_patterns"):
                walk(p.url_patterns, prefix + str(p.pattern))
            else:
                result.append(prefix + str(p.pattern))

    walk(get_resolver().url_patterns)
    return result


def main() -> None:
    print(f"Проект: {BASE_DIR}")
    print(f"DEBUG:  {settings.DEBUG}")

    check_section_1_auth()
    check_section_2_content()
    check_section_3_quiz()
    check_section_4_roles()
    check_section_5_tech()
    check_section_6_tests()

    header("Готово")
    print("Для полной проверки API открой http://127.0.0.1:8000/api/schema/swagger-ui/")


if __name__ == "__main__":
    main()