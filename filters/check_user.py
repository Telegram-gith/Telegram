from aiogram.types import Message
from aiogram.filters import BaseFilter
from database.Database import DataBase


class CheckUser(BaseFilter):
    def __init__(self, message: Message):
        self.user_id = str(message.from_user.id)  # Store the user ID

    async def __call__(self, message: Message) -> bool:
        try:
            db = DataBase()  # Initialize the database connection
            users = await db.get_users()  # Fetch all admins from the database
            user_ids = [str(user.telegram_id) for user in users]  # Ensure IDs are strings

            # Check if the user's Telegram ID is NOT in the list of admin IDs
            return self.user_id not in user_ids
        except Exception as e:
            print(f"Error in CheckUser filter: {e}")
            return False
