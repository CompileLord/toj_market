from django.core.management.base import BaseCommand
import asyncio
from telegram_bot import bot_logic

class Command(BaseCommand):
    help = "Runs the aiogram bot"

    def handle(self, *args, **options):
        try:
            asyncio.run(bot_logic.start())
        except KeyboardInterrupt:
            pass