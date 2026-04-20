from django.db import models
from api.models import User

class Test(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    percent_success = models.IntegerField()
    test_question_count = models.IntegerField(null=True)
    time_limit = models.IntegerField(help_text="limit in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'api_test'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['creator']),
        ]