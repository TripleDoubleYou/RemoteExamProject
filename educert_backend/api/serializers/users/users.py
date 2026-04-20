from rest_framework import serializers
from api.models import User, Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field='name'
    )
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'second_name', 'last_name',
            'email', 'role', 'date_of_birth',
            'profile_picture', 'date_joined', 'email_confirmed',
            'is_active', 'is_staff'
        ]
        read_only_fields = ['id', 'date_joined', 'is_staff']