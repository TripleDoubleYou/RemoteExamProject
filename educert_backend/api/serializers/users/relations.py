from rest_framework import serializers
from api.models import UserCourse

class UserCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourse
        fields = ['id', 'user_id', 'course_id', 'progress']