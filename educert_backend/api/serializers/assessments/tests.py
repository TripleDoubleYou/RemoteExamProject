from rest_framework import serializers
from api.models import Test

class TestSerializer(serializers.ModelSerializer):
    total_question_count = serializers.SerializerMethodField()

    def get_total_question_count(self, obj):
        return obj.testquestion_set.count()
    
    class Meta:
        model = Test
        fields = ['id', 'name', 'percent_success', 'test_question_count', 
                  'time_limit', 'created_at', 'creator', 'total_question_count']