"""
Email utility functions for the delivery tracking system.
"""
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_tracking_notification(recipient_email, tracking_number, status, delivery_info=None):
    """
    Send tracking status notification email.
    
    Args:
        recipient_email (str): Email address of the recipient
        tracking_number (str): Tracking number
        status (str): Current delivery status
        delivery_info (dict): Additional delivery information
    """
    try:
        subject = f'Delivery Update - Tracking #{tracking_number}'
        
        # Create email content
        context = {
            'tracking_number': tracking_number,
            'status': status,
            'delivery_info': delivery_info or {},
            'site_url': settings.SITE_URL,
        }
        
        # Render HTML email template
        html_message = render_to_string('emails/tracking_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Tracking notification sent to {recipient_email} for tracking #{tracking_number}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send tracking notification: {str(e)}")
        return False


def send_delivery_confirmation(recipient_email, tracking_number, delivery_details):
    """
    Send delivery confirmation email.
    
    Args:
        recipient_email (str): Email address of the recipient
        tracking_number (str): Tracking number
        delivery_details (dict): Delivery details including date, time, location
    """
    try:
        subject = f'Delivery Confirmed - Tracking #{tracking_number}'
        
        context = {
            'tracking_number': tracking_number,
            'delivery_details': delivery_details,
            'site_url': settings.SITE_URL,
        }
        
        html_message = render_to_string('emails/delivery_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Delivery confirmation sent to {recipient_email} for tracking #{tracking_number}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send delivery confirmation: {str(e)}")
        return False


def send_investment_notification(recipient_email, investment_details):
    """
    Send investment-related notification email.
    
    Args:
        recipient_email (str): Email address of the recipient
        investment_details (dict): Investment details
    """
    try:
        subject = f'Investment Update - {investment_details.get("type", "Notification")}'
        
        context = {
            'investment_details': investment_details,
            'site_url': settings.SITE_URL,
        }
        
        html_message = render_to_string('emails/investment_notification.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Investment notification sent to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send investment notification: {str(e)}")
        return False


def send_custom_email(recipient_email, subject, message, html_message=None):
    """
    Send a custom email.
    
    Args:
        recipient_email (str): Email address of the recipient
        subject (str): Email subject
        message (str): Plain text message
        html_message (str): HTML message (optional)
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Custom email sent to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send custom email: {str(e)}")
        return False


def test_email_configuration():
    """
    Test email configuration by sending a test email to admin.
    """
    try:
        subject = 'Email Configuration Test'
        message = 'This is a test email to verify your email configuration is working correctly.'
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        
        logger.info("Email configuration test successful")
        return True
        
    except Exception as e:
        logger.error(f"Email configuration test failed: {str(e)}")
        return False
