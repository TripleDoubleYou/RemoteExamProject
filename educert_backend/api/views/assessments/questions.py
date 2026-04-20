import pandas as pd
from io import BytesIO
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models import *
from api.serializers import *
from api.decorators import log_exceptions
from api.utils import *
from api.permissions import IsAdmin
from random import sample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class GetExamQuestionsView(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Course', 'Question']

    @log_exceptions
    def get(self, request, course_id):
        course =  Course.objects.get(id=course_id)

        module_ids = CourseModule.objects.filter(course_id=course_id).values_list('module_id', flat=True)

        test_ids = ModuleTest.objects.filter(module__in=module_ids).values_list('test', flat=True)

        question_ids = TestQuestion.objects.filter(test_id__in=test_ids).values_list('question_id', flat=True).distinct()

        questions_qs = sample(list(Question.objects.filter(id__in=question_ids)), course.exam_question_count)

        serializer = QuestionNoAnswerSerializer(questions_qs, many=True)
        return Response({
            "questions": serializer.data
        }, status=status.HTTP_200_OK)
    
class GetTestQuestionsView(APIView):
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Test']

    @log_exceptions
    def get(self, request, test_id):
        test = Test.objects.get(id=test_id)

        question_ids = TestQuestion.objects.filter(test_id=test.id).values_list('question_id', flat=True).distinct()

        questions_qs = sample(list(Question.objects.filter(id__in=question_ids)), test.test_question_count)

        serializer = QuestionNoAnswerSerializer(questions_qs, many=True)
        return Response({
            "questions": serializer.data
        }, status=status.HTTP_200_OK)
    
class QuestionViewSet(viewsets.ModelViewSet):
    """
    Стандартные CRUD-эндпойнты для Question
    + bulk import через JSON на POST /questions/bulk/
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        """
        Ожидает JSON:
        {
          "questions": [
            {
              "type": "...",
              "text": "...",
              "payload": {...},
              "correct_answer": "..."
            }, ...
          ]
        }
        Отвечает:
        {
          "created": [id, ...],
          "existing": [id, ...],
          "questions": [
            { "id":..., "type":..., "text":..., "payload":..., "correct_answer":... },
            ...
          ]
        }
        """
        data = request.data.get('questions')
        if not isinstance(data, list):
            return Response(
                {"detail": "Ожидается список questions"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_ids, existing_ids, all_q = save_parsed_questions(data)
        return Response({
            'created':  created_ids,
            'existing': existing_ids,
            'questions': all_q,
        }, status=status.HTTP_201_CREATED)
    
class QuestionImportView(APIView):
    """
    Принимает файл Excel, парсит и сохраняет вопросы.
    Если валидация упала — сразу отдаёт ошибки по строкам.
    Если всё ок — создаёт новые или берёт существующие вопросы,
    и в ответ кладёт списки их id.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Импорт тестов из Excel",
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                description="Файл Excel (.xlsx) с тестами",
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
        f = request.FILES.get('file')
        if not f:
            return Response({'detail':'Файл не передан'}, status=400)

        df = pd.read_excel(BytesIO(f.read()))
        parsed, errors = validate_and_parse_questions(df)

        if errors:
            return Response({'errors': errors}, status=400)

        #created_ids, existing_ids, all_q = save_parsed_questions(parsed)

        all_q = []
        for item in parsed:
            all_q.append({
            'type': item['type'],
            'text': item['text'],
            'payload': item['payload'],
            'correct_answer': item['correct_answer'],
        })
        

        return Response({
            'questions': all_q,
        }, status=status.HTTP_201_CREATED)