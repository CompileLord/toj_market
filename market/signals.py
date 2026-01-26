import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
import asyncio
from .models import Order

@receiver(post_save, sender=Order)
def notify_seller_on_new_order(sender, instance, created, **kwargs):
    if created:
        seller = instance.product.shop.seller 
        
        if seller and seller.telegram_id:
            bot_token = os.getenv('BOT_TOKEN')
            
            if not bot_token:
                print("Warning: BOT_TOKEN not set in environment variables")
                return
            
            message = (
                f"🎉 New Order Received! 🎉\n\n"
                f"Order ID: {instance.id}\n"
                f"Product: {instance.product.title}\n"
                f"Customer: {instance.user.first_name} {instance.user.last_name}\n"
                f"Total Amount: ${instance.total_amount}\n"
                f"Status: {instance.get_status_display()}\n\n"
                f"Order Date: {instance.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"View details on your dashboard."
            )
            
            try:
                from aiogram import Bot
                from aiogram.client.default import DefaultBotProperties
                from aiogram.enums import ParseMode
                
                async def send_telegram_message():
                    bot = Bot(
                        token=bot_token,
                        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
                    )
                    try:
                        await bot.send_message(
                            chat_id=seller.telegram_id,
                            text=message,
                            parse_mode=None  
                        )
                    except Exception as e:
                        print(f"Failed to send Telegram notification: {e}")
                    finally:
                        await bot.session.close()
                async_to_sync(send_telegram_message)()
                
            except ImportError:
                print("aiogram is not installed. Install with: pip install aiogram")
            except Exception as e:
                print(f"Error sending Telegram notification: {e}")