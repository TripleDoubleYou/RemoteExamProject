from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models import Program
from api.serializers import ProgramSerializer

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Program']