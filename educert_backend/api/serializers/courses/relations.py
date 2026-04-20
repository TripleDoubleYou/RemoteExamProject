from rest_framework import serializers
from api.models import ProgramCourse, CourseModule, ModuleFile, ModuleTest

class ProgramCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramCourse
        fields = ['id', 'program_id', 'course_id', 'created_at', 'creator']

class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = ['id', 'course_id', 'module_id', 'module_number', 'created_at', 'creator']

class ModuleFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleFile
        fields = ['id', 'module_id', 'file_id']

class ModuleTestSerializer(serializers.ModelSerializer):
    test_id = serializers.IntegerField()
    module_id = serializers.IntegerField()
    class Meta:
        model = ModuleTest
        fields = ['id', 'test_id', 'module_id']