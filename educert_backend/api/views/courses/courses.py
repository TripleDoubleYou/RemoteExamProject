from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models import Course
from api.serializers import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Course']