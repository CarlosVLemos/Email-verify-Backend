from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Executado quando o Django inicializa"""

        if not settings.USE_REDIS:
            self.create_cache_table()

    def create_cache_table(self):
        """Cria a tabela de cache se não existir"""
        try:
            from django.core.management import call_command
            from django.db import connection
            table_name = 'django_cache_table'
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=%s",
                    [table_name]
                )
                if not cursor.fetchone():

                    call_command('createcachetable', verbosity=0)
                    print(f"✅ Cache table '{table_name}' created successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not create cache table: {e}")

