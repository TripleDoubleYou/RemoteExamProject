from django.db import models
from api.models import User

class File(models.Model):
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(unique=True)
    description = models.CharField()
    file = models.FileField(upload_to='courses/', unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.file_name
    
    def save(self, *args, **kwargs):
        if not self.file_name and self.file:
            self.file_name = self.file.name.rsplit('/', 1)[-1]
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'api_file'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['file']),
            models.Index(fields=['file_name']),
            models.Index(fields=['creator']),
        ]