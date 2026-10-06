from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, LessonViewSet, ModuleViewSet

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='course')
router.register('modules', ModuleViewSet, basename='module')
router.register('lessons', LessonViewSet, basename='lesson')

urlpatterns = router.urls
