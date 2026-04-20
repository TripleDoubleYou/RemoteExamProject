from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'programs', ProgramViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'programcourses', ProgramCourseViewSet)
router.register(r'user-courses', UserCourseViewSet)
router.register(r'coursemodules', CourseModuleViewSet)
router.register(r'files', FileViewSet)
router.register(r'modulefiles', ModuleFileViewSet)
router.register(r'module', ModuleViewSet)
router.register(r'tests', TestViewSet)
router.register(r'moduletests', ModuleTestViewSet)
router.register(r'testattempts', TestAttemptViewSet)
router.register(r'examattempts', ExamAttemptViewSet)
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'test-questions', TestQuestionViewSet, basename='testquestion')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('users-import/', UserImportView.as_view(), name='users_import'),
    path('questions-import/', QuestionImportView.as_view(), name='questions_import'),
    path('coursemoduledetail/<int:course_id>/',CourseModuleDetailView.as_view(),name='course-module-detail'),
    path('courses/<int:course_id>/exam-questions/', GetExamQuestionsView.as_view(), name='get-course-exam-questions'),
    path('tests/<int:test_id>/test-questions/', GetTestQuestionsView.as_view(), name='get-test-questions'),
    path('logout/', LogoutView.as_view(), name='log-out'),
]