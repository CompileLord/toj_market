import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings') 
django.setup()

BOT_TOKEN = os.getenv('BOT_TOKEN')

import asyncio
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, DecimalField, F
from django.db.models.functions import Coalesce
from asgiref.sync import sync_to_async

from aiogram import Dispatcher, Bot, F as AF, types
from aiogram.types import (Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton, FSInputFile)
from aiogram.filters import Command, CommandObject

from market.models import Shop, Product, Order, ImageProduct

User = get_user_model()

class Keyboards:
    @staticmethod
    def get_main_keyboard():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="💳 Orders"), KeyboardButton(text="⌛ Last my products")],
                [KeyboardButton(text="🛍️ My shop"), KeyboardButton(text="🗿 My profile")],
                [KeyboardButton(text="🔙 Logout")]
            ],
            resize_keyboard=True
        )

    @staticmethod
    def get_order_status_keyboard(order_id):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⏳ Pending", callback_data=f"ord_st:pending:{order_id}"),
                    InlineKeyboardButton(text="💳 Paid", callback_data=f"ord_st:paid:{order_id}"),
                ],
                [
                    InlineKeyboardButton(text="📦 Delivered", callback_data=f"ord_st:delivered:{order_id}"),
                    InlineKeyboardButton(text="❌ Canceled", callback_data=f"ord_st:cancel:{order_id}"),
                ],
                [InlineKeyboardButton(text="🚚 Shipped", callback_data=f"ord_st:shipped:{order_id}")]
            ]
        )

    @staticmethod
    def get_product_manage_keyboard(product_id):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🗑️ Delete Product", callback_data=f"prod_del:{product_id}")]
            ]
        )

class DB:
    @staticmethod
    @sync_to_async
    def get_user_by_tg_id(tg_id):
        return User.objects.filter(telegram_id=tg_id).first()

    @staticmethod
    @sync_to_async
    def get_last_orders(user):
        return list(
            Order.objects.filter(product__shop__seller=user)
            .exclude(status='delivered')
            .select_related('product')
            .order_by('-created_at')[:10]
        )

    @staticmethod
    @sync_to_async
    def get_shop_info(user):
        return Shop.objects.annotate(
            avg_crowns=Coalesce(Avg('products__product_crowns__crowns'), 0, output_field=DecimalField()),
            total_products=Count('products', distinct=True),
            total_orders=Count('products__orders', distinct=True)
        ).select_related('seller').filter(seller=user).first()

    @staticmethod
    @sync_to_async
    def get_last_products_with_images(user):
        products = Product.objects.filter(shop__seller=user).order_by('-created_at')[:10]
        result = []
        for prod in products:
            image_obj = prod.images.filter(is_main_image=True).first()
            if not image_obj:
                image_obj = prod.images.first()
            
            image_path = None
            if image_obj and image_obj.image:
                image_path = os.path.join(settings.MEDIA_ROOT, str(image_obj.image))
            
            result.append({
                'id': prod.id,
                'title': prod.title,
                'price': prod.price,
                'image_path': image_path
            })
        return result

    @staticmethod
    @sync_to_async
    def delete_product(product_id, user_tg_id):
        deleted_count, _ = Product.objects.filter(id=product_id, shop__seller__telegram_id=user_tg_id).delete()
        return deleted_count > 0

    @staticmethod
    @sync_to_async
    def update_order_status(order_id, status):
        return Order.objects.filter(id=order_id).update(status=status)

    @staticmethod
    @sync_to_async
    def identify_token(token):
        return User.objects.filter(telegram_token=token).first()

    @staticmethod
    @sync_to_async
    def save_tg_id(user, tg_id):
        user.telegram_id = tg_id
        user.token_telegram = None
        user.save()

    @staticmethod
    @sync_to_async
    def logout_user(tg_id):
        User.objects.filter(telegram_id=tg_id).update(telegram_id=None)

class MarketBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()
        self._register_handlers()

    def _register_handlers(self):
        self.dp.message.register(self.start, Command(commands=['start']))
        self.dp.message.register(self.show_my_orders, AF.text == "💳 Orders")
        self.dp.message.register(self.show_my_products, AF.text == "⌛ Last my products")
        self.dp.message.register(self.show_my_profile, AF.text == "🗿 My profile")
        self.dp.message.register(self.show_my_shop, AF.text == "🛍️ My shop")
        self.dp.message.register(self.logout, AF.text == "🔙 Logout")

        self.dp.callback_query.register(self.process_status_change, AF.data.startswith("ord_st:"))
        self.dp.callback_query.register(self.process_delete_product, AF.data.startswith("prod_del:"))


    async def start(self, message: Message, command: CommandObject):
        user_exists = await DB.get_user_by_tg_id(message.from_user.id)
        if user_exists:
            await message.answer(f"Welcome back, {user_exists.first_name}! 👋", reply_markup=Keyboards.get_main_keyboard())
            return

        if command.args:
            user = await DB.identify_token(command.args)
            if user:
                await DB.save_tg_id(user, message.from_user.id)
                await message.answer(f"✅ Auth successful! Welcome {user.first_name}", reply_markup=Keyboards.get_main_keyboard())
            else:
                await message.answer("❌ Invalid or expired token.")
        else:
            await message.answer("🔑 Please login via the website link.")

    async def show_my_orders(self, message: Message):
        user = await DB.get_user_by_tg_id(message.from_user.id)
        if not user:
            await message.answer("🔑 Please login via the website link.")
            return
        if user.role != 'SL':
             await message.answer("❌ You are not a seller.")
             return

        orders = await DB.get_last_orders(user)
        if not orders:
            await message.answer("📭 No orders found.")
            return

        for order in orders:
            prod_name = order.product.title if order.product else "Deleted Product"
            
            text = (
                f"📑 **Order #{order.id}**\n"
                f"📦 Product: {prod_name}\n"
                f"💰 Total: {order.total_amount}\n" 
                f"✨ Status: {order.status}"
            )
            await message.answer(
                text,
                reply_markup=Keyboards.get_order_status_keyboard(order.id),
                parse_mode="Markdown"
            )

    async def show_my_shop(self, message: Message):
        user = await DB.get_user_by_tg_id(message.from_user.id)
        if not user or user.role != 'SL':
            await message.answer("❌ You are not a seller or not logged in.")
            return

        shop = await DB.get_shop_info(user)
        if not shop:
            await message.answer("❌ You don't have a shop yet.")
            return

        await message.answer(
            f"🛒 **Shop Info**\n\n"
            f"📦 Name: {shop.title}\n"
            f"👑 Avg. Crowns: {shop.avg_crowns}\n"
            f"🛒 Total Products: {shop.total_products}\n"
            f"📦 Total Orders: {shop.total_orders}",
            parse_mode="Markdown"
        )

    async def show_my_products(self, message: Message):
        user = await DB.get_user_by_tg_id(message.from_user.id)
        if not user or user.role != 'SL':
            await message.answer("❌ You are not a seller.")
            return

        products_data = await DB.get_last_products_with_images(user)
        
        if not products_data:
            await message.answer("❌ No products found.")
            return

        for prod in products_data:
            caption = f"📦 {prod['title']}\n🏷️ Price: {prod['price']}"
            keyboard = Keyboards.get_product_manage_keyboard(prod['id'])
            
            file_path = prod['image_path']
            if file_path and os.path.exists(file_path):
                try:
                    await message.answer_photo(
                        photo=FSInputFile(file_path),
                        caption=caption,
                        reply_markup=keyboard
                    )
                except Exception as e:
                    await message.answer(f"{caption}\n(Image error: {e})", reply_markup=keyboard)
            else:
                await message.answer(caption, reply_markup=keyboard)

    async def show_my_profile(self, message: Message):
        user = await DB.get_user_by_tg_id(message.from_user.id)
        if not user:
            await message.answer("🔑 Please login.")
            return
        text = f"👤 **Profile**\n\n📛 Name: {user.first_name}\n📧 Email: {user.email}\n🆔 ID: {user.telegram_id}"

        if user.avatar:
            file_path = os.path.join(settings.MEDIA_ROOT, str(user.avatar))
            if os.path.exists(file_path):
                try:
                    await message.answer_photo(photo=FSInputFile(file_path), caption=text, parse_mode="Markdown")
                    return
                except Exception as e:
                    print(f"Error sending profile photo: {e}")
        
        await message.answer(text, parse_mode="Markdown")

    async def process_status_change(self, callback: CallbackQuery):
        _, status, order_id = callback.data.split(":")
        await DB.update_order_status(order_id, status)
        await callback.answer(f"Status updated to {status}")
    
        try:
            current_text = callback.message.caption if callback.message.caption else callback.message.text
           
            await callback.message.edit_reply_markup(reply_markup=Keyboards.get_order_status_keyboard(order_id))
        except Exception:
            pass 

    async def process_delete_product(self, callback: CallbackQuery):
        product_id = callback.data.split(":")[1]
        user_tg_id = callback.from_user.id
        
        success = await DB.delete_product(product_id, user_tg_id)
        
        if success:
            await callback.answer("✅ Product deleted!")
            await callback.message.delete()
        else:
            await callback.answer("❌ Error: Could not delete product (maybe it's not yours).")

    async def logout(self, message: Message):
        user = await DB.get_user_by_tg_id(message.from_user.id)
        if user:
            await DB.logout_user(message.from_user.id)
        await message.answer("🔌 Logged out successfully.", reply_markup=types.ReplyKeyboardRemove())

    async def run(self):
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)

if __name__ == '__main__':
    bot_app = MarketBot()
    try:
        print("Bot started...")
        asyncio.run(bot_app.run())
    except KeyboardInterrupt:
        print("Bot turned off safely.")