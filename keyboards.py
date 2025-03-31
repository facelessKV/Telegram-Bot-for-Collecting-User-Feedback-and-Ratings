from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from typing import List, Dict, Any

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создание основной клавиатуры с командами бота
    
    :return: Объект клавиатуры
    """
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="/leave_feedback"))
    builder.add(KeyboardButton(text="/view_feedback"))
    builder.add(KeyboardButton(text="/rate"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_categories_keyboard() -> InlineKeyboardMarkup:
    """
    Создание инлайн-клавиатуры с категориями продуктов
    
    :return: Объект инлайн-клавиатуры
    """
    from config import PRODUCT_CATEGORIES
    
    builder = InlineKeyboardBuilder()
    
    for category in PRODUCT_CATEGORIES:
        builder.add(InlineKeyboardButton(
            text=category,
            callback_data=f"category_{category}"
        ))
    
    builder.adjust(2)
    return builder.as_markup()

def get_products_keyboard(products: List[Dict[str, Any]], action: str) -> InlineKeyboardMarkup:
    """
    Создание инлайн-клавиатуры со списком продуктов
    
    :param products: Список продуктов
    :param action: Действие (feedback или rate)
    :return: Объект инлайн-клавиатуры
    """
    builder = InlineKeyboardBuilder()
    
    for product in products:
        builder.add(InlineKeyboardButton(
            text=product['name'],
            callback_data=f"{action}_{product['id']}"
        ))
    
    # Добавляем кнопку "Назад к категориям"
    builder.add(InlineKeyboardButton(
        text="◀️ Назад к категориям",
        callback_data="back_to_categories"
    ))
    
    builder.adjust(1)
    return builder.as_markup()

def get_rating_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """
    Создание инлайн-клавиатуры для выставления рейтинга
    
    :param product_id: ID продукта
    :return: Объект инлайн-клавиатуры
    """
    builder = InlineKeyboardBuilder()
    
    for i in range(1, 6):
        # Используем эмодзи звезд для наглядности
        star = "⭐"
        builder.add(InlineKeyboardButton(
            text=f"{i} {star*i}",
            callback_data=f"set_rating_{product_id}_{i}"
        ))
    
    # Добавляем кнопку "Отмена"
    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_rating"
    ))
    
    builder.adjust(5, 1)
    return builder.as_markup()