import os
import threading
import asyncio
from django.conf import settings


def start_bot_notification(instance):
    try:
        order_items = instance.items.select_related('product__shop__seller').prefetch_related('product__images').all()
        sellers_data = {}

        for item in order_items:
            seller = item.product.shop.seller
            if seller.id not in sellers_data:
                sellers_data[seller.id] = {
                    'tg_id': seller.telegram_id,
                    'items': [],
                    'total': 0,
                    'photo_path': None
                }
            
            s_data = sellers_data[seller.id]
            s_data['items'].append(f"{item.product.title} x {item.quantity}")
            s_data['total'] += item.price_at_purchase * item.quantity

            if not s_data['photo_path'] and item.product.images.exists():
                image_name = item.product.images.first().image.name
                s_data['photo_path'] = os.path.join(settings.MEDIA_ROOT, image_name)

        customer_name = instance.user.get_full_name()
        created_at_str = instance.created_at.strftime('%Y-%m-%d %H:%M')
        order_id = instance.id

    except Exception as e:
        print(f"Error preparing bot notification data: {e}")
        return

    def run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        tasks = []
        for s_data in sellers_data.values():
            if s_data['tg_id']:
                products_str = "\n".join(s_data['items'])
                tasks.append(_send_telegram_async(
                    s_data['tg_id'],
                    products_str,
                    customer_name,
                    s_data['total'],
                    created_at_str,
                    order_id,
                    s_data['photo_path']
                ))
        
        if tasks:
            loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

    threading.Thread(target=run_loop, daemon=True).start()


async def _send_telegram_async(seller_tg_id, products_str, customer_name, total_amount, created_at_str, order_id, photo_path):
    from aiogram import Bot
    from aiogram.types import FSInputFile
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("BOT_TOKEN is missing")
        return

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    message = (
        f"🎉 New Order Received! 🎉\n\n"
        f"Order ID: {order_id}\n"
        f"Products:\n{products_str}\n"
        f"Customer: {customer_name}\n"
        f"Your Earnings: ${total_amount}\n"
        f"Order Date: {created_at_str}\n"
    )

    try:
        if photo_path and os.path.exists(photo_path):
            await bot.send_photo(chat_id=seller_tg_id, photo=FSInputFile(photo_path), caption=message)
        else:
            await bot.send_message(chat_id=seller_tg_id, text=message)
    except Exception as e:
        print(f"Bot Sending Error: {e}")
    finally:
        await bot.session.close()

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import ImageProduct, ProductImageEmbedding
# from PIL import Image
# from sentence_transformers import SentenceTransformer
# import numpy as np
#
# try:
#     embedding_model = SentenceTransformer('clip-ViT-B-32')
# except Exception as e:
#     print(f"Warning: Could not load embedding model: {e}")
#     embedding_model = None
#
# @receiver(post_save, sender=ImageProduct)
# def create_image_embedding(sender, instance, created, **kwargs):
#     if created and instance.image and embedding_model:
#         try:
#             image_path = instance.image.path
#             if not os.path.exists(image_path):
#                  return
#
#             img = Image.open(image_path)
#             embedding = embedding_model.encode(img)
#
#             ProductImageEmbedding.objects.create(
#                 product_image=instance,
#                 embedding=embedding.tolist()
#             )
#         except Exception as e:
#             print(f"Error creating embedding for image {instance.id}: {e}")