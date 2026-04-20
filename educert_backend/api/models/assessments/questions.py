from django.db import models

class Question(models.Model):
    QUESTION_TYPES = [
        ('one',   'Один ответ'),
        ('multi', 'Несколько ответов'),
        ('text',  'Строка'),
        ('table', 'Таблица'),
    ]

    id = models.AutoField(primary_key=True)
    text = models.TextField()
    payload = models.JSONField(default=dict)
    type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    correct_answer = models.TextField()

    class Meta:
        db_table = 'api_question'
        unique_together = ('text','type','payload','correct_answer')
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['type']),
        ]