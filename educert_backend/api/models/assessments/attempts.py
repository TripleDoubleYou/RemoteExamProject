from django.db import models
from api.models import User, Course, Test

class TestAttempt(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE, db_column='test_id')
    created_at = models.DateTimeField(auto_now_add=True)
    percent = models.FloatField()
    is_best = models.BooleanField(default=False)
    is_passed  = models.BooleanField(default=False)

    class Meta:
        db_table = 'api_usertestattempt'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['test_id']),
            models.Index(fields=['user_id', 'test_id']),
            models.Index(fields=['user_id', 'test_id', 'is_best']),
        ]
        verbose_name = "User-Test-Attempt"
        verbose_name_plural = "User-Test-Attempts"

class ExamAttempt(models.Model):
    id         = models.AutoField(primary_key=True)
    user_id    = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    course_id  = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    created_at = models.DateTimeField(auto_now_add=True)
    percent    = models.FloatField(default=0)
    exam_mark  = models.IntegerField()

    class Meta:
        db_table = 'api_userexamattempt'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['course_id']),
            models.Index(fields=['user_id', 'course_id']),
        ]
        verbose_name = "User-Exam-Attempt"
        verbose_name_plural = "User-Exam-Attempts"