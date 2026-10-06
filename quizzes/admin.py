from django.contrib import admin

from .models import Answer, Question, Quiz


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2
    min_num = 2
    # 'order' убран, 'text' + 'is_correct' — по факту есть в модели


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True
    # без 'order' — у Question его нет


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'title')
    list_filter = ('lesson__module__course',)
    search_fields = ('title', 'lesson__title')
    raw_id_fields = ('lesson',)
    list_select_related = ('lesson',)
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_short', 'quiz')
    list_filter = ('quiz__lesson__module__course',)
    search_fields = ('text',)
    raw_id_fields = ('quiz',)
    list_select_related = ('quiz',)
    inlines = (AnswerInline,)

    def text_short(self, obj):
        return (obj.text or '')[:60]
    text_short.short_description = 'Вопрос'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_short', 'question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)
    raw_id_fields = ('question',)
    list_select_related = ('question',)

    def text_short(self, obj):
        return (obj.text or '')[:60]
    text_short.short_description = 'Ответ'
