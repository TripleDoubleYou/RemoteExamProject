from rest_framework import serializers
from api.models import File

class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    file_name   = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = File
        fields = ['id', 'file_name', 'description', 'file', 'created_at', 'creator']