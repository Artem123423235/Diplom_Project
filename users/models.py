from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Студент'
        TEACHER = 'teacher', 'Преподаватель'
        ADMIN = 'admin', 'Администратор'

    email = models.EmailField('Email', unique=True)
    role = models.CharField('Роль', max_length=20, choices=Role.choices, default=Role.STUDENT)
    full_name = models.CharField('ФИО', max_length=150, blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('О себе', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER
