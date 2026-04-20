import logging
import warnings
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from .models import User

# Отключаем предупреждение о доступе к БД во время инициализации приложений
warnings.filterwarnings(
    "ignore",
    message="Accessing the database during app initialization.*",
    category=RuntimeWarning,
)

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(job_defaults={'misfire_grace_time': 30, 'coalesce': False})

# 1) Функция, которая удалит одного пользователя
@util.close_old_connections
def delete_unconfirmed_users():
    hours = getattr(settings, 'UNCONFIRMED_USER_EXPIRATION_HOURS', 24)
    cutoff = timezone.now() - timedelta(hours=hours)
    users = User.objects.filter(email_confirmed=False, date_joined__lt=cutoff)
    count, _ = users.delete()
    logger.info(f"🗑️ Deleted {count} unconfirmed users older than {hours}h")

@util.close_old_connections
def delete_old_job_executions(max_age_seconds=7*24*3600):
    """
    Удаляет из django_apscheduler_djangojobexecution 
    записи старше указанного времени (в секундах).
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age_seconds)
    logger.info(f"🧹 Cleaned up APScheduler executions older than "
                f"{max_age_seconds // 3600}h")

# 2) Инициализация и старт планировщика
def start():
    scheduler.add_jobstore(DjangoJobStore(), 'default')
    hours = getattr(settings, 'UNCONFIRMED_USER_EXPIRATION_HOURS', 24)
    scheduler.add_job(
        delete_unconfirmed_users,
        trigger=IntervalTrigger(hours=hours),
        id="cleanup_unconfirmed_users",
        name="Cleanup unconfirmed users",
        replace_existing=True,
        next_run_time=timezone.now(),
    )
    scheduler.add_job(
        delete_old_job_executions,
        trigger=IntervalTrigger(days=7),
        id="cleanup_job_executions",
        name="Cleanup old APScheduler executions",
        replace_existing=True,
        next_run_time=timezone.now(),
    )
    scheduler.start()
    logger.info("APScheduler started")
