from django.contrib import admin

from .models import Enrollment, Progress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_active', 'progress_percent')
    list_filter = ('is_active', 'enrolled_at', 'course')
    search_fields = ('student__username', 'student__email', 'course__title')
    raw_id_fields = ('student', 'course')
    list_select_related = ('student', 'course')
    date_hierarchy = 'enrolled_at'
    autocomplete_fields = ()          # оставляем пустым, чтобы не требовать search_fields в User/Course админках
    readonly_fields = ('enrolled_at',)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'course_title', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completed_at', 'lesson__module__course')
    search_fields = ('student__username', 'student__email', 'lesson__title')
    raw_id_fields = ('student', 'lesson')
    list_select_related = ('student', 'lesson', 'lesson__module', 'lesson__module__course')
    date_hierarchy = 'completed_at'

    def course_title(self, obj):
        return obj.lesson.module.course.title
    course_title.short_description = 'Курс'
    course_title.admin_order_field = 'lesson__module__course__title'
