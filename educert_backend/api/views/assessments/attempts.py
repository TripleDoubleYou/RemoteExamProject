from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models import *
from api.serializers import *
from api.decorators import log_exceptions
from api.utils import *
from api.permissions import IsAdmin
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class TestAttemptViewSet(viewsets.ModelViewSet):
    queryset = TestAttempt.objects.all()
    serializer_class = TestAttemptSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @log_exceptions
    def update_best_attempt(user, test):
        with transaction.atomic():
            attempts = TestAttempt.objects.filter(user_id=user, test_id=test)
            if not attempts.exists():
                return
            best = attempts.order_by('-percent', '-created_at').first()
            attempts.update(is_best=False)
            best.is_best = True
            best.save(update_fields=['is_best'])

    @swagger_auto_schema(
        request_body=TestAttemptSerializer,
        responses={201: TestAttemptSerializer}
    )
    @log_exceptions
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        data = serializer.validated_data
        test = data['test']
        questions_data = request.data.get('questions', [])

        with transaction.atomic():
            test = Test.objects.get(id=test.id)
            attempt = TestAttempt.objects.create(
                user_id=user,
                test_id=test,
                percent=0.0,
                is_best=False,
                is_passed=False
            )
        
            percent = save_attempt_questions(attempt, questions_data, is_exam=False)
            attempt.percent = percent
            attempt.is_passed = percent >= test.percent_success
            attempt.save(update_fields=['percent', 'is_passed'])

            TestAttemptViewSet.update_best_attempt(user, attempt.test)

            update_user_course_progress(request.user, test_id=attempt.test)

        out = TestAttemptSerializer(attempt, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('test_id', in_=openapi.IN_QUERY, description='Идентификатор теста для фильтрации попыток', type=openapi.TYPE_INTEGER),
        ],
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'attempts': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))}
        )}
    )
    @log_exceptions
    def list(self, request, *args, **kwargs):
        user = request.user
        qs = TestAttempt.objects.filter(user_id=user).order_by('-created_at')
        if 'test_id' in request.query_params:
            test_id = request.query_params.get('test_id')
            qs = qs.filter(test_id=test_id)
        data = [
            {
             "id": att.id, 
             "test_id": att.test_id, 
             "percent": att.percent, 
             "is_best": att.is_best,
             "is_passed": att.is_passed,
             "created_at": att.created_at
            }
            for att in qs
        ]
        return Response({"attempts": data})



class ExamAttemptViewSet(viewsets.ModelViewSet):
    queryset = ExamAttempt.objects.all()
    serializer_class = ExamAttemptSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('course_id', in_=openapi.IN_QUERY, description='Идентификатор курса для фильтрации попыток', type=openapi.TYPE_INTEGER),
        ],
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'attempts': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))}
        )}
    )
    @log_exceptions
    def list(self, request, *args, **kwargs):
        qs = self.queryset.filter(user_id=self.request.user).order_by('-created_at')
        if 'course_id' in self.request.query_params:
            course_id = self.request.query_params.get('course_id')
            qs = qs.filter(course_id=course_id)
        serializer = self.get_serializer(qs, many=True)
        return Response({'attempts': serializer.data})

    @swagger_auto_schema(
        request_body=ExamAttemptSerializer,
        responses={201: ExamAttemptSerializer}
    )
    @log_exceptions
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user
        course = data['course_id']
        questions = request.data.get('questions', [])

        with transaction.atomic():
            attempt = ExamAttempt.objects.create(
                user_id=user,
                course_id=course,
                percent=0.0,
                exam_mark=0
            )

            percent = save_attempt_questions(attempt, questions, is_exam=True)
            attempt.percent = percent
            for mark, thresh in sorted(settings.EXAM_MARKS_PERCENT.items(), key=lambda kv: kv[1]):
                if percent < thresh:
                    attempt.exam_mark = mark
                    break
            else:
                attempt.exam_mark = max(settings.EXAM_MARKS_PERCENT.keys())
            attempt.save(update_fields=['percent', 'exam_mark'])
            
        update_user_course_progress(request.user, course_id=attempt.course_id)

        out = ExamAttemptSerializer(attempt, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('attempt_id', in_=openapi.IN_QUERY, description='Идентификатор попытки для удаления', type=openapi.TYPE_INTEGER),
        ],
        responses={204: 'No Content'}
    )
    @log_exceptions
    def destroy(self, request, *args, **kwargs):
        attempt_id = request.query_params.get('attempt_id')
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, user=request.user)
        attempt.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)