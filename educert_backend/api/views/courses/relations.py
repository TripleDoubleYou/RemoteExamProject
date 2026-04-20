from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models import ProgramCourse, CourseModule, ModuleFile, ModuleTest
from api.serializers import ProgramCourseSerializer, CourseModuleSerializer, ModuleFileSerializer, ModuleTestSerializer
from api.decorators import log_exceptions
from api.utils import get_module_details
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProgramCourseViewSet(viewsets.ModelViewSet):
    queryset = ProgramCourse.objects.all()
    serializer_class = ProgramCourseSerializer
    parser_classes = [MultiPartParser, FormParser]
    swagger_tags = ['Program', 'Course']

    @log_exceptions
    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    name='id',
                    in_=openapi.IN_QUERY,
                    description='Идентификатор записи ProgramCourse',
                    type=openapi.TYPE_INTEGER,
                ),
                openapi.Parameter(
                    name='program_id',
                    in_=openapi.IN_QUERY,
                    description='Идентификатор курса для фильтрации программ',
                    type=openapi.TYPE_INTEGER,
                ),
                openapi.Parameter(
                    name='course_id',
                    in_=openapi.IN_QUERY,
                    description='Идентификатор программы для фильтрации курсов',
                    type=openapi.TYPE_INTEGER,
                ),
            ]
        )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @log_exceptions
    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if 'id' in params:
            return qs.filter(id=params['id'])
        if 'program_id' in params:
            return qs.filter(program_id=params['program_id'])
        if 'course_id' in params:
            return qs.filter(course_id=params['course_id'])
        return qs
    
class CourseModuleViewSet(viewsets.ModelViewSet):
    """
    GET /api/coursemodules/?
        id=
        course_id=
        module_id=
    """
    queryset = CourseModule.objects.all()
    serializer_class = CourseModuleSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @log_exceptions
    @swagger_auto_schema(
            manual_parameters=[
                openapi.Parameter(
                    name='id',
                    in_=openapi.IN_QUERY,
                    description='Идентификатор записи CourseModule',
                    type=openapi.TYPE_INTEGER,
                ),
                openapi.Parameter(
                    name='course_id',
                    in_=openapi.IN_QUERY,
                    description='Идентификатор курса для фильтрации модулей',
                    type=openapi.TYPE_INTEGER,
                ),
                openapi.Parameter(
                    name='module_id',
                    in_=openapi.IN_QUERY,
                    description='Идентификатор модуля для фильтрации',
                    type=openapi.TYPE_INTEGER,
                ),
            ]
        )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @log_exceptions
    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if 'id' in params:
            return qs.filter(id=params['id'])
        if 'course_id' in params:
            return qs.filter(course_id=params['course_id'])
        if 'module_id' in params:
            return qs.filter(module_id=params['module_id'])
        return qs
    
    
class CourseModuleDetailView(APIView):
    """
    GET /api/coursemoduledetail/{course_id}/
    Возвращает для курса полный набор данных по каждому модулю:
    module_id, module_number, module_name, description, files, tests...
    """
    queryset = CourseModule.objects.all()
    serializer_class = CourseModuleSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='course_id',
                in_=openapi.IN_PATH,
                description='Идентификатор курса',
                type=openapi.TYPE_INTEGER,
            )
        ]
    )

    @log_exceptions
    def get(self, request, course_id):
        cms = CourseModule.objects.filter(course_id=course_id).select_related('module_id')
        result = []
        for cm in cms:
            module_data = get_module_details(cm.module_id)
            module_data['module_number'] = cm.module_number
            result.append(module_data)
        return Response(result, status=status.HTTP_200_OK)
    
class ModuleFileViewSet(viewsets.ModelViewSet):
    queryset = ModuleFile.objects.all()
    serializer_class = ModuleFileSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Module', 'File']

class ModuleTestViewSet(viewsets.ModelViewSet):
    queryset = ModuleTest.objects.all()
    serializer_class = ModuleTestSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['Module', 'Test']