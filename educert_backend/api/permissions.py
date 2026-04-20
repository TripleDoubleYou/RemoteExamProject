from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role and request.user.role.name == 'Администратор'

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role and request.user.role.name == 'Преподаватель'

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role and request.user.role.name == 'Студент'