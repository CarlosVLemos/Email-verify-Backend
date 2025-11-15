from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from .models import EmailAnalytics
@shared_task(bind=True, max_retries=3)
def cleanup_old_analytics(self):
    try:
        cutoff_date = timezone.now() - timedelta(days=90)
        deleted_count, _ = EmailAnalytics.objects.filter(
            processed_at__lt=cutoff_date
        ).delete()
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
@shared_task(bind=True, max_retries=3)
def update_trending_keywords(self):
    try:
        from datetime import timedelta
        from django.utils import timezone
        from django.db.models import Count, Q
        last_7_days = timezone.now() - timedelta(days=7)
        last_30_days = timezone.now() - timedelta(days=30)
        productive_keywords = []
        unproductive_keywords = []
        emails_7d = EmailAnalytics.objects.filter(processed_at__gte=last_7_days)
        emails_30d = EmailAnalytics.objects.filter(processed_at__gte=last_30_days)
        for email in emails_7d:
            if email.keywords_detected:
                if email.category == 'Produtivo':
                    productive_keywords.extend(email.keywords_detected)
                else:
                    unproductive_keywords.extend(email.keywords_detected)
        from collections import Counter
        productive_counter = Counter(productive_keywords)
        unproductive_counter = Counter(unproductive_keywords)
        cache.set('trending_productive_keywords', dict(productive_counter.most_common(20)), 3600)
        cache.set('trending_unproductive_keywords', dict(unproductive_counter.most_common(20)), 3600)
        return {
            'status': 'success',
            'productive_keywords_count': len(productive_counter),
            'unproductive_keywords_count': len(unproductive_counter)
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
@shared_task
def process_email_batch_async(emails_data):
    from classifier.email_scripts import EmailClassifier
    classifier = EmailClassifier()
    results = []
    for idx, email_text in enumerate(emails_data):
        try:
            result = classifier.classify_email(email_text)
            results.append({
                'email_id': idx + 1,
                'status': 'success',
                'classification': result
            })
        except Exception as e:
            results.append({
                'email_id': idx + 1,
                'status': 'error',
                'error': str(e)
            })
    return results
@shared_task
def generate_executive_summary_async(email_text, max_sentences=3):
    from classifier.email_scripts import ExecutiveSummarizer
    summarizer = ExecutiveSummarizer()
    return summarizer.generate_summary(email_text, max_sentences=max_sentences)
@shared_task
def warm_cache_dashboard():
    from .views import DashboardOverviewView
    from rest_framework.test import APIRequestFactory
    factory = APIRequestFactory()
    request = factory.get('/api/analytics/dashboard/overview/')
    view = DashboardOverviewView.as_view()
    response = view(request)
    return {
        'status': 'success',
        'cache_warmed': True
    }
