import os
import django
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

from aiogram import Dispatcher, Bot, F
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

User = get_user_model()






class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        tg_id = event.from_user.id
        user = await sync_to_async(
            User.objects.filter(telegram_id=tg_id).select_related('shop').first
        )()
        data['django_user'] = user
        return await handler(event, data)


class SellerBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self._register_handlers()


    # registering handlers and commands
    def _register_handlers(self):
        self.dp.message.register(self.start_handler, CommandStart(deep_link=True))
        self.dp.message.register(self.help_command_handler, Command('/help'))
        # self.dp.message.register(self.add_product_handler, Command('/add_product'))
        # self.dp.message.register(self.view_products_handler, Command('/view_products'))
        # self.dp.message.register(self.view_categories_handler, Command('/view_categories'))



        self.dp.message.outer_middleware(AuthMiddleware())
        self.dp.callback_query.outer_middleware(AuthMiddleware())

    #verify user first
    @sync_to_async
    def _verify_user(self, token, telegram_id):
        try:
            user = User.objects.get(telegram_token=token)
            if user:
                user.telegram_id = telegram_id
                user.telegram_token = None
                user.save()
                return user
        except User.DoesNotExist:
            return None
    
    # start command and saving his telegram id in the django if token valid
    async def start_handler(self, message: Message, command: CommandObject, django_user: User = None):
        token = command.args
        if token:
            user = await self._verify_user(token, message.from_user.id)
            if user:
                return await message.answer(
                    f"🌟 Hello {user.first_name}!\n"
                    "Your Telegram has been linked successfully. You can now create a shop."
                )
            else:
                return await message.answer("❌ Invalid or expired link.")
        if django_user:
            return await message.answer(
                f"👋 Welcome back, {django_user.first_name}!\n"
                "You are already linked. Use the menu below to manage your shop."
            )
        await message.answer(
            "🚫 Account not linked.\n"
            "Please log in to the website and click 'Connect Telegram'."
        )
    
    # help command for giving info
    async def help_command_handler(self, message: Message, django_user: User = None):
        
        if not django_user:
            return await message.answer(
                "Hello there!👋 I'm a bot that helps you manage your online shop. "
                "To get started, please log in to the website and click 'Connect Telegram'."
            )
        
        return await message.answer(
            "Here are some of the commands you can use with this bot:\n"
            "/view_products - View all products in your shop.\n"
            "/view_categories - View all categories in your shop.\n"
            "/delete_product - Delete a product from your shop.\n"
            )

    # add product
    async def add_product_handler(self, message: Message, django_user: User = None):
        if not django_user:
            return await message.answer(
                f"To get started, please log in to the website and click 'Connect Telegram'."
            )

        shop = django_user.shop

    

    async def start_polling(self):
        print("Bot is running...")
        await self.dp.start_polling(self.bot)





if __name__ == "__main__":
    seller_bot = SellerBot(os.getenv('BOT_TOKEN'))
    
    import asyncio
    asyncio.run(seller_bot.start_polling())
