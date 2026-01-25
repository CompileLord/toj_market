import os
import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from .models import Order

@receiver(post_save, sender=Order)
def notify_seller_on_new_order(sender, instance, created, **kwargs):
    if created:
        seller = instance.shop.seller
        if seller.telegram_id:
            bot_token = os.getenv('BOT_TOKEN')
            bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            message = (
                f"🎉 New Order Received! 🎉\n\n"
                f"Order ID: {instance.id}\n"
                f"Customer: {instance.customer.first_name} {instance.customer.last_name}\n"
                f"Total Price: {instance.total_price}\n\n"
                f"You can view the order details on the website."
            )
            
            async def send_notification():
                await bot.send_message(chat_id=seller.telegram_id, text=message)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(send_notification())

