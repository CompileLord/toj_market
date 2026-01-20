import random
from django.core.mail import send_mail
from django.conf import settings

def send_verification_code(user_email):
    code = str(random.randint(100000, 999999))
    
    subject = 'Your Verification Code'
    message = f'Your authorization code is: {code}. It will expire in 10 minutes.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    
    send_mail(subject, message, email_from, recipient_list)
    return code

