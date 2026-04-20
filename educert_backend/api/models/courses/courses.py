from django.db import models
from api.models import User

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    exam_question_count = models.IntegerField(null=True)
    time_limit = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.name} — {self.description[:50]}"
    
    class Meta:
        db_table = 'api_course'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['creator']),
        ]