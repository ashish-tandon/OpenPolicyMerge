"""
Views for core app.
"""
from django.shortcuts import render
from django.http import JsonResponse

def home(request):
    """Home page view."""
    return JsonResponse({
        'message': 'OpenPolicyMerge Django Backend',
        'status': 'operational',
        'service': 'core'
    })
    