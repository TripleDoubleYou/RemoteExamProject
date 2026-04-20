from django.contrib import admin
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Group
from .models import *

admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def role_name(self, obj):
        role = Role.objects.filter(id=obj.role_id).first()
        return role.name if role else '-'
    role_name.short_description = 'Role'

    def save_model(self, request, obj, form, change):
        if not change and not obj.password:
            password = get_random_string(12)
            obj.set_password(password)
        elif not change and obj.password:
            obj.set_password(obj.password)
        obj.save()

    list_display = ('email', 'first_name', 'second_name', 'last_name', 'role_name')
    search_fields = ('email', 'first_name', 'second_name', 'last_name')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'creator')
    list_filter = ('name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'exam_question_count', 'time_limit', 'created_at', 'creator')
    list_filter = ('name',)

@admin.register(UserCourse)
class UserCoursesAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'course_id', 'progress')

@admin.register(ProgramCourse)
class ProgramCourseAdmin(admin.ModelAdmin):
    list_display = ('program_id', 'course_id', 'created_at', 'creator')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'creator')
    list_filter = ('name',)

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'module_id', 'module_number', 'created_at', 'creator')

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('description', 'file', 'created_at', 'creator')
    list_filter = ('description',)

@admin.register(ModuleFile)
class ModuleFileAdmin(admin.ModelAdmin):
    list_display = ('module_id', 'file_id')

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'test_question_count', 'percent_success', 'time_limit', 'created_at', 'creator')
    list_filter = ('name',)

@admin.register(ModuleTest)
class ModuleTestAdmin(admin.ModelAdmin):
    list_display = ('module_id', 'test_id')

@admin.register(TestAttempt)
class UserTestAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'test_id', 'percent', 'is_best', 'is_passed', 'created_at')
    list_filter = ('id', 'user_id', 'test_id',)

@admin.register(ExamAttempt)
class UserExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'course_id', 'percent', 'exam_mark', 'created_at')
    list_filter = ('id', 'user_id', 'course_id',)

@admin.register(AttemptQuestion)
class AttemptQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_attempt_id', 'exam_attempt_id', 'question', 'user_answer', 'is_correct')
    list_filter = ('test_attempt_id', 'exam_attempt_id', 'question')

@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_id', 'question_id')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'text', 'correct_answer')
    search_fields = ('text',)