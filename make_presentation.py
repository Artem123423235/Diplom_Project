# -*- coding: utf-8 -*-
"""
Генератор презентации к защите дипломного проекта.
Создаёт файл: Diplom_Presentation.pptx

Установка:  pip install python-pptx
Запуск:     python make_presentation.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


# ============================================================
# ПАЛИТРА (меняй тут, если хочется другой цвет)
# ============================================================
DARK_BLUE  = RGBColor(0x1F, 0x3A, 0x5F)
BLUE       = RGBColor(0x2E, 0x86, 0xAB)
GREEN      = RGBColor(0x27, 0xAE, 0x60)
ORANGE     = RGBColor(0xE6, 0x7E, 0x22)
RED        = RGBColor(0xC0, 0x39, 0x2B)
GRAY_DARK  = RGBColor(0x33, 0x33, 0x33)
GRAY_MED   = RGBColor(0x66, 0x66, 0x66)
GRAY_LIGHT = RGBColor(0xEE, 0xF1, 0xF4)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)


# ============================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


# ============================================================
# ХЕЛПЕРЫ
# ============================================================
def new_slide():
    return prs.slides.add_slide(BLANK)


def textbox(slide, left, top, width, height):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    return tf


def set_para(p, text, size=22, bold=False, italic=False,
             color=GRAY_DARK, align=PP_ALIGN.LEFT, space_after=12):
    p.text = text
    p.alignment = align
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.italic = italic
    p.font.color.rgb = color
    p.font.name = 'Calibri'
    p.space_after = Pt(space_after)
    return p


def add_title_bar(slide, title_text, subtitle=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                                 prs.slide_width, Inches(1.15))
    bar.fill.solid()
    bar.fill.fore_color.rgb = DARK_BLUE
    bar.line.fill.background()
    bar.shadow.inherit = False

    tf = textbox(slide, Inches(0.6), Inches(0.1),
                 prs.slide_width - Inches(1.2), Inches(0.95))
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    set_para(tf.paragraphs[0], title_text, size=32, bold=True,
             color=WHITE, space_after=0)

    if subtitle:
        tf2 = textbox(slide, Inches(0.6), Inches(1.25),
                      prs.slide_width - Inches(1.2), Inches(0.4))
        set_para(tf2.paragraphs[0], subtitle, size=15, italic=True,
                 color=GRAY_MED, space_after=0)


def add_bullets(slide, items, left=Inches(0.7), top=Inches(1.9),
                width=None, height=Inches(5.2), size=22, space=16):
    if width is None:
        width = prs.slide_width - Inches(1.4)
    tf = textbox(slide, left, top, width, height)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        set_para(p, item, size=size, space_after=space)


def add_rounded_box(slide, left, top, width, height, fill_color,
                    text_lines, text_color=WHITE, font_size=18, bold=False):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = fill_color
    box.line.fill.background()
    box.shadow.inherit = False

    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.1)
    tf.margin_bottom = Inches(0.1)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    for i, line in enumerate(text_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        set_para(p, line, size=font_size, bold=bold,
                 color=text_color, align=PP_ALIGN.CENTER, space_after=4)
    return box


# ============================================================
# СЛАЙД 1 — Титульный
# ============================================================
s = new_slide()
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(4.2))
band.fill.solid(); band.fill.fore_color.rgb = DARK_BLUE
band.line.fill.background(); band.shadow.inherit = False

tf = textbox(s, Inches(1), Inches(1.2), prs.slide_width - Inches(2), Inches(2))
set_para(tf.paragraphs[0], "Backend-платформа", size=44, bold=True,
         color=WHITE, space_after=6)
p = tf.add_paragraph()
set_para(p, "для управления онлайн-обучением", size=30, color=WHITE, space_after=20)
p = tf.add_paragraph()
set_para(p, "Дипломный проект", size=20, italic=True,
         color=RGBColor(0xBB, 0xD0, 0xE6), space_after=0)

tf2 = textbox(s, Inches(1), Inches(4.7), prs.slide_width - Inches(2), Inches(2.5))
set_para(tf2.paragraphs[0], "ФИО студента", size=22, bold=True,
         color=GRAY_DARK, space_after=8)
for line in ["Группа: ___________",
             "Научный руководитель: ___________",
             "Город, 2025"]:
    p = tf2.add_paragraph()
    set_para(p, line, size=18, color=GRAY_MED, space_after=8)


# ============================================================
# СЛАЙД 2 — Проблема
# ============================================================
s = new_slide()
add_title_bar(s, "Проблема")
add_bullets(s, [
    "•  Учебные центры и репетиторы ведут обучение в чатах и таблицах",
    "•  Домашки теряются, тесты проверяются вручную",
    "•  Прогресс ученика никто не отслеживает — «кто что прошёл» непонятно",
    "•  Готовые LMS (например, Moodle) — тяжёлые и избыточные для небольшой школы",
], top=Inches(1.8), size=22, space=22)


# ============================================================
# СЛАЙД 3 — Что я предлагаю
# ============================================================
s = new_slide()
add_title_bar(s, "Что я предлагаю")

tf = textbox(s, Inches(0.7), Inches(1.7), Inches(6.3), Inches(5))
set_para(tf.paragraphs[0], "•  Компактная backend-платформа", size=20,
         bold=True, space_after=14)
for t in [
    "•  Не сайт, а API — можно подключить любой интерфейс",
    "•  Три роли с разными правами",
    "     студент / преподаватель / администратор",
    "•  Каждый работает только со своим",
    "•  Легко разворачивается на любом сервере",
]:
    p = tf.add_paragraph()
    set_para(p, t, size=20, space_after=14)

# Схема справа
x0, y0 = Inches(7.4), Inches(2.0)
add_rounded_box(s, x0,              y0, Inches(1.65), Inches(0.75), BLUE, ["Веб-сайт"],  font_size=14)
add_rounded_box(s, x0 + Inches(1.85), y0, Inches(1.65), Inches(0.75), BLUE, ["Мобильное"], font_size=14)
add_rounded_box(s, x0 + Inches(3.7),  y0, Inches(1.65), Inches(0.75), BLUE, ["Сервис"],    font_size=14)

add_rounded_box(s, x0, Inches(3.7), Inches(5.35), Inches(1.7), DARK_BLUE,
                ["Мой API", "(backend на Django)"], font_size=22, bold=True)

capt = textbox(s, x0, Inches(5.7), Inches(5.35), Inches(0.5))
set_para(capt.paragraphs[0], "Логика обучения — на сервере",
         size=14, italic=True, color=GRAY_MED,
         align=PP_ALIGN.CENTER, space_after=0)


# ============================================================
# СЛАЙД 4 — Главные тезисы (из ТЗ)
# ============================================================
s = new_slide()
add_title_bar(s, "Главные тезисы (из ТЗ)")
add_bullets(s, [
    "•  Хранение учебного контента:  курс → модуль → урок",
    "•  Тесты:  тест → вопрос → вариант ответа",
    "•  Запись студента на курс и отслеживание прогресса",
    "•  Разграничение прав доступа на уровне сервера",
    "•  Автодокументация API через Swagger",
], top=Inches(1.9), size=24, space=24)


# ============================================================
# СЛАЙД 5 — Стек технологий (таблица)
# ============================================================
s = new_slide()
add_title_bar(s, "Стек технологий")

rows = [
    ("Слой",         "Технология",                  "Зачем выбрана"),
    ("Язык",         "Python 3.11",                 "Основной стек"),
    ("Фреймворк",    "Django 5",                    "ORM, админка, миграции из коробки"),
    ("API",          "Django REST Framework",       "Стандарт для REST API на Python"),
    ("Авторизация",  "SimpleJWT",                   "Токены вместо сессий"),
    ("База данных",  "PostgreSQL (SQLite в dev)",   "Надёжность в продакшене"),
    ("Документация", "drf-spectacular",             "Swagger генерируется из кода"),
]
tbl_shape = s.shapes.add_table(len(rows), 3, Inches(0.7), Inches(1.7),
                               prs.slide_width - Inches(1.4), Inches(5))
table = tbl_shape.table
table.columns[0].width = Inches(2.3)
table.columns[1].width = Inches(4.0)
table.columns[2].width = Inches(5.6)

for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = table.cell(r, c)
        cell.text = val
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(18 if r == 0 else 16)
            p.font.bold = (r == 0)
            p.font.name = 'Calibri'
            p.font.color.rgb = WHITE if r == 0 else GRAY_DARK
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE if r == 0 else (GRAY_LIGHT if r % 2 == 0 else WHITE)


# ============================================================
# СЛАЙД 6 — Архитектура проекта
# ============================================================
s = new_slide()
add_title_bar(s, "Архитектура проекта",
              "Проект разбит по смыслу, а не по слоям")

apps = [
    ("users",    ["User", "Роли", "JWT-вход"],                     BLUE),
    ("courses",  ["Course", "Module", "Lesson"],                   DARK_BLUE),
    ("learning", ["Enrollment", "Progress"],                       GREEN),
    ("quizzes",  ["Quiz", "Question", "Answer", "Attempt"],        ORANGE),
]
box_w = Inches(2.9)
gap   = Inches(0.35)
total = box_w * 4 + gap * 3
left0 = int((prs.slide_width - total) / 2)

for i, (name, items, color) in enumerate(apps):
    x = left0 + int((box_w + gap) * i)
    add_rounded_box(s, x, Inches(1.9),  box_w, Inches(0.85), color,
                    [name], font_size=20, bold=True)
    add_rounded_box(s, x, Inches(2.9),  box_w, Inches(2.8), GRAY_LIGHT,
                    items, text_color=GRAY_DARK, font_size=17)

# Подпись снизу
tf = textbox(s, Inches(0.7), Inches(6.1), prs.slide_width - Inches(1.4), Inches(0.6))
set_para(tf.paragraphs[0], "Контент — слева, активность студента — справа, тесты — отдельно",
         size=14, italic=True, color=GRAY_MED, align=PP_ALIGN.CENTER, space_after=0)


# ============================================================
# СЛАЙД 7 — Контент vs Активность
# ============================================================
s = new_slide()
add_title_bar(s, "Ключевое архитектурное решение",
              "Контент и активность студента живут в разных моделях")

# Левая колонка — Контент
add_rounded_box(s, Inches(0.8), Inches(1.9), Inches(5.6), Inches(0.7),
                BLUE, ["КОНТЕНТ — что учить"], font_size=18, bold=True)
tf = textbox(s, Inches(0.8), Inches(2.8), Inches(5.6), Inches(3.5))
set_para(tf.paragraphs[0], "Course → Module → Lesson",
         size=20, bold=True, color=GRAY_DARK, space_after=10)
p = tf.add_paragraph()
set_para(p, "Quiz → Question → Answer",
         size=20, bold=True, color=GRAY_DARK, space_after=16)
p = tf.add_paragraph()
set_para(p, "Живут в приложениях courses и quizzes",
         size=14, italic=True, color=GRAY_MED, space_after=0)

# Разделитель
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.66), Inches(1.9),
                          Inches(0.02), Inches(4.6))
line.fill.solid(); line.fill.fore_color.rgb = GRAY_LIGHT
line.line.fill.background(); line.shadow.inherit = False

# Правая колонка — Активность
add_rounded_box(s, Inches(6.95), Inches(1.9), Inches(5.6), Inches(0.7),
                GREEN, ["АКТИВНОСТЬ — кто что сделал"], font_size=18, bold=True)
tf = textbox(s, Inches(6.95), Inches(2.8), Inches(5.6), Inches(3.5))
set_para(tf.paragraphs[0], "Enrollment — запись на курс",
         size=18, color=GRAY_DARK, space_after=10)
p = tf.add_paragraph()
set_para(p, "Progress — пройденные уроки",
         size=18, color=GRAY_DARK, space_after=10)
p = tf.add_paragraph()
set_para(p, "Attempt — попытки сдать тест",
         size=18, color=GRAY_DARK, space_after=16)
p = tf.add_paragraph()
set_para(p, "Живут в приложении learning",
         size=14, italic=True, color=GRAY_MED, space_after=0)

# Баннер снизу
add_rounded_box(s, Inches(0.8), Inches(6.4), Inches(11.7), Inches(0.7),
                DARK_BLUE,
                ["Если структура курсов изменится — история обучения студентов не сломается"],
                font_size=15, bold=True)


# ============================================================
# СЛАЙД 8 — Права доступа
# ============================================================
s = new_slide()
add_title_bar(s, "Права доступа",
              "Работает на уровне сервера, а не в интерфейсе")

chain = ["Тест", "Урок", "Модуль", "Курс", "Автор"]
box_w = Inches(2.0)
gap   = Inches(0.35)
total = box_w * 5 + gap * 4
left0 = int((prs.slide_width - total) / 2)

for i, name in enumerate(chain):
    x = left0 + int((box_w + gap) * i)
    color = GREEN if name == "Автор" else BLUE
    add_rounded_box(s, x, Inches(2.0), box_w, Inches(0.9),
                    color, [name], font_size=18, bold=True)
    if i < 4:
        arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                                 x + box_w + Inches(0.03), Inches(2.3),
                                 Inches(0.29), Inches(0.3))
        arr.fill.solid(); arr.fill.fore_color.rgb = GRAY_MED
        arr.line.fill.background(); arr.shadow.inherit = False

# Три правила
cyan_y = Inches(3.8)
add_rounded_box(s, Inches(0.8), cyan_y, Inches(3.7), Inches(1.5),
                GRAY_LIGHT, ["ЧИТАТЬ", "любой авторизованный"],
                text_color=GRAY_DARK, font_size=18)
add_rounded_box(s, Inches(4.83), cyan_y, Inches(3.7), Inches(1.5),
                GRAY_LIGHT, ["МЕНЯТЬ", "только автор или админ"],
                text_color=GRAY_DARK, font_size=18)
add_rounded_box(s, Inches(8.85), cyan_y, Inches(3.7), Inches(1.5),
                RED, ["ЧУЖОЕ", "ответ 403 Forbidden"], font_size=18)

# Пояснение
tf = textbox(s, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.5))
set_para(tf.paragraphs[0],
         "Чтобы проверить права на тест, сервер пробегает всю цепочку наверх:",
         size=15, color=GRAY_MED, space_after=6)
p = tf.add_paragraph()
set_para(p, "Тест → Урок → Модуль → Курс → автор",
         size=20, bold=True, color=DARK_BLUE, space_after=8)
p = tf.add_paragraph()
set_para(p, "Спрятанную кнопку обходят за секунду — отказ сервера обойти нельзя.",
         size=15, italic=True, color=GRAY_DARK, space_after=0)


# ============================================================
# СЛАЙД 9 — ДЕМО: Swagger UI (вставь скриншот)
# ============================================================
s = new_slide()
add_title_bar(s, "Живая демонстрация — Swagger UI")

ph = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6),
                        prs.slide_width - Inches(1.6), Inches(5.0))
ph.fill.solid(); ph.fill.fore_color.rgb = RGBColor(0xE8, 0xEE, 0xF3)
ph.line.color.rgb = BLUE; ph.line.width = Pt(2)
ph.shadow.inherit = False

tf = ph.text_frame
tf.word_wrap = True
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
set_para(tf.paragraphs[0], "Скриншот Swagger UI",
         size=32, bold=True, color=BLUE,
         align=PP_ALIGN.CENTER, space_after=14)
p = tf.add_paragraph()
set_para(p, "http://127.0.0.1:8000/api/schema/swagger-ui/",
         size=18, color=GRAY_MED, align=PP_ALIGN.CENTER, space_after=8)
p = tf.add_paragraph()
set_para(p, "(вставь сюда картинку перед защитой — правый клик → «Изменить рисунок»)",
         size=13, italic=True, color=GRAY_MED,
         align=PP_ALIGN.CENTER, space_after=0)


# ============================================================
# СЛАЙД 10 — Что показывает демо
# ============================================================
s = new_slide()
add_title_bar(s, "Что показывает демонстрация")
add_bullets(s, [
    "•  Полный набор операций по 8 ресурсам:",
    "     courses · modules · lessons · enrollments ·",
    "     progress · quizzes · questions · attempts",
    "•  Права работают: чужой объект — 403, свой — 200",
    "•  Пагинация: отдаём по 20 записей, а не всю базу",
    "•  Вложенность: у урока есть ссылка на модуль, у модуля — на курс",
    "•  Автодокументация: Swagger строится прямо из кода",
], top=Inches(1.8), size=20, space=16)


# ============================================================
# СЛАЙД 11 — Результаты тестирования
# ============================================================
s = new_slide()
add_title_bar(s, "Результаты тестирования")

# Левая колонка — списки
tf = textbox(s, Inches(0.7), Inches(1.7), Inches(5.7), Inches(5.3))
set_para(tf.paragraphs[0], "Проверено:", size=22, bold=True,
         color=DARK_BLUE, space_after=14)
for t in [
    "✓  python manage.py check — без замечаний",
    "✓  Сквозной smoke-тест API — 7 запросов",
    "✓  Миграции с чистой базы — без конфликтов",
]:
    p = tf.add_paragraph()
    set_para(p, t, size=17, color=GREEN, space_after=10)

p = tf.add_paragraph(); set_para(p, "", size=8, space_after=14)
p = tf.add_paragraph()
set_para(p, "Не покрыто (в планах после защиты):",
         size=18, bold=True, color=DARK_BLUE, space_after=12)
for t in [
    "−  Юнит-тесты логики моделей",
    "−  Нагрузочное тестирование",
]:
    p = tf.add_paragraph()
    set_para(p, t, size=17, color=ORANGE, space_after=10)

# Правая колонка — терминал
term = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.9), Inches(1.7),
                          Inches(5.7), Inches(5.3))
term.fill.solid(); term.fill.fore_color.rgb = RGBColor(0x1E, 0x1E, 0x1E)
term.line.fill.background(); term.shadow.inherit = False

tf2 = term.text_frame
tf2.word_wrap = True
tf2.margin_left = Inches(0.3); tf2.margin_right = Inches(0.3)
tf2.margin_top = Inches(0.3);  tf2.margin_bottom = Inches(0.3)

terminal_lines = [
    "LOGIN:                 200  ✓",
    "GET /api/courses/      200  → count: 3",
    "GET /api/modules/      200  → count: 6",
    "GET /api/lessons/      200  → count: 18",
    "GET /api/quizzes/      200  → count: 9",
    "GET /api/progress/     200  → count: 18",
    "PATCH /api/modules/1/  200  ✓ (автор)",
]
for i, line in enumerate(terminal_lines):
    p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
    set_para(p, line, size=14,
             color=RGBColor(0x33, 0xFF, 0x66), space_after=10)
    p.font.name = 'Consolas'


# ============================================================
# СЛАЙД 12 — Бизнес-ценность
# ============================================================
s = new_slide()
add_title_bar(s, "Бизнес-ценность")

items = [
    ("Экономия времени",   "Тесты проверяются\nавтоматически,\nпрогресс считается сам",     BLUE),
    ("Прозрачность",       "Родитель или руководитель\nвидит реальную картину,\nа не пересказ", GREEN),
    ("Задел под продукт",  "Из этой базы можно\nсделать платную подписку\nза 2–3 итерации",        ORANGE),
]
box_w = Inches(3.8)
gap   = Inches(0.35)
total = box_w * 3 + gap * 2
left0 = int((prs.slide_width - total) / 2)

for i, (title, desc, color) in enumerate(items):
    x = left0 + int((box_w + gap) * i)
    add_rounded_box(s, x, Inches(2.2),  box_w, Inches(0.9),
                    color, [title], font_size=20, bold=True)
    add_rounded_box(s, x, Inches(3.25), box_w, Inches(2.6),
                    GRAY_LIGHT, desc.split('\n'),
                    text_color=GRAY_DARK, font_size=16)


# ============================================================
# СЛАЙД 13 — Итоги и планы
# ============================================================
s = new_slide()
add_title_bar(s, "Итоги и планы")

tf = textbox(s, Inches(0.7), Inches(1.7), Inches(6), Inches(5.3))
set_para(tf.paragraphs[0], "Что сделано:", size=22, bold=True,
         color=DARK_BLUE, space_after=14)
for t in [
    "✓  Backend на Django REST Framework",
    "✓  10 моделей в 4 приложениях",
    "✓  27 эндпоинтов API",
    "✓  Роли, права, JWT-аутентификация",
    "✓  Swagger — автодокументация",
    "✓  Наполнение БД одной командой",
]:
    p = tf.add_paragraph()
    set_para(p, t, size=16, space_after=9)

tf2 = textbox(s, Inches(7), Inches(1.7), Inches(5.7), Inches(5.3))
set_para(tf2.paragraphs[0], "Планы на будущее:", size=22, bold=True,
         color=DARK_BLUE, space_after=14)
for t in [
    "•  Юнит-тесты и нагрузочное тестирование",
    "•  Хранение видеоуроков",
    "•  Оплата курсов",
    "•  Аналитика для преподавателя",
    "•  Frontend и мобильное приложение",
]:
    p = tf2.add_paragraph()
    set_para(p, t, size=16, space_after=9)

tf3 = textbox(s, Inches(0.7), Inches(6.7),
              prs.slide_width - Inches(1.4), Inches(0.6))
set_para(tf3.paragraphs[0],
         "Спасибо за внимание! Готов ответить на вопросы.",
         size=20, bold=True, color=DARK_BLUE,
         align=PP_ALIGN.CENTER, space_after=0)


# ============================================================
# СОХРАНЕНИЕ
# ============================================================
FILE = 'Diplom_Presentation.pptx'
prs.save(FILE)
print(f"Готово! Файл создан: {FILE}")
print(f"Слайдов: {len(prs.slides)}")
print("Открой его в PowerPoint и вставь скриншот на слайд 9.")
