from django.shortcuts import render


def landing_page(request):
    """Public landing page for customers"""
    return render(request, 'tracking/landing_page.html')
