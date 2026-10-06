from django.contrib import admin
from django.utils.html import format_html

from .models import Course, Lesson, Module


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('order', 'title')          # VERIFY: если у Lesson есть content/video_url — добавь
    ordering = ('order',)
    show_change_link = True


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ('order', 'title')
    ordering = ('order',)
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'level', 'is_published', 'created_at')
    list_filter = ('level', 'is_published', 'created_at')
    search_fields = ('title', 'description')
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
    inlines = (ModuleInline,)
    list_editable = ('is_published',)
    list_select_related = ('author',)

    # Если у модели Course есть поле description — покажем превью.
    # Если поля нет — эта строка упадёт, удали её.
    def description_preview(self, obj):
        text = getattr(obj, 'description', '') or ''
        return text[:80]
    description_preview.short_description = 'Описание'


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    raw_id_fields = ('course',)
    list_select_related = ('course',)
    inlines = (LessonInline,)
    ordering = ('course', 'order')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order')
    list_filter = ('module__course',)
    search_fields = ('title', 'module__title', 'module__course__title')
    raw_id_fields = ('module',)
    list_select_related = ('module', 'module__course')
    ordering = ('module', 'order')

    def course(self, obj):
        return obj.module.course
    course.short_description = 'Курс'
