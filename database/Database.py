from sqlalchemy import select, delete, update, desc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.model import *
import os
# from Google_sheets.Google_sheets import send_orders_to_google_sheets


class DataBase:
    def __init__(self):
        self.connect = os.getenv('DATABASE_URL')
        print(f"Connecting to database at {self.connect}")
        self.async_engine = create_async_engine(self.connect)
        self.Session = async_sessionmaker(bind=self.async_engine, class_=AsyncSession)

    async def create_db(self):
        async with self.async_engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)

    async def get_user(self, user_id):
        async with self.Session() as request:
            result = await request.execute(select(Users).where(Users.telegram_id == user_id))
        return result.scalar()

    async def add_language(self, user_id, language):
        async with self.Session() as session:
            result = await session.execute(select(Language).where(Language.telegram_id == user_id))
            existing_entry = result.scalar()
            if existing_entry:  # Обновить язык, если запись уже существует
                existing_entry.user_language = language
            else:  # Добавить новую запись
                session.add(Language(telegram_id=user_id, user_language=language))
            await session.commit()

    async def update_language(self, user_id, language):
        async with self.Session() as session:
            try:
                update_fields = {}
                if language:
                    update_fields["user_language"] = language

                if update_fields:  # Update only if there are fields to update
                    await session.execute(
                        update(Language).where(Language.telegram_id == user_id).values(**update_fields)
                    )
                    await session.commit()
                    print('Success')
            except Exception as e:
                print(f"Error updating admin: {e}")
                await session.rollback()
                return False

    async def get_lang(self, user_id):
        async with self.Session() as session:
            result = await session.execute(select(Language.user_language).where(Language.telegram_id == user_id))
        return result.scalar()

    async def get_users(self):
        async with self.Session() as request:
            result = await request.execute(select(Users))
            return result.scalars().all()

    async def add_user(self, name, surname, phone, telegram_id):
        async with self.Session() as request:
            request.add(Users(
                username=name,
                usersurname=surname,
                userphone=phone,
                telegram_id=telegram_id
            ))
            await request.commit()

    async def get_admin(self, admin_id):
        async with self.Session() as request:
            result = await request.execute(select(Admins).where(Admins.id == admin_id))
        return result.scalar()

    async def get_admin_by_id(self, admin_id):
        async with self.Session() as request:
            result = await request.execute(select(Admins).where(Admins.telegram_id == admin_id))
        return result.scalar()

    async def get_admins(self):
        async with self.Session() as request:
            result = await request.execute(select(Admins))
            return result.scalars().all()

    async def get_table(self, table_name):
        async with self.Session() as request:
            result = await request.execute(select(table_name))
        return result.scalars().all()

    async def add_admin(self, admin_name, telegram_id):
        async with self.Session() as request:
            request.add(Admins(
                username=admin_name,
                telegram_id=telegram_id
            ))
            await request.commit()

    async def update_admin(self, admin_id, username=None, telegram_id=None):
        async with self.Session() as session:
            try:
                update_fields = {}
                if username:
                    update_fields["username"] = username
                if telegram_id:
                    update_fields["telegram_id"] = telegram_id

                if update_fields:  # Update only if there are fields to update
                    await session.execute(
                        update(Admins).where(Admins.id == admin_id).values(**update_fields)
                    )
                    await session.commit()
                    return True
                return False
            except Exception as e:
                print(f"Error updating admin: {e}")
                await session.rollback()
                return False

    async def delete_admin(self, admin_id):
        async with self.Session() as session:
            try:
                await session.execute(delete(Admins).where(Admins.id == admin_id))
                await session.commit()
                return True
            except Exception as e:
                print(f"Error while deleting admin: {e}")
                await session.rollback()
                return False

    async def add_category(self, name):
        async with self.Session() as request:
            request.add(Category(
                name=name
            ))
            await request.commit()

    async def update_category(self, category_id, name):
        async with self.Session() as request:
            try:
                # Build the update statement dynamically
                update_fields = {}
                if name:
                    update_fields['name'] = name  # Add name to fields if provided
                if update_fields:  # Only run the query if there's something to update
                    await request.execute(
                        update(Category).where(Category.id == category_id).values(**update_fields)
                    )
                    await request.commit()
                    return True  # Indicate success
                else:
                    return False  # Nothing to update
            except Exception as e:
                print(f"Error while updating category: {e}")
                await request.rollback()
                return False

    async def delete_category(self, category_id):
        async with self.Session() as request:
            try:
                await request.execute(
                    delete(Category).where(Category.id == category_id)
                )
                await request.commit()
                return True
            except Exception as e:
                print(f"Error while deleting category: {e}")
                await request.rollback()
                return False

    async def get_category_by_id(self, category_id):
        async with self.Session() as request:
            try:
                result = await request.execute(
                    select(Category).where(Category.id == category_id)
                )
                category = result.scalar()
                if category:
                    return category
                return None
            except Exception as e:
                print(f"Error fetching category by ID: {e}")
                return None

    async def add_product(self, name, category_id, images, description, quantity, price, status):
        async with self.Session() as request:
            request.add(Products(
                name=name,
                category_id=category_id,
                images=images,
                description=description,
                quantity=quantity,
                price=price,
                status_product=status))
            await request.commit()

    async def get_product(self, category_id):
        async with self.Session() as request:
            result = await request.execute(select(Products).where(Products.category_id == category_id))
            products = result.scalars().all()
            return products if products else None

    async def get_all_products(self):
        async with self.Session() as request:
            result = await request.execute(select(Products))
        return result.scalars().all()

    async def update_product(self, product_id, name, category_id, images, description,
                             quantity, price, status):
        async with self.Session() as request:
            try:
                # Строим динамическое обновление
                update_fields = {}
                if name:
                    update_fields['name'] = name
                if category_id:
                    update_fields['category_id'] = category_id
                if images:
                    update_fields['images'] = images
                if description:
                    update_fields['description'] = description
                if quantity is not None and str(quantity).isdigit():
                    update_fields['quantity'] = int(quantity)
                if price is not None:  # Проверяем, что цена не None
                    try:
                        # Преобразуем цену в float, если это возможно
                        price = float(price)
                        update_fields['price'] = price
                    except ValueError:
                        print("Ошибка: Цена не является числом с плавающей точкой.")
                        return False
                if status is not None:
                    update_fields['status_product'] = status

                if update_fields:  # Выполняем запрос, если есть что обновить
                    await request.execute(update(Products).where(Products.id == product_id).values(**update_fields))
                    await request.commit()
                    return True  # Успех
                else:
                    return False  # Нечего обновлять
            except Exception as e:
                print(f"Ошибка при обновлении продукта: {e}")
                await request.rollback()
                return False

    async def delete_product(self, product_id):
        async with self.Session() as request:
            try:
                await request.execute(delete(Products).where(Products.id == product_id))
                await request.commit()
                return True
            except Exception as e:
                print(f"Error deleting product: {e}")
                await request.rollback()
                return False

    async def check_basket(self, user_id, product_id):
        async with self.Session() as request:
            result = await request.execute(select(Basket).where(
                (Basket.user_telegram_id == user_id) &
                (Basket.product == product_id)
            ))
        return result.scalars().all()

    async def get_product_one(self, id):
        async with self.Session() as request:
            try:
                result = await request.execute(select(Products).where(Products.id == id))
                return result.scalar()
            except Exception as e:
                print(f"Error fetching product: {e}")
                return None

    async def get_all_categories(self):
        async with self.Session() as request:
            result = await request.execute(select(Category))
        return result.scalars().all()

    async def confirm_product(self, total_price, product_name, quantity, user_id, username, user_surname, user_phone, status):
        async with self.Session() as request:
            request.add(Order(
                sum_order=total_price,
                order_product=product_name,
                order_quantity=quantity,
                user_telegram_id=user_id,
                user_name=username,
                user_surname=user_surname,
                user_phone=user_phone,
                order_status=status
            ))
            await request.commit()

    async def update_product_quantity(self, product_id: int, new_quantity: int):
        async with self.Session() as session:  # Make sure 'self.Session' is an async
            # Using `select` for async queries
            result = await session.execute(select(Products).where(Products.id == product_id))
            product = result.scalar()  # Use `scalars().first()` to get the first object
            if product:
                product.quantity = new_quantity  # Update the quantity
                await session.commit()  # Commit the changes to the database
                return True  # Successfully updated
            else:
                return False  # Product not found

    async def add_basket(self, telegram_id, product, product_quantity, product_sum):
        async with self.Session() as request:
            request.add(Basket(
                user_telegram_id=telegram_id,
                product=product,
                product_quantity=product_quantity,
                product_sum=product_sum
            ))
            await request.commit()

    async def delete_basket_one(self, product_id, user_id, basket_id):
        async with self.Session() as request:
            await request.execute(delete(Basket).where(Basket.product == product_id,
                                                       Basket.user_telegram_id == user_id, Basket.id == basket_id))
            await request.commit()

    async def delete_basket_all(self, user_id):
        async with self.Session() as request:
            await request.execute(delete(Basket).where(Basket.user_telegram_id == user_id))
            await request.commit()

    async def get_basket(self, user_id):
        async with self.Session() as request:
            result = await request.execute(select(Basket).where(
                (Basket.user_telegram_id == user_id)
            ))
            return result.scalars().all()

    async def get_basket_item(self, product_id: int, user_id: str, basket_id):
        async with self.Session() as session:
            result = await session.execute(
                select(Basket).where(
                    Basket.user_telegram_id == user_id, Basket.product == product_id, Basket.id == basket_id
                ))
            return result.scalar()

    async def update_basket(self, user_id, product_id, quantity):
        async with self.Session() as session:
            result = await session.execute(
                select(Basket).where(
                    Basket.user_telegram_id == user_id, Basket.product == product_id
                ))
            basket_item = result.scalar()
            if basket_item:
                basket_item.product_quantity = quantity
                await session.commit()

    async def get_orders(self, user_id):
        async with self.Session() as request:
            result = await request.execute(select(Order).where(
                Order.user_telegram_id == user_id
            ))
            return result.scalars().all()

    async def search_users_by_username(self, search_term: str):
        async with self.Session() as request:
            result = await request.execute(select(Users).filter(Users.username.ilike(f"{search_term}%")))
            return result.scalars().all()

    async def get_user_orders(self, user_id):
        async with self.Session() as session:
            result = await session.execute(select(Order).where(
                Order.user_telegram_id == user_id
            ))
            return result.scalars().all()

    async def delete_order(self, order_id: int):
        async with self.Session() as request:
            await request.execute(delete(Order).where(Order.id == order_id))
            await request.commit()

    async def get_last_order(self):
        async with self.Session() as request:
            # Выполняем запрос, сортируя по дате или ID, и получаем только последний заказ
            result = await request.execute(select(Order).order_by(desc(Order.id)).limit(1))
            return result.scalars().first()

    async def prepare_orders_for_sheet(self):
        # Получаем последний заказ
        orders = await self.get_last_order()  # Получаем последний заказ из базы данных

        # Если заказов нет
        if not orders:
            return {"orders": []}  # Возвращаем пустой список, если заказов нет

        # Формируем данные для отправки в нужном формате
        data = [
                orders.id,  # ID заказа
                orders.order_date.strftime("%d.%m.%Y"),  # Дата заказа
                orders.sum_order,  # Сумма заказа
                orders.order_product,  # Продукт заказа
                orders.order_quantity,  # Количество продукта
                orders.user_telegram_id,  # Telegram ID пользователя
                orders.user_name,  # Имя пользователя
                orders.user_surname,  # Фамилия пользователя
                orders.user_phone,  # Телефон пользователя
                orders.order_status  # Статус заказа
            ]

        return data
