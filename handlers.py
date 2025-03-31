from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import Database
from analytics import Analytics
from keyboards import (
    get_main_keyboard, 
    get_categories_keyboard, 
    get_products_keyboard, 
    get_rating_keyboard
)
from config import ADMIN_IDS, DB_NAME
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Инициализируем базу данных
db = Database(DB_NAME)

# Определяем состояния для FSM (конечного автомата)
class FeedbackStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_product = State()
    waiting_for_feedback_text = State()
    waiting_for_rating = State()

# Создаем роутер для регистрации обработчиков
router = Router()

# Обработчики команд
@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    Приветствует пользователя и объясняет функциональность бота
    """
    # Регистрируем пользователя в базе данных
    db.register_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name
    )
    
    # Отправляем приветственное сообщение
    await message.answer(
        "👋 Добро пожаловать в бот для сбора отзывов и рейтингов!\n\n"
        "Вы можете использовать следующие команды:\n"
        "📝 /leave_feedback - оставить отзыв о продукте или услуге\n"
        "👁️ /view_feedback - просмотреть отзывы о продукте или услуге\n"
        "⭐ /rate - поставить оценку продукту или услуге\n\n"
        "Ваше мнение очень важно для нас!",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("leave_feedback"))
async def cmd_leave_feedback(message: Message):
    """
    Обработчик команды /leave_feedback
    Запускает процесс оставления отзыва
    """
    await message.answer(
        "📋 Выберите категорию продукта или услуги:",
        reply_markup=get_categories_keyboard()
    )

@router.message(Command("view_feedback"))
async def cmd_view_feedback(message: Message):
    """
    Обработчик команды /view_feedback
    Показывает категории для просмотра отзывов
    """
    await message.answer(
        "📋 Выберите категорию продукта или услуги для просмотра отзывов:",
        reply_markup=get_categories_keyboard()
    )

@router.message(Command("rate"))
async def cmd_rate(message: Message):
    """
    Обработчик команды /rate
    Запускает процесс оценки продукта или услуги
    """
    await message.answer(
        "📋 Выберите категорию продукта или услуги для оценки:",
        reply_markup=get_categories_keyboard()
    )

@router.message(Command("stats"))
async def cmd_admin_stats(message: Message):
    """
    Обработчик команды /stats
    Генерирует и отправляет статистику (только для админов)
    """
    # Проверяем, является ли пользователь администратором
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    await message.answer("📊 Генерирую статистику, пожалуйста, подождите...")
    
    # Получаем данные для аналитики
    db_data = db.get_all_feedback_and_ratings()
    
    # Инициализируем аналитику
    analytics = Analytics(db_data)
    
    # Получаем общую статистику
    stats = analytics.get_general_stats()
    
    # Формируем текст отчета
    report_text = (
        "📊 **Общая статистика**\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"📝 Пользователей, оставивших отзывы: {stats['users_with_feedback']}\n"
        f"⭐ Пользователей, оставивших рейтинги: {stats['users_with_ratings']}\n\n"
        f"📝 Всего отзывов: {stats['total_feedback']}\n"
        f"⭐ Всего рейтингов: {stats['total_ratings']}\n"
        f"📊 Средний рейтинг всех продуктов: {stats['avg_rating_all_products']}\n\n"
        f"📅 **За последнюю неделю**\n"
        f"📝 Новых отзывов: {stats['feedback_last_week']}\n"
        f"⭐ Новых рейтингов: {stats['ratings_last_week']}\n"
        f"📊 Средний рейтинг: {stats['avg_rating_last_week']}\n\n"
    )
    
    # Добавляем топ продуктов
    top_products = analytics.get_top_products()
    if top_products:
        report_text += "🏆 **Топ-5 продуктов по рейтингу**\n\n"
        for i, product in enumerate(top_products, 1):
            report_text += (
                f"{i}. {product['name']} ({product['category']})\n"
                f"   ⭐ Рейтинг: {product['avg_rating']} (на основе {product['ratings_count']} оценок)\n\n"
            )
    
    # Отправляем текстовую статистику
    await message.answer(report_text, parse_mode="Markdown")
    
    # Генерируем и отправляем графики
    try:
        # График распределения рейтингов
        ratings_chart = analytics.generate_ratings_chart()
        await message.answer_photo(
            photo=ratings_chart,
            caption="📊 Распределение рейтингов"
        )
        
        # График отзывов по времени
        feedback_chart = analytics.generate_feedback_by_time_chart()
        await message.answer_photo(
            photo=feedback_chart,
            caption="📊 Динамика отзывов по дням"
        )
    except Exception as e:
        await message.answer(f"⚠️ Ошибка при генерации графиков: {str(e)}")

# Обработчики инлайн кнопок
@router.callback_query(F.data.startswith('category_'))
async def process_category_selection(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора категории
    
    :param callback_query: Объект callback_query
    :param state: Состояние FSM
    """
    # Извлекаем выбранную категорию из данных колбэка
    category = callback_query.data.split('_', 1)[1]
    
    # Получаем продукты выбранной категории
    products = db.get_products_by_category(category)
    
    if not products:
        await callback_query.answer("В этой категории нет продуктов")
        return
    
    # Определяем, какое действие выполняется (feedback, view или rate)
    # Просматриваем предыдущие сообщения для определения контекста
    message_text = callback_query.message.text.lower()
    
    action = "feedback"  # По умолчанию
    
    if "просмотра отзывов" in message_text:
        action = "view"
    elif "оценки" in message_text:
        action = "rate"
    
    # Сохраняем выбранную категорию и действие в состоянии
    await state.update_data(category=category, action=action)
    
    # Показываем продукты выбранной категории с соответствующим действием
    await callback_query.message.edit_text(
        f"Выберите продукт из категории '{category}':",
        reply_markup=get_products_keyboard(products, action)
    )
    
    # Отвечаем на колбэк, чтобы убрать часы загрузки
    await callback_query.answer()

@router.callback_query(F.data.startswith('feedback_'))
async def process_product_selection_for_feedback(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора продукта для отзыва
    
    :param callback_query: Объект callback_query
    :param state: Состояние FSM
    """
    # Извлекаем ID продукта из данных колбэка
    product_id = int(callback_query.data.split('_')[1])
    
    # Получаем информацию о продукте
    product = db.get_product_by_id(product_id)
    
    if not product:
        await callback_query.answer("Продукт не найден")
        return
    
    # Сохраняем выбранный продукт в состоянии
    await state.update_data(product_id=product_id, product_name=product['name'])
    
    # Переходим в состояние ожидания текста отзыва
    await state.set_state(FeedbackStates.waiting_for_feedback_text)
    
    await callback_query.message.edit_text(
        f"Вы выбрали: {product['name']}\n\n"
        "Пожалуйста, напишите свой отзыв в ответном сообщении:"
    )
    
    # Отвечаем на колбэк
    await callback_query.answer()

@router.callback_query(F.data.startswith('rate_'))
async def process_product_selection_for_rating(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора продукта для рейтинга
    
    :param callback_query: Объект callback_query
    :param state: Состояние FSM
    """
    # Извлекаем ID продукта из данных колбэка
    product_id = int(callback_query.data.split('_')[1])
    
    # Получаем информацию о продукте
    product = db.get_product_by_id(product_id)
    
    if not product:
        await callback_query.answer("Продукт не найден")
        return
    
    # Получаем текущий рейтинг пользователя для этого продукта
    user_rating = db.get_user_rating(callback_query.from_user.id, product_id)
    
    # Получаем средний рейтинг продукта
    avg_rating = db.get_average_rating(product_id)
    
    # Сохраняем выбранный продукт в состоянии
    await state.update_data(product_id=product_id, product_name=product['name'])
    
    # Формируем сообщение
    message_text = f"Оценка продукта: {product['name']}\n\n"
    
    if avg_rating:
        message_text += f"Средний рейтинг: {avg_rating} ⭐\n\n"
    
    if user_rating:
        message_text += f"Ваша текущая оценка: {user_rating} ⭐\n\n"
    
    message_text += "Выберите рейтинг от 1 до 5:"
    
    # Отображаем клавиатуру для выбора рейтинга
    await callback_query.message.edit_text(
        message_text,
        reply_markup=get_rating_keyboard(product_id)
    )
    
    # Отвечаем на колбэк
    await callback_query.answer()

@router.callback_query(F.data.startswith('view_'))
async def process_product_selection_for_view(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора продукта для просмотра отзывов
    
    :param callback_query: Объект callback_query
    :param state: Состояние FSM
    """
    # Извлекаем ID продукта из данных колбэка
    product_id = int(callback_query.data.split('_')[1])
    
    # Получаем информацию о продукте
    product = db.get_product_by_id(product_id)
    
    if not product:
        await callback_query.answer("Продукт не найден")
        return
    
    # Получаем отзывы о продукте
    feedback_list = db.get_feedback_by_product(product_id)
    
    # Получаем средний рейтинг продукта
    avg_rating = db.get_average_rating(product_id)
    
    # Формируем сообщение
    message_text = f"📝 Отзывы о продукте: {product['name']}\n\n"
    
    if avg_rating:
        message_text += f"⭐ Средний рейтинг: {avg_rating}\n\n"
    else:
        message_text += "⭐ Рейтинг отсутствует\n\n"
    
    if feedback_list:
        for i, feedback in enumerate(feedback_list, 1):
            # Формируем имя пользователя
            if feedback['username']:
                user_name = f"@{feedback['username']}"
            else:
                user_name = f"{feedback['first_name']} {feedback['last_name'] or ''}".strip()
            
            # Добавляем отзыв в сообщение
            message_text += (
                f"{i}. От: {user_name}\n"
                f"   {feedback['text']}\n"
                f"   Дата: {feedback['created_at']}\n\n"
            )
    else:
        message_text += "😞 Пока нет отзывов об этом продукте."
    
    # Проверяем длину сообщения и обрезаем при необходимости (Telegram ограничивает длину сообщения)
    if len(message_text) > 4000:
        message_text = message_text[:3950] + "...\n\n(Показаны не все отзывы)"
    
    # Создаем кнопку "Назад к категориям"
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="◀️ Назад к категориям",
        callback_data="back_to_categories"
    ))
    
    # Отправляем сообщение с отзывами
    await callback_query.message.edit_text(
        message_text,
        reply_markup=builder.as_markup()
    )
    
    # Отвечаем на колбэк
    await callback_query.answer()

@router.message(FeedbackStates.waiting_for_feedback_text)
async def process_feedback_text(message: Message, state: FSMContext):
    """
    Обработчик текста отзыва
    
    :param message: Объект сообщения
    :param state: Состояние FSM
    """
    # Получаем данные из состояния
    data = await state.get_data()
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    
    if not product_id:
        await message.answer("Произошла ошибка. Пожалуйста, начните процесс заново с команды /leave_feedback")
        await state.clear()
        return
    
    # Сохраняем отзыв в базе данных
    feedback_id = db.add_feedback(message.from_user.id, product_id, message.text)
    
    # Сбрасываем состояние
    await state.clear()
    
    # Отправляем подтверждение
    await message.answer(
        f"✅ Спасибо за ваш отзыв о продукте '{product_name}'!\n\n"
        "Хотите также оценить этот продукт?",
        reply_markup=get_rating_keyboard(product_id)
    )

@router.callback_query(F.data.startswith('set_rating_'))
async def process_rating_selection(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора рейтинга
    
    :param callback_query: Объект callback_query
    :param state: Состояние FSM
    """
    # Извлекаем данные из колбэка
    parts = callback_query.data.split('_')
    product_id = int(parts[2])
    rating = int(parts[3])
    
    # Получаем информацию о продукте
    product = db.get_product_by_id(product_id)
    
    if not product:
        await callback_query.answer("Продукт не найден")
        return
    
    # Сохраняем рейтинг в базе данных
    db.add_rating(callback_query.from_user.id, product_id, rating)
    
    # Получаем обновленный средний рейтинг
    avg_rating = db.get_average_rating(product_id)
    
    # Формируем текст благодарности
    stars = "⭐" * rating
    thank_you_text = (
        f"✅ Спасибо за вашу оценку продукта '{product['name']}'!\n\n"
        f"Ваша оценка: {rating} {stars}\n"
    )
    
    if avg_rating:
        thank_you_text += f"Средний рейтинг продукта: {avg_rating} ⭐"
    
    # Создаем клавиатуру с кнопками навигации
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="◀️ К категориям продуктов",
        callback_data="back_to_categories"
    ))
    builder.add(InlineKeyboardButton(
        text="🏠 Главное меню",
        callback_data="back_to_main"
    ))
    builder.adjust(1)
    
    # Отправляем сообщение с благодарностью
    await callback_query.message.edit_text(
        thank_you_text,
        reply_markup=builder.as_markup()
    )
    
    # Отвечаем на колбэк
    await callback_query.answer("Рейтинг сохранен!")

@router.callback_query(F.data == "back_to_categories")
async def process_back_to_categories(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Назад к категориям"
    
    :param callback_query: Объект callback_query
    :param state: Состояние FSM
    """
    # Получаем данные из состояния
    data = await state.get_data()
    action = data.get('action', 'feedback')  # По умолчанию feedback
    
    # Определяем заголовок сообщения в зависимости от действия
    if action == "view":
        message_text = "📋 Выберите категорию продукта или услуги для просмотра отзывов:"
    elif action == "rate":
        message_text = "📋 Выберите категорию продукта или услуги для оценки:"
    else:
        message_text = "📋 Выберите категорию продукта или услуги:"
    
    # Показываем клавиатуру с категориями
    await callback_query.message.edit_text(
        message_text,
        reply_markup=get_categories_keyboard()
    )
    
    # Отвечаем на колбэк
    await callback_query.answer()

@router.callback_query(F.data == "cancel_rating")
async def process_cancel_rating(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Отмена" при выставлении рейтинга
    
    :param callback_query: Объект callback_query
    :param state: Состояние FSM
    """
    # Показываем клавиатуру с категориями
    await callback_query.message.edit_text(
        "📋 Выберите категорию продукта или услуги:",
        reply_markup=get_categories_keyboard()
    )
    
    # Отвечаем на колбэк
    await callback_query.answer("Действие отменено")

@router.callback_query(F.data == "back_to_main")
async def process_back_to_main(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Главное меню"
    
    :param callback_query: Объект callback_query
    :param state: Состояние FSM
    """
    await callback_query.message.edit_text(
        "Вы вернулись в главное меню. Выберите команду на клавиатуре ниже:"
    )
    
    # Отправляем основную клавиатуру в новом сообщении
    await callback_query.message.answer(
        "Доступные команды:",
        reply_markup=get_main_keyboard()
    )
    
    # Отвечаем на колбэк
    await callback_query.answer()