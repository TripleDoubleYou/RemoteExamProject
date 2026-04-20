import pandas as pd
from io import BytesIO
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.models import *
from api.serializers import *
from api.decorators import log_exceptions
from api.utils import *
from api.permissions import IsAdmin
from random import sample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action 
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import timedelta

class TestQuestionViewSet(viewsets.ModelViewSet):
    """
    CRUD для TestQuestion с фильтрацией по test_id и question_id
    """
    queryset = TestQuestion.objects.all()
    serializer_class = TestQuestionSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @log_exceptions
    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if 'id' in params:
            return qs.filter(id=params['id'])
        if 'test_id' in params:
            return qs.filter(test_id=params['test_id'])
        if 'question_id' in params:
            return qs.filter(question_id=params['question_id'])
        return qs
    
    @log_exceptions
    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    name='id',
                    in_=openapi.IN_QUERY,
                    description='Идентификатор записи TestQuestion',
                    type=openapi.TYPE_INTEGER,
                ),
                openapi.Parameter(
                    name='test_id',
                    in_=openapi.IN_QUERY,
                    description='Идентификатор теста для фильтрации модулей',
                    type=openapi.TYPE_INTEGER,
                ),
                openapi.Parameter(
                    name='question_id',
                    in_=openapi.IN_QUERY,
                    description='Идентификатор вопроса для фильтрации',
                    type=openapi.TYPE_INTEGER,
                ),
            ]
        )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    
    @action(
        detail=False,
        methods=['post'],
        parser_classes=[JSONParser],
    )
    def bulk(self, request):
        """
        Ожидает JSON:
        {
          "test_id": <int>,
          "question_ids": [<int>, <int>, ...]
        }
        Отвечает:
        {
          "created":  [<TestQuestion id>, ...],
          "existing": [<TestQuestion id>, ...]
        }
        """
        test_id = request.data.get('test_id')
        question_ids = request.data.get('question_ids')

        if not isinstance(test_id, int) or not isinstance(question_ids, list):
            return Response(
                {"detail": "Нужно передать test_id:int и question_ids:list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # проверяем, что тест существует
        try:
            test = Test.objects.get(pk=test_id)
        except Test.DoesNotExist:
            return Response(
                {"detail": f"Test с id={test_id} не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_ids = []
        existing_ids = []

        for qid in question_ids:
            # проверяем, что вопрос существует
            try:
                question = Question.objects.get(pk=qid)
            except Question.DoesNotExist:
                return Response(
                    {"detail": f"Question с id={qid} не найден"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            obj, created = TestQuestion.objects.get_or_create(
                test_id=test,
                question_id=question,
            )
            if created:
                created_ids.append(obj.id)
            else:
                existing_ids.append(obj.id)

        return Response({
            "created":  created_ids,
            "existing": existing_ids,
        }, status=status.HTTP_201_CREATED)