# api/models/__init__.py

"""
Главный файл экспорта всех моделей.
"""

# --- Пользователи и роли
from .users.users           import Role, User, UserManager

# --- Каталог: программы, курсы и модули
from .courses.programs      import Program
from .courses.courses       import Course
from .courses.modules       import Module
from .courses.files         import File

# --- Оценивания: тесты, вопросы, попытки
from .assessments.tests     import Test
from .assessments.questions import Question
from .assessments.attempts  import TestAttempt, ExamAttempt

# --- Связи
from .users.relations       import UserCourse
from .courses.relations     import (
                                    ProgramCourse, CourseModule, 
                                    ModuleFile, ModuleTest
                                )
from .assessments.relations import TestQuestion, AttemptQuestion

# API экспорта моделей
__all__ = [
    # Пользователи
    'User', 'UserManager', 'Role', 'UserCourse',
    # Курсы
    'Program', 'Course', 'ProgramCourse', 'Module', 
    'CourseModule', 'File', 'ModuleFile', 'ModuleTest',
    # Оценивания
    'Test','Question', 'TestQuestion',
    'TestAttempt', 'ExamAttempt', 'AttemptQuestion',
]
