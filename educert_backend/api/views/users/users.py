import pandas as pd
from io import BytesIO
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.models import User, Role
from api.serializers import UserSerializer, RoleSerializer
from api.decorators import log_exceptions
from api.utils import import_and_notify, validate_excel, create_user_account
from api.permissions import IsAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action 
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserImportView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Импорт пользователей из Excel",
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                description="Файл Excel (.xlsx) с пользователями",
                type=openapi.TYPE_FILE,
                required=True
            )
        ],
        responses={
            201: openapi.Response('Успех', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'created': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )),
            207: 'Partial Success, multi-status',
            400: 'Bad Request'
        }
    )

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"detail":"Не передан файл"}, status=400)

        # Читаем Excel из памяти
        try:
            excel_bytes = file_obj.read()
            df = pd.read_excel(BytesIO(excel_bytes))
        except Exception:
            return Response({"detail":"Невозможно прочитать Excel"}, status=400)

        # Теперь df уже есть — можно вызвать validate_excel(df, request.user)
        rows, errors = validate_excel(df, request.user)
        if errors:
            return Response({"errors":errors}, status=400)

        created, existing = import_and_notify(rows)

        return Response({
            'created':  created,
            'existing': existing
        }, status=status.HTTP_201_CREATED)
    


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    swagger_tags = ['User']

    def get_serializer_class(self):
        if self.action in ['ban', 'unban']:
            return None
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ('ban', 'unban'):
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def save(self, request, *args, **kwargs):
        return super().save(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='me')
    @log_exceptions
    def get_current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @log_exceptions
    def create(self, request):
        data = request.data.copy()
        if not data.get('role'):
            data['role'] = 'Студент'
        try:
            user = create_user_account(data)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Пользователь создан, пароль отправлен'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=None)
    @action(
        detail=True,
        methods=['patch'],
        url_path='ban',
    )
    @log_exceptions
    def ban(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'detail': 'Пользователь заблокирован'},
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=None)
    @action(
        detail=True,
        methods=['patch'],
        url_path='unban',
    )
    @log_exceptions
    def unban(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response({'detail': 'Пользователь разблокирован'},
                        status=status.HTTP_200_OK)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Role']