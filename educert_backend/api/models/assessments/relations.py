from django.db import models
from api.models import Test, Question, TestAttempt, ExamAttempt

class TestQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE, db_column='test_id')
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, db_column='question_id')

    class Meta:
        db_table = 'api_testquestion'
        unique_together = ['test_id', 'question_id']
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['test_id']),
            models.Index(fields=['question_id']),
        ]
        verbose_name = "Test-Question"
        verbose_name_plural = "Test-Questions"


# Прохождение тестов


class AttemptQuestion(models.Model):
    """
    Хранит, какие вопросы и с какими ответами вошли в конкретную попытку теста.
    """
    id = models.AutoField(primary_key=True)
    test_attempt_id = models.ForeignKey(TestAttempt, null=True, on_delete=models.CASCADE, db_column='test_attempt_id')
    exam_attempt_id = models.ForeignKey(ExamAttempt, null=True, on_delete=models.CASCADE, db_column='exam_attempt_id')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=255, null=True)
    is_correct = models.BooleanField(null=True)

    class Meta:
        db_table = 'api_attemptquestion'
        indexes = [
            models.Index(fields=['test_attempt_id']),
            models.Index(fields=['exam_attempt_id']),
            models.Index(fields=['question']),
            models.Index(fields=['test_attempt_id', 'question']),
            models.Index(fields=['exam_attempt_id', 'question']),
        ]
        verbose_name = "Attempt-Question"
        verbose_name_plural = "Attempt-Questions"