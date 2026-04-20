# api/serializers/__init__.py

"""
Главный файл экспорта всех сериализаторов.
"""

# --- Пользователи, роли и аутентификация
from .users.auth            import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer
from .users.users           import RoleSerializer, UserSerializer

# --- Каталог: программы, курсы и модули
from .courses.courses       import CourseSerializer
from .courses.programs      import ProgramSerializer
from .courses.modules       import ModuleSerializer
from .courses.files         import FileSerializer

# --- Оценивания: тесты, вопросы, попытки
from .assessments.tests     import TestSerializer
from .assessments.questions import QuestionSerializer, QuestionNoAnswerSerializer
from .assessments.attempts  import TestAttemptSerializer, ExamAttemptSerializer



# --- Связи
from .users.relations       import UserCourseSerializer
from .courses.relations     import (
                                    ProgramCourseSerializer,
                                    CourseModuleSerializer,
                                    ModuleFileSerializer,
                                    ModuleTestSerializer,
                                )
from .assessments.relations import TestQuestionSerializer, AttemptQuestionSerializer
__all__ = [
    # Пользователи
    'CustomTokenObtainPairSerializer', 'CustomTokenRefreshSerializer',
    'RoleSerializer', 'UserSerializer', 'UserCourseSerializer',
    # Курсы
    'CourseSerializer', 'ProgramSerializer', 'ModuleSerializer', 'FileSerializer',
    'ProgramCourseSerializer', 'CourseModuleSerializer', 'ModuleFileSerializer', 'ModuleTestSerializer',
    # Оценивания
    'TestSerializer',
    'TestQuestionSerializer', 'AttemptQuestionSerializer',
    'QuestionSerializer', 'QuestionNoAnswerSerializer',
    'TestAttemptSerializer', 'ExamAttemptSerializer',
]
