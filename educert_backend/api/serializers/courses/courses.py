from rest_framework import serializers
from api.models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'exam_question_count', 'time_limit', 'created_at', 'creator']