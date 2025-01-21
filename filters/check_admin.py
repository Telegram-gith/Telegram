from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from database.Database import DataBase


class CheckAdmin(BaseFilter):
    async def __call__(self, obj: [Message, CallbackQuery]) -> bool:
        try:
            db = DataBase()  # Initialize the database connection
            admins = await db.get_admins()  # Dynamically fetch the current list of admin IDs
            admin_ids = [str(admin.telegram_id) for admin in admins]  # Ensure IDs are strings

            # Check if the user ID is in the list of admin IDs, handling both Message and CallbackQuery
            user_id = str(obj.from_user.id) if isinstance(obj, (Message, CallbackQuery)) else None
            return user_id in admin_ids if user_id else False
        except Exception as e:
            print(f"Error in CheckAdmin filter: {e}")
            return False
    # async def __call__(self, message: Message) -> bool:
    #     try:
    #         db = DataBase()  # Initialize the database connection
    #         # Dynamically fetch the current list of admin IDs
    #         admins = await db.get_admins()
    #         admin_ids = [str(admin.telegram_id) for admin in admins]  # Ensure IDs are strings
    #         # Check if the user's Telegram ID is in the list of admin IDs
    #         return str(message.from_user.id) in admin_ids
    #     except Exception as e:
    #         print(f"Error in CheckAdmin filter: {e}")
    #         return False


class CheckSuperAdmin(BaseFilter):
    def __init__(self, super_admin_id):
        self.super_admin_id = super_admin_id  # Predefined super_admin Telegram ID

    async def __call__(self, message: Message):
        try:
            # Check if the user's Telegram ID matches the super_admin ID
            print(message.from_user.id == int(self.super_admin_id))
            return message.from_user.id == int(self.super_admin_id)
        except Exception as e:
            print(e)
            return False
