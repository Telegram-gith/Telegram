import os
import json
import dotenv
from gspread_asyncio import AsyncioGspreadClientManager
from oauth2client.service_account import ServiceAccountCredentials
dotenv.load_dotenv()


def get_google_credentials():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials_json = os.getenv("GOOGLE_SHEET_CREDENTIALS")  # Получение JSON из переменной окружения
    creds_data = json.loads(credentials_json)  # Преобразование строки в JSON
    return ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)


async def get_google_sheet():
    def creds_func():
        return get_google_credentials()  # Возвращаем функцию для создания учётных данных

    agcm = AsyncioGspreadClientManager(creds_func)
    client = await agcm.authorize()  # Авторизация асинхронного клиента
    spreadsheet = await client.open("Telegram")
    sheet = await spreadsheet.get_worksheet(0)  # Получаем первый лист
    return sheet


async def ensure_headers(sheet, headers):
    existing_headers = await sheet.row_values(1)
    if existing_headers != headers:
        await sheet.insert_row(headers, index=1)


async def write_order_to_sheet(order_data):
    try:
        sheet = await get_google_sheet()
        headers = ["Order ID", "Order Date", "Sum Order", "Product", "Quantity", "Telegram ID",
                   "First Name", "Last Name", "Phone", "Status"]
        await ensure_headers(sheet, headers)
        await sheet.append_row(order_data)
        print(f"Заказ {order_data[0]} успешно записан в Google Sheets.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Example usage
# asyncio.run(write_order_to_sheet(["123", "2023-01-01", "500", "Product A", "2", "123456789",
#                                   "John", "Doe", "+1234567890", "Pending"]))
