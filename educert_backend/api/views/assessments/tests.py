from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models import Test
from api.serializers import TestSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Test']