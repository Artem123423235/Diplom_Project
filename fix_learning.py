from django.db import connection

tables = [
    'learning_progress', 'learning_enrollment',
    'learning_quiz', 'learning_question', 'learning_choice',
    'learning_attempt', 'learning_answer',
]
with connection.cursor() as c:
    c.execute("DELETE FROM django_migrations WHERE app='learning'")
    print('django_migrations deleted:', c.rowcount)
    for t in tables:
        c.execute(f'DROP TABLE IF EXISTS {t} CASCADE')
        print('dropped table:', t)

print('DONE')
