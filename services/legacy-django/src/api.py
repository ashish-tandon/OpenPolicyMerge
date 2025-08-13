"""
API endpoints for Legacy Django Service
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_status(request):
    """API status endpoint"""
    return JsonResponse({
        "status": "active",
        "service": "legacy-django",
        "version": "1.0.0",
        "port": 9022
    })

@csrf_exempt
def api_health(request):
    """Health check endpoint"""
    return JsonResponse({
        "status": "healthy",
        "service": "legacy-django"
    })
