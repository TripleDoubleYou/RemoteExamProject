from django.db import models
from api.models import User, Course

class UserCourse(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    progress = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'api_usercourse'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['course_id']),
        ]
        verbose_name = "User-Course"
        verbose_name_plural = "User-Courses"