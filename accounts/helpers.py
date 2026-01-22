from django.core.mail import send_mail
from django.utils.html import strip_tags

def send_verification_email(email, code):
    subject = 'Verify your TojMarket account'
    
    # Modern HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f7f9;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="100%" style="max-width: 500px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                        <tr>
                            <td style="padding: 40px; text-align: center;">
                                <h1 style="margin: 0; font-size: 24px; color: #1a1a1a; letter-spacing: -0.5px;">Toj<span style="color: #ffdf53;">Market</span></h1>
                                <div style="height: 1px; background-color: #e5e7eb; margin: 24px 0;"></div>
                                <p style="font-size: 16px; color: #4b5563; line-height: 24px; margin-bottom: 32px;">
                                    Hello! Use the verification code below to secure your account.
                                </p>
                                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin-bottom: 32px;">
                                    <span style="font-family: monospace; font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #ffae00;">{code}</span>
                                </div>
                                <p style="font-size: 13px; color: #9ca3af;">
                                    This code is valid for 10 minutes. If you didn't request this, please ignore this email.
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px; background-color: #f9fafb; text-align: center; border-top: 1px solid #f3f4f6;">
                                <p style="margin: 0; font-size: 12px; color: #6b7280;">&copy; 2026 Toj<span style="color: #ffdf53;">Market</span> Inc.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    send_mail(
        subject,
        f'Your verification code is: {code}',
        'noreply@tojmarket.com',
        [email],
        html_message=html_content,
        fail_silently=False,
    )


from django.core.mail import send_mail
from django.utils.html import strip_tags

def send_welcome_message(email, full_name):
    subject = 'Welcome to TojMarket'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin: 0; padding: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f9fafb;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="padding: 50px 20px;">
            <tr>
                <td align="center">
                    <table width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: left;">
                                <h1 style="margin: 0; font-size: 28px; color: #ffffff; letter-spacing: -1px;">
                                    Toj<span style="color: #ebba25;">Market</span>
                                </h1>
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="padding: 0 40px 40px 40px;">
                                <h2 style="font-size: 22px; color: #1f2937; margin-top: 0;">Welcome, {full_name}! 👋</h2>
                                <p style="font-size: 16px; color: #4b5563; line-height: 1.6; margin-bottom: 25px;">
                                    We're thrilled to have you join the TojMarket community. Whether you're here to find great deals or start selling, we've got you covered.
                                </p>
                                
                                <div style="text-align: left; margin-bottom: 35px;">
                                    <a href="https://tojmarket.com" style="background-color: #ebba25; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 10px; font-weight: 600; display: inline-block;">
                                        Explore the Market
                                    </a>
                                </div>
                                
                                <p style="font-size: 14px; color: #6b7280; margin: 0; border-top: 1px solid #f3f4f6; padding-top: 20px;">
                                    Need help? Just reply to this email. Our team is always here for you.
                                </p>
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="padding: 30px 40px; background-color: #f3f4f6; text-align: center;">
                                <p style="margin: 0; font-size: 12px; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px;">
                                    &copy; 2026 TojMarket Ltd. • Dushanbe, Tajikistan
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_content)
    
    send_mail(
        subject,
        plain_message,
        'welcome@tojmarket.com',
        [email],
        html_message=html_content,
        fail_silently=False,
    )
