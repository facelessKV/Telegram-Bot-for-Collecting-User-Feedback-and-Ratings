import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import io

class Analytics:
    def __init__(self, db_data: Dict[str, List[Dict[str, Any]]]):
        """
        Инициализация аналитики данными из базы данных
        
        :param db_data: Словарь с данными из базы данных
        """
        self.feedback_df = pd.DataFrame(db_data['feedback']) if db_data['feedback'] else pd.DataFrame()
        self.ratings_df = pd.DataFrame(db_data['ratings']) if db_data['ratings'] else pd.DataFrame()
        self.products_ratings_df = pd.DataFrame(db_data['products_ratings']) if db_data['products_ratings'] else pd.DataFrame()
        self.user_stats = db_data['user_stats']
        
        # Преобразуем строковые даты в datetime
        if not self.feedback_df.empty and 'created_at' in self.feedback_df:
            self.feedback_df['created_at'] = pd.to_datetime(self.feedback_df['created_at'])
        
        if not self.ratings_df.empty and 'created_at' in self.ratings_df:
            self.ratings_df['created_at'] = pd.to_datetime(self.ratings_df['created_at'])

    def get_general_stats(self) -> Dict[str, Any]:
        """
        Получение общей статистики по отзывам и рейтингам
        
        :return: Словарь с общей статистикой
        """
        stats = {
            'total_users': self.user_stats['total_users'],
            'users_with_feedback': self.user_stats['users_with_feedback'],
            'users_with_ratings': self.user_stats['users_with_ratings'],
            'total_feedback': len(self.feedback_df) if not self.feedback_df.empty else 0,
            'total_ratings': len(self.ratings_df) if not self.ratings_df.empty else 0,
            'avg_rating_all_products': round(self.ratings_df['rating'].mean(), 2) if not self.ratings_df.empty else 0,
        }
        
        # Добавляем статистику за последнюю неделю
        week_ago = datetime.now() - timedelta(days=7)
        
        if not self.feedback_df.empty:
            recent_feedback = self.feedback_df[self.feedback_df['created_at'] > week_ago]
            stats['feedback_last_week'] = len(recent_feedback)
        else:
            stats['feedback_last_week'] = 0
        
        if not self.ratings_df.empty:
            recent_ratings = self.ratings_df[self.ratings_df['created_at'] > week_ago]
            stats['ratings_last_week'] = len(recent_ratings)
            if not recent_ratings.empty:
                stats['avg_rating_last_week'] = round(recent_ratings['rating'].mean(), 2)
            else:
                stats['avg_rating_last_week'] = 0
        else:
            stats['ratings_last_week'] = 0
            stats['avg_rating_last_week'] = 0
        
        return stats

    def get_top_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Получение списка продуктов с наивысшим рейтингом
        
        :param limit: Количество продуктов в списке
        :return: Список словарей с информацией о топовых продуктах
        """
        if self.products_ratings_df.empty:
            return []
        
        # Отфильтруем только продукты с рейтингами
        rated_products = self.products_ratings_df[self.products_ratings_df['avg_rating'].notna()]
        
        if rated_products.empty:
            return []
        
        # Сортируем по среднему рейтингу в убывающем порядке
        top_products = rated_products.sort_values('avg_rating', ascending=False).head(limit)
        
        # Преобразуем в список словарей
        result = []
        for _, row in top_products.iterrows():
            result.append({
                'id': row['id'],
                'name': row['name'],
                'category': row['category'],
                'avg_rating': round(row['avg_rating'], 2),
                'ratings_count': row['ratings_count']
            })
        
        return result

    def get_category_stats(self) -> List[Dict[str, Any]]:
        """
        Получение статистики по категориям продуктов
        
        :return: Список словарей со статистикой по категориям
        """
        if self.products_ratings_df.empty:
            return []
        
        # Группируем по категориям и считаем среднее
        category_stats = self.products_ratings_df.groupby('category').agg({
            'avg_rating': lambda x: x.mean(skipna=True),
            'ratings_count': 'sum',
            'id': 'count'  # Количество продуктов в категории
        }).reset_index()
        
        if category_stats.empty:
            return []
        
        # Преобразуем в список словарей
        result = []
        for _, row in category_stats.iterrows():
            result.append({
                'category': row['category'],
                'products_count': row['id'],
                'avg_rating': round(row['avg_rating'], 2) if not pd.isna(row['avg_rating']) else 0,
                'ratings_count': row['ratings_count']
            })
        
        return sorted(result, key=lambda x: x['avg_rating'], reverse=True)

    def generate_ratings_chart(self) -> io.BytesIO:
        """
        Генерация графика распределения рейтингов
        
        :return: Буфер с изображением графика
        """
        if self.ratings_df.empty:
            # Создаем пустой график
            plt.figure(figsize=(10, 6))
            plt.title('Нет данных о рейтингах')
            plt.xlabel('Рейтинг')
            plt.ylabel('Количество')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plt.close()
            return buf
        
        # Считаем количество рейтингов каждого значения
        rating_counts = self.ratings_df['rating'].value_counts().sort_index()
        
        # Создаем график
        plt.figure(figsize=(10, 6))
        bars = plt.bar(rating_counts.index, rating_counts.values, color='skyblue')
        
        # Добавляем значения над столбцами
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height}',
                    ha='center', va='bottom')
        
        plt.title('Распределение рейтингов')
        plt.xlabel('Рейтинг')
        plt.ylabel('Количество')
        plt.xticks([1, 2, 3, 4, 5])
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Сохраняем график в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf

    def generate_feedback_by_time_chart(self) -> io.BytesIO:
        """
        Генерация графика количества отзывов по времени
        
        :return: Буфер с изображением графика
        """
        if self.feedback_df.empty:
            # Создаем пустой график
            plt.figure(figsize=(10, 6))
            plt.title('Нет данных об отзывах')
            plt.xlabel('Дата')
            plt.ylabel('Количество отзывов')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            plt.close()
            return buf
        
        # Группируем по дате (без времени)
        feedback_df_copy = self.feedback_df.copy()
        feedback_df_copy['date'] = feedback_df_copy['created_at'].dt.date
        daily_feedback = feedback_df_copy.groupby('date').size()
        
        # Создаем график
        plt.figure(figsize=(12, 6))
        plt.plot(daily_feedback.index, daily_feedback.values, marker='o', linestyle='-', color='blue')
        
        plt.title('Количество отзывов по дням')
        plt.xlabel('Дата')
        plt.ylabel('Количество отзывов')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Форматируем оси
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Сохраняем график в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf