"""
Views for api app.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'django-backend',
        'timestamp': '2025-08-11T16:00:00Z'
    })

@csrf_exempt
def status(request):
    """Status endpoint."""
    return JsonResponse({
        'status': 'operational',
        'service': 'django-backend',
        'endpoints': ['health', 'status']
    })