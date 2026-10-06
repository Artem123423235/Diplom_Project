from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from courses.models import Course, Lesson
from learning.models import Enrollment, Progress

User = get_user_model()

print("=== SETUP ===")
User.objects.filter(username="test_lrn").delete()
student = User.objects.create_user(
    username="test_lrn", password="TestPass123!", role="student",
)
print("student id =", student.id)

course = None
for c in Course.objects.filter(is_published=True):
    if Lesson.objects.filter(module__course=c).exists():
        course = c
        break

if course is None:
    print("!! NO published course with lessons found. Create one via admin first.")
else:
    lesson = Lesson.objects.filter(module__course=course).first()
    print("course:", course.id, repr(course.title))
    print("lesson:", lesson.id, repr(lesson.title))

    client = APIClient()
    refresh = RefreshToken.for_user(student)
    client.credentials(HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token))

    def show(label, resp):
        try:
            body = resp.data
        except Exception:
            body = resp.content[:200]
        print(label, "->", resp.status_code, body)

    show("1. enroll        ", client.post("/api/v1/courses/" + str(course.id) + "/enroll/"))
    show("2. enroll again  ", client.post("/api/v1/courses/" + str(course.id) + "/enroll/"))
    show("3. toggle ON     ", client.post("/api/v1/progress/toggle/", {"lesson": lesson.id}, format="json"))
    show("4. enrollments   ", client.get("/api/v1/enrollments/"))
    show("5. toggle OFF    ", client.post("/api/v1/progress/toggle/", {"lesson": lesson.id}, format="json"))
    show("6. progress list ", client.get("/api/v1/progress/"))

    Progress.objects.filter(student=student).delete()
    Enrollment.objects.filter(student=student).delete()

student.delete()
print("=== DONE ===")
