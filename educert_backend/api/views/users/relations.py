from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models import UserCourse
from api.serializers import UserCourseSerializer
from api.decorators import log_exceptions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserCourseViewSet(viewsets.ModelViewSet):
    queryset = UserCourse.objects.all()
    serializer_class = UserCourseSerializer
    permission_classes = [IsAuthenticated]
    swagger_tags = ['User', 'Courses']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='id', in_=openapi.IN_QUERY,
                description='ID записи UserCourses',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                name='user_id', in_=openapi.IN_QUERY,
                description='ID пользователя',
                type=openapi.TYPE_INTEGER
            ),
        ]
    )
    @log_exceptions
    def list(self, request):
        id_      = request.query_params.get('id')
        user_id  = request.query_params.get('user_id')

        # Базовый queryset с нужными связями
        qs = UserCourse.objects.select_related('user_id', 'course_id')
        if id_:
            qs = qs.filter(id=id_)
        elif user_id:
            qs = qs.filter(user_id=user_id)

        result = {}
        for uc in qs:
            uid = str(uc.user.id)
            if uid not in result:
                result[uid] = {
                    "user_id":      uid,
                    "user_email":   uc.user.email,
                    "user_name":    f"{uc.user.first_name} {uc.user.second_name} {uc.user.last_name}",
                    "courses":      []
                }
            result[uid]["courses"].append({
                "id":           uc.id,
                "course_id":          uc.course.id,
                "course_name":        uc.course.name,
                "course_description": uc.course.description,
                "progress":           uc.progress,
                "creator":            uc.course.creator_id,
            })

        if id_:
            if not result:
                return Response(status=404)
            return Response(next(iter(result.values())))

        if user_id:
            return Response(
                result.get(str(user_id), {
                    "user_id": user_id,
                    "user_email": None,
                    "user_name": None,
                    "courses": []
                })
            )

        return Response(list(result.values()))
    


