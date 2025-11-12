# Celery configuration - DISABLED
# Uncomment this file when you need async tasks
#
# import os
# from celery import Celery
# from celery.schedules import crontab
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
#
# app = Celery('core')
#
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# app.autodiscover_tasks()
#
# app.conf.beat_schedule = {
#     'cleanup-old-analytics': {
#         'task': 'analytics.tasks.cleanup_old_analytics',
#         'schedule': crontab(hour=2, minute=0),
#     },
#     'update-trending-keywords': {
#         'task': 'analytics.tasks.update_trending_keywords',
#         'schedule': crontab(hour='*/6'),
#     },
# }
#
# @app.task(bind=True, ignore_result=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')

