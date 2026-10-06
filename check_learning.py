from django.db import connection
with connection.cursor() as c:
    for t in ("learning_enrollment", "learning_progress"):
        c.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name=%s ORDER BY ordinal_position", [t]
        )
        print(t, "->", [r[0] for r in c.fetchall()])
