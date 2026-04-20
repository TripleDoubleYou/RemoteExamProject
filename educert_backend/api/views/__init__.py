# api/views/__init__.py

"""
Главный файл экспорта всех view-классов.
"""

# --- Аутентификация, управление пользователями и ролями
from .users.auth            import (
                                    CustomTokenObtainPairView,
                                    CustomTokenRefreshView,
                                    LogoutView,
                                    ChangePasswordView,
                                    ResetPasswordView,
                                )
from .users.users           import (
                                    UserImportView,
                                    UserViewSet,
                                    RoleViewSet,
                                )

# --- Каталог: программы, курсы и модули
from .courses.courses       import CourseViewSet
from .courses.modules       import ModuleViewSet
from .courses.files         import FileViewSet
from .courses.programs      import ProgramViewSet

# --- Оценивания: тесты, вопросы, попытки
from .assessments.tests     import TestViewSet
from .assessments.questions import (
                                    GetExamQuestionsView,
                                    GetTestQuestionsView,
                                    QuestionViewSet,
                                    QuestionImportView,
                                )
from .assessments.attempts  import (
                                    TestAttemptViewSet,
                                    ExamAttemptViewSet,
                                )

# --- Связи
from .users.relations       import UserCourseViewSet
from .courses.relations     import (
                                    ProgramCourseViewSet,
                                    CourseModuleViewSet,
                                    CourseModuleDetailView,
                                    ModuleFileViewSet,
                                    ModuleTestViewSet,
                                )
from .assessments.relations import TestQuestionViewSet

# Форма экспорта
__all__ = [
    # Пользователи
    'CustomTokenObtainPairView', 'CustomTokenRefreshView', 'LogoutView',
    'ChangePasswordView', 'ResetPasswordView', 'UserImportView',
    'UserViewSet', 'RoleViewSet', 'UserCourseViewSet',
    # Курсы
    'CourseViewSet', 'ModuleViewSet', 'FileViewSet', 'ProgramViewSet',
    'ProgramCourseViewSet', 'CourseModuleViewSet', 'CourseModuleDetailView',
    'ModuleFileViewSet', 'ModuleTestViewSet',
    # Оценивания
    'TestViewSet', 'TestQuestionViewSet', 'GetExamQuestionsView',
    'GetTestQuestionsView', 'QuestionViewSet', 'QuestionImportView',
    'TestAttemptViewSet', 'ExamAttemptViewSet',
]
