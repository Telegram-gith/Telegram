from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Запустить бота / перезапустить бота'
        ),
        BotCommand(
            command='language',
            description='Изменить язык'
        ),
        BotCommand(
            command='catalog',
            description='Каталог'
        ),
        BotCommand(
            command='order',
            description='Посмотреть заказы'
        ),
        BotCommand(
            command='basket',
            description='Корзина'
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
