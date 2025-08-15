from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_thank_you_email(participation_id, user_email):
    subject = "Thank you for contributing to recording horse racing history."
    message = "Thank you for your contribution. Your data is appreciated."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    return send_mail(subject, message, from_email, recipient_list)