from django.db import models
from api.models import Program, Course, Module, Test, File, User

class ProgramCourse(models.Model):
    id = models.AutoField(primary_key=True)
    program_id = models.ForeignKey(Program, on_delete=models.CASCADE, db_column='program_id')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'api_programcourse'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['program_id']),
            models.Index(fields=['course_id']),
        ]
        verbose_name = "Program-Course"
        verbose_name_plural = "Program-Courses"

class CourseModule(models.Model):
    id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    module_id = models.ForeignKey(Module, on_delete=models.CASCADE, db_column='module_id')
    module_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'api_coursemodule'
        unique_together = ['course_id', 'module_id']
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['course_id']),
            models.Index(fields=['module_id']),
        ]
        verbose_name = "Course-Module"
        verbose_name_plural = "Course-Modules"

class ModuleFile(models.Model):
    id = models.AutoField(primary_key=True)
    module_id = models.ForeignKey(Module, on_delete=models.CASCADE, db_column='module_id')
    file_id = models.ForeignKey(File, on_delete=models.CASCADE, db_column='file_id')

    class Meta:
        db_table = 'api_modulefile'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['module_id']),
            models.Index(fields=['file_id']),
        ]
        verbose_name = "Module-File"
        verbose_name_plural = "Module-Files"

# Тестирование


class ModuleTest(models.Model):
    id = models.AutoField(primary_key=True)
    module_id = models.ForeignKey(Module, on_delete=models.CASCADE, db_column='module_id')
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE, db_column='test_id')

    class Meta:
        db_table = 'api_moduletest'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['module_id']),
            models.Index(fields=['test_id']),
        ]
        verbose_name = "Module-Test"
        verbose_name_plural = "Module-Tests"