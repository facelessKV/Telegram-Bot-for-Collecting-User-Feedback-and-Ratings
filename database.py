import sqlite3
import datetime
from typing import List, Dict, Tuple, Optional, Any, Union

class Database:
    def __init__(self, db_name: str):
        """
        Инициализация соединения с базой данных
        
        :param db_name: Имя файла базы данных SQLite
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """
        Установка соединения с базой данных
        """
        self.conn = sqlite3.connect(self.db_name)
        # Настройка для получения результатов запросов в виде словарей
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def disconnect(self) -> None:
        """
        Закрытие соединения с базой данных
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def create_tables(self) -> None:
        """
        Создание необходимых таблиц в базе данных, если они не существуют
        """
        self.connect()
        
        # Таблица пользователей
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица продуктов/услуг
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Предварительное заполнение таблицы продуктов
        self.cursor.execute('''
        INSERT OR IGNORE INTO products (name, category) VALUES 
        ('iPhone 15', 'Смартфоны'),
        ('Samsung Galaxy S23', 'Смартфоны'),
        ('MacBook Pro', 'Ноутбуки'),
        ('Dell XPS 13', 'Ноутбуки'),
        ('AirPods Pro', 'Наушники'),
        ('Apple Watch Series 9', 'Умные часы'),
        ('iPad Pro', 'Планшеты'),
        ('Доставка курьером', 'Доставка'),
        ('Техническая поддержка', 'Обслуживание клиентов')
        ''')
        
        # Таблица отзывов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Таблица рейтингов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            rating INTEGER CHECK (rating BETWEEN 1 AND 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            UNIQUE (user_id, product_id)
        )
        ''')
        
        self.conn.commit()
        self.disconnect()

    def register_user(self, user_id: int, username: str, first_name: str, last_name: str) -> None:
        """
        Регистрация нового пользователя или обновление существующего
        
        :param user_id: ID пользователя в Telegram
        :param username: Username пользователя
        :param first_name: Имя пользователя
        :param last_name: Фамилия пользователя
        """
        self.connect()
        
        # Используем INSERT OR REPLACE для обновления существующих пользователей
        self.cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        
        self.conn.commit()
        self.disconnect()

    def add_product(self, name: str, category: str) -> int:
        """
        Добавление нового продукта или услуги
        
        :param name: Название продукта/услуги
        :param category: Категория продукта/услуги
        :return: ID добавленного продукта
        """
        self.connect()
        
        self.cursor.execute('''
        INSERT OR IGNORE INTO products (name, category) VALUES (?, ?)
        ''', (name, category))
        
        # Получаем ID добавленного или существующего продукта
        self.cursor.execute('SELECT id FROM products WHERE name = ?', (name,))
        product_id = self.cursor.fetchone()[0]
        
        self.conn.commit()
        self.disconnect()
        
        return product_id

    def get_products(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех продуктов/услуг
        
        :return: Список словарей с информацией о продуктах
        """
        self.connect()
        
        self.cursor.execute('SELECT id, name, category FROM products ORDER BY category, name')
        products = [dict(row) for row in self.cursor.fetchall()]
        
        self.disconnect()
        
        return products

    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Получение списка продуктов/услуг по категории
        
        :param category: Категория продуктов/услуг
        :return: Список словарей с информацией о продуктах
        """
        self.connect()
        
        self.cursor.execute('''
        SELECT id, name, category 
        FROM products 
        WHERE category = ? 
        ORDER BY name
        ''', (category,))
        
        products = [dict(row) for row in self.cursor.fetchall()]
        
        self.disconnect()
        
        return products

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение информации о продукте по его ID
        
        :param product_id: ID продукта
        :return: Словарь с информацией о продукте или None, если продукт не найден
        """
        self.connect()
        
        self.cursor.execute('SELECT id, name, category FROM products WHERE id = ?', (product_id,))
        product = self.cursor.fetchone()
        
        self.disconnect()
        
        return dict(product) if product else None

    def add_feedback(self, user_id: int, product_id: int, text: str) -> int:
        """
        Добавление нового отзыва
        
        :param user_id: ID пользователя
        :param product_id: ID продукта
        :param text: Текст отзыва
        :return: ID добавленного отзыва
        """
        self.connect()
        
        self.cursor.execute('''
        INSERT INTO feedback (user_id, product_id, text) VALUES (?, ?, ?)
        ''', (user_id, product_id, text))
        
        feedback_id = self.cursor.lastrowid
        
        self.conn.commit()
        self.disconnect()
        
        return feedback_id

    def get_feedback_by_product(self, product_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получение отзывов о конкретном продукте
        
        :param product_id: ID продукта
        :param limit: Ограничение на количество отзывов
        :return: Список словарей с информацией об отзывах
        """
        self.connect()
        
        # Получаем отзывы с информацией о пользователях
        self.cursor.execute('''
        SELECT f.id, f.text, f.created_at, 
               u.user_id, u.username, u.first_name, u.last_name,
               p.name as product_name
        FROM feedback f
        JOIN users u ON f.user_id = u.user_id
        JOIN products p ON f.product_id = p.id
        WHERE f.product_id = ?
        ORDER BY f.created_at DESC
        LIMIT ?
        ''', (product_id, limit))
        
        feedback_list = [dict(row) for row in self.cursor.fetchall()]
        
        self.disconnect()
        
        return feedback_list

    def add_rating(self, user_id: int, product_id: int, rating: int) -> int:
        """
        Добавление или обновление рейтинга продукта
        
        :param user_id: ID пользователя
        :param product_id: ID продукта
        :param rating: Оценка от 1 до 5
        :return: ID добавленного рейтинга
        """
        self.connect()
        
        # Используем INSERT OR REPLACE для обновления существующих рейтингов
        self.cursor.execute('''
        INSERT OR REPLACE INTO ratings (user_id, product_id, rating)
        VALUES (?, ?, ?)
        ''', (user_id, product_id, rating))
        
        rating_id = self.cursor.lastrowid
        
        self.conn.commit()
        self.disconnect()
        
        return rating_id

    def get_average_rating(self, product_id: int) -> Optional[float]:
        """
        Получение среднего рейтинга продукта
        
        :param product_id: ID продукта
        :return: Средний рейтинг или None, если рейтингов нет
        """
        self.connect()
        
        self.cursor.execute('''
        SELECT AVG(rating) as avg_rating
        FROM ratings
        WHERE product_id = ?
        ''', (product_id,))
        
        result = self.cursor.fetchone()
        avg_rating = result['avg_rating'] if result and result['avg_rating'] is not None else None
        
        self.disconnect()
        
        return round(avg_rating, 1) if avg_rating is not None else None

    def get_user_rating(self, user_id: int, product_id: int) -> Optional[int]:
        """
        Получение рейтинга, оставленного пользователем для продукта
        
        :param user_id: ID пользователя
        :param product_id: ID продукта
        :return: Рейтинг или None, если рейтинг не найден
        """
        self.connect()
        
        self.cursor.execute('''
        SELECT rating
        FROM ratings
        WHERE user_id = ? AND product_id = ?
        ''', (user_id, product_id))
        
        result = self.cursor.fetchone()
        
        self.disconnect()
        
        return result['rating'] if result else None
    
    def get_all_feedback_and_ratings(self) -> Dict[str, Any]:
        """
        Получение всех отзывов и рейтингов для аналитики
        
        :return: Словарь с данными для анализа
        """
        self.connect()
        
        # Получаем все отзывы
        self.cursor.execute('''
        SELECT f.id, f.text, f.created_at, 
               u.user_id, u.username, u.first_name, u.last_name,
               p.id as product_id, p.name as product_name, p.category
        FROM feedback f
        JOIN users u ON f.user_id = u.user_id
        JOIN products p ON f.product_id = p.id
        ORDER BY f.created_at DESC
        ''')
        
        feedback_list = [dict(row) for row in self.cursor.fetchall()]
        
        # Получаем все рейтинги
        self.cursor.execute('''
        SELECT r.id, r.rating, r.created_at,
               u.user_id, u.username, u.first_name, u.last_name,
               p.id as product_id, p.name as product_name, p.category
        FROM ratings r
        JOIN users u ON r.user_id = u.user_id
        JOIN products p ON r.product_id = p.id
        ORDER BY r.created_at DESC
        ''')
        
        ratings_list = [dict(row) for row in self.cursor.fetchall()]
        
        # Получаем средние рейтинги по продуктам
        self.cursor.execute('''
        SELECT p.id, p.name, p.category, AVG(r.rating) as avg_rating, COUNT(r.id) as ratings_count
        FROM products p
        LEFT JOIN ratings r ON p.id = r.product_id
        GROUP BY p.id
        ORDER BY avg_rating DESC
        ''')
        
        products_ratings = [dict(row) for row in self.cursor.fetchall()]
        
        # Получаем статистику по пользователям
        self.cursor.execute('''
        SELECT COUNT(DISTINCT u.user_id) as total_users,
               COUNT(DISTINCT f.user_id) as users_with_feedback,
               COUNT(DISTINCT r.user_id) as users_with_ratings
        FROM users u
        LEFT JOIN feedback f ON u.user_id = f.user_id
        LEFT JOIN ratings r ON u.user_id = r.user_id
        ''')
        
        user_stats = dict(self.cursor.fetchone())
        
        self.disconnect()
        
        return {
            'feedback': feedback_list,
            'ratings': ratings_list,
            'products_ratings': products_ratings,
            'user_stats': user_stats
        }