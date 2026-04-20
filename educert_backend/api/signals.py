from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

from .models import ModuleFile, CourseModule, File, Module, TestQuestion, Question

@receiver(post_delete, sender=ModuleFile)
def cleanup_file_on_modulefile_delete(sender, instance, **kwargs):
    """
    После того как связь ModuleFile удалена,
    если этот файл больше нигде не привязан — удаляем и запись в File, и сам файл из хранилища.
    """
    file_obj = instance.file
    # если больше нет ни одного ModuleFile с этим файлом
    if not ModuleFile.objects.filter(file=file_obj).exists():
        # сначала удаляем физический файл
        file_obj.file.delete(save=False)
        # затем запись в БД
        file_obj.delete()

@receiver(post_delete, sender=CourseModule)
def cleanup_module_on_coursemodule_delete(sender, instance, **kwargs):
    """
    После удаления связи CourseModule, если этого Module больше нигде нет —
    удаляем и сам Module.
    """
    module_obj = instance.module_id
    if not CourseModule.objects.filter(module_id=module_obj).exists():
        module_obj.delete()

@receiver(post_delete, sender=TestQuestion)
def cleanup_questions_on_testquestion_delete(sender, instance, **kwargs):
    """
    После удаления TestQuestion, если эти Question больше не используются  —
    удаляем и сами Question.
    """
    q = instance.question_id
    if not TestQuestion.objects.filter(question_id=q).exists():
        q.delete()