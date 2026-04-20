from rest_framework import serializers
from api.models import TestQuestion, AttemptQuestion

class TestQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestQuestion
        fields = ['id', 'test_id', 'question_id']

class AttemptQuestionSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField()
    user_answer = serializers.CharField(allow_blank=True)

    class Meta:
        model = AttemptQuestion
        fields = ['question_id', 'user_answer', 'is_correct']
        read_only_fields = ['is_correct']