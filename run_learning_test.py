from django.conf import settings
settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "testserver"]

from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson
import uuid

User = get_user_model()

if User.objects.filter(username="test_lrn").exists():
    raise RuntimeError("Пользователь test_lrn уже существует; тест остановлен.")

author = User.objects.first()
created_author = False

if author is None:
    author = User.objects.create_user(
        username="tmp_lrn_author",
        password="TempPass123!",
        role="teacher",
    )
    created_author = True

course = Course.objects.create(
    title=f"API test course {uuid.uuid4().hex[:8]}",
    author=author,
    is_published=True,
)
module = Module.objects.create(course=course, title="API test module")
Lesson.objects.create(module=module, title="API test lesson")

print("Temporary course:", course.id)

try:
    script = open("test_learning.py", encoding="utf-8-sig").read()
    exec(compile(script, "test_learning.py", "exec"))
finally:
    User.objects.filter(username="test_lrn").delete()
    course.delete()
    if created_author:
        author.delete()
    print("Temporary test data cleaned up.")
