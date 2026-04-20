from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models import Module
from api.serializers import ModuleSerializer
from api.decorators import log_exceptions
from api.utils import get_module_details
from rest_framework.response import Response

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    @log_exceptions
    def list(self, request, *args, **kwargs):
        data = [get_module_details(m) for m in self.get_queryset()]
        return Response(data)

    @log_exceptions
    def retrieve(self, request, *args, **kwargs):
        module = self.get_object()
        return Response(get_module_details(module))
    