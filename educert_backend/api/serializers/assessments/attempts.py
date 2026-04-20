from rest_framework import serializers
from api.models import TestAttempt, ExamAttempt
from .relations import AttemptQuestionSerializer

class TestAttemptSerializer(serializers.ModelSerializer):
    questions = AttemptQuestionSerializer(source='attemptquestion_set', many=True)

    class Meta:
        model = TestAttempt
        fields = [
            'id', 'user_id', 'test_id', 'percent', 'is_best',
            'is_passed', 'created_at', 'questions'
        ]
        read_only_fields = ['id', 'user_id', 'percent', 'is_best', 'is_passed', 'created_at']
        
class ExamAttemptSerializer(serializers.ModelSerializer):
    questions = AttemptQuestionSerializer(source='attemptquestion_set', many=True)

    class Meta:
        model = ExamAttempt
        fields = [
            'id', 'user_id', 'course_id', 'percent', 'exam_mark',
            'created_at', 'questions'
        ]
        read_only_fields = ['id', 'user_id', 'percent', 'exam_mark', 'created_at']