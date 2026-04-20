from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

# Роли пользователей
class Role(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'api_role'
        indexes = [
            models.Index(fields=['id']),
        ]
    
# Django admin panel users
class UserManager(BaseUserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        try:
            admin_role = Role.objects.get(name='Администратор')
        except Role.DoesNotExist:
            raise ValueError("Роль 'Администратор' не найдена в базе. Создай её сначала.")
        extra_fields['role'] = admin_role
        extra_fields['email_confirmed'] = True
        extra_fields['is_staff'] = True
        
        if not email:
            raise ValueError("Почта обязательна.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

# Модель пользователя
class User(AbstractBaseUser):
    last_login = None
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    email_confirmed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'second_name', 'last_name', 'date_of_birth']
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        if self.is_staff:
            return True
        return False

    def has_module_perms(self, app_label):
        return self.is_staff
    
    class Meta:
        db_table = 'api_user'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]