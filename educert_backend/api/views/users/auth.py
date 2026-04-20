from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.models import *
from api.serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer
from api.decorators import log_exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta

# Авторизация
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    # Получение токена с добавлением роли
    @log_exceptions
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        try:
            # email берём из request.data
            email = request.data.get('email')
            user = User.objects.get(email=email)
            if not user.email_confirmed:
                user.email_confirmed = True
                user.save(update_fields=['email_confirmed'])
        except User.DoesNotExist:
            pass

        access_token = response.data.pop('access', None)  # Удаляем из тела ответа
        refresh_token = response.data.pop('refresh', None)

        if access_token and refresh_token:
            # Устанавливаем access_token cookie
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=settings.SECURE_SSL_REDIRECT,
                samesite='Strict',
                max_age=int(timedelta(days=1).total_seconds()),  # Конвертируем в секунды
                path='/',  # Доступно на всех путях сайта
            )
            
            # Устанавливаем refresh_token cookie
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=settings.SECURE_SSL_REDIRECT,
                samesite='Strict',
                max_age=int(timedelta(days=7).total_seconds()),  # Refresh на 7 дней
                path='/',
            )

        return response

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    swagger_tags = ['User']

class LogoutView(APIView):
    @log_exceptions
    def post(self, request):
        response = Response({"detail": "Successfully logged out."})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    
    # Смена пароля
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["old_password", "new_password"],
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    @log_exceptions
    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Старый пароль неверный"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Пароль успешно изменен"}, status=status.HTTP_200_OK)
    
    swagger_tags = ['User']

class ResetPasswordView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    @log_exceptions
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Поле email обязательно"}, status=400)

        try:
            user = User.objects.get(email=email)
            new_password = get_random_string(12)
            user.set_password(new_password)
            user.save()

            send_mail(
                subject='Восстановление пароля EduCert',
                message=f'Ваш новый пароль: {new_password}',
                from_email='noreply@educert.local',
                recipient_list=[email]
            )
            return Response({"message": "Новый пароль отправлен на почту"}, status=200)
        except User.DoesNotExist:
            return Response({"error": "Пользователь с таким email не найден"}, status=404)
        
    swagger_tags = ['User']