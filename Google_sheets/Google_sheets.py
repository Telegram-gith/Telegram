import aiohttp
from asyncio import Lock

order_queue = []  # Очередь для хранения заказов
queue_lock = Lock()  # Блокировка для предотвращения одновременного доступа

SCRIPT_URL = \
    "https://script.google.com/macros/s/AKfycbxh7ctwGrODrPa98ZVITu92pdxtRozhQFjhAvADdtCLqK2h3bEBiWSE-mOYwF5uhlGy/exec"


async def add_order_to_queue(order_data):
    async with queue_lock:
        order_queue.append(order_data)  # Добавляем новый заказ в очередь
        if len(order_queue) > 15:  # Если в очереди больше 10 заказов, удаляем старые
            order_queue.pop(0)
    if len(order_queue) >= 10:  # Если в очереди накопилось 10 заказов, отправляем их
        await process_order_queue()


async def process_order_queue():
    async with queue_lock:
        orders_to_send = order_queue[-10:]  # Берем последние 10 заказов
        order_queue.clear()  # Очищаем очередь после отправки
    await send_orders_to_google_sheets(orders_to_send)


async def send_orders_to_google_sheets(orders):
    data = {"orders": orders}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(SCRIPT_URL, json=data) as response:
                if response.status == 200:
                    print("Заказы успешно отправлены")
                else:
                    print(f"Ошибка {response.status}: {await response.text()}")
        except Exception as e:
            print(f"Ошибка соединения: {e}")
