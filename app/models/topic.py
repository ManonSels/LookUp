from .database import db_connection
from flask import current_app

class TopicModel:
    @db_connection
    def get_all_published(self, cursor):
        try:
            cursor.execute('''
                SELECT DISTINCT t.*
                FROM topic t
                JOIN topic_category tc ON t.id = tc.topic_id
                WHERE t.is_published = 1 
                ORDER BY t.title
            ''')
            topics_data = cursor.fetchall()
            return [self._dict_to_topic(topic) for topic in topics_data]
        except Exception as e:
            current_app.logger.error(f"Error getting published topics: {e}")
            return []
    
    @db_connection
    def get_by_slug(self, cursor, slug):
        try:
            cursor.execute('''
                SELECT t.*
                FROM topic t
                WHERE t.slug = ? AND t.is_published = 1
            ''', (slug,))
            topic_data = cursor.fetchone()
            
            if not topic_data:
                return None
            
            cursor.execute('UPDATE topic SET view_count = view_count + 1 WHERE id = ?', (topic_data['id'],))
            
            topic = self._dict_to_topic(topic_data)
            
            from app.models.topic_category import TopicCategoryModel
            topic_category_model = TopicCategoryModel()
            topic.categories = topic_category_model.get_categories_for_topic(topic.id)
            
            return topic
        except Exception as e:
            current_app.logger.error(f"Error getting topic by slug {slug}: {e}")
            return None
    
    @db_connection
    def increment_view_count(self, cursor, topic_id):
        try:
            cursor.execute('UPDATE topic SET view_count = view_count + 1 WHERE id = ?', (topic_id,))
            return True
        except Exception as e:
            current_app.logger.error(f"Error incrementing view count for topic {topic_id}: {e}")
            return False
    
    @db_connection
    def get_most_viewed(self, cursor, limit=4):
        try:
            cursor.execute('''
                SELECT DISTINCT t.*
                FROM topic t
                JOIN topic_category tc ON t.id = tc.topic_id
                WHERE t.is_published = 1 
                ORDER BY t.view_count DESC, t.updated_at DESC
                LIMIT ?
            ''', (limit,))
            topics_data = cursor.fetchall()
            return [self._dict_to_topic(topic) for topic in topics_data]
        except Exception as e:
            current_app.logger.error(f"Error getting most viewed topics: {e}")
            return []
    
    @db_connection
    def get_all(self, cursor):
        try:
            cursor.execute('''
                SELECT DISTINCT t.*
                FROM topic t
                JOIN topic_category tc ON t.id = tc.topic_id
                ORDER BY t.title
            ''')
            topics_data = cursor.fetchall()
            return [self._dict_to_topic(topic) for topic in topics_data]
        except Exception as e:
            current_app.logger.error(f"Error getting all topics: {e}")
            return []

    @db_connection
    def get_all_grouped_by_category(self, cursor):
        try:
            cursor.execute('''
                SELECT t.*, c.name as category_name, c.id as category_id, c.display_order as category_display_order
                FROM topic t
                JOIN topic_category tc ON t.id = tc.topic_id
                JOIN category c ON tc.category_id = c.id
                ORDER BY c.display_order ASC, tc.display_order ASC, t.title ASC
            ''')
            topics_data = cursor.fetchall()
            
            categorized_topics = {}
            for topic_data in topics_data:
                category_id = topic_data['category_id']
                category_name = topic_data['category_name']
                
                if category_id not in categorized_topics:
                    categorized_topics[category_id] = {
                        'name': category_name,
                        'display_order': topic_data['category_display_order'],
                        'topics': []
                    }
                
                categorized_topics[category_id]['topics'].append(self._dict_to_topic(topic_data))
            
            sorted_categories = sorted(categorized_topics.items(), key=lambda x: x[1]['display_order'])
            return dict(sorted_categories)
        except Exception as e:
            current_app.logger.error(f"Error getting topics grouped by category: {e}")
            return {}
    
    @db_connection
    def get_by_id(self, cursor, topic_id):
        try:
            cursor.execute('SELECT t.* FROM topic t WHERE t.id = ?', (topic_id,))
            topic_data = cursor.fetchone()
            
            if not topic_data:
                return None
            
            topic = self._dict_to_topic(topic_data)
            
            from app.models.topic_category import TopicCategoryModel
            topic_category_model = TopicCategoryModel()
            topic.categories = topic_category_model.get_categories_for_topic(topic.id)
            topic.category_ids = [cat.id for cat in topic.categories]
            
            return topic
        except Exception as e:
            current_app.logger.error(f"Error getting topic by ID {topic_id}: {e}")
            return None
    
    @db_connection
    def get_by_category(self, cursor, category_id):
        try:
            from app.models.topic_category import TopicCategoryModel
            topic_category_model = TopicCategoryModel()
            return topic_category_model.get_topics_for_category(category_id)
        except Exception as e:
            current_app.logger.error(f"Error getting topics by category {category_id}: {e}")
            return []
    
    @db_connection
    def create_topic(self, cursor, slug, title, description, user_id, category_ids, is_published=False, card_color_light='#ffffff', card_color_dark='#1a1a1a', logo_filename_light=None, logo_filename_dark=None):
        try:
            if not slug or not title:
                raise ValueError("Slug and title are required")
            
            if len(slug) > 100 or len(title) > 200:
                raise ValueError("Slug or title too long")
            
            if not category_ids:
                raise ValueError("At least one category is required")
            
            cursor.execute(
                'INSERT INTO topic (slug, title, description, user_id, is_published, card_color_light, card_color_dark, logo_filename_light, logo_filename_dark) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (slug, title, description, user_id, 1 if is_published else 0, card_color_light, card_color_dark, logo_filename_light, logo_filename_dark)
            )
            topic_id = cursor.lastrowid
            
            from app.models.topic_category import TopicCategoryModel
            topic_category_model = TopicCategoryModel()
            topic_category_model.set_topic_categories(topic_id, category_ids)
            
            return topic_id
        except Exception as e:
            current_app.logger.error(f"Error creating topic: {e}")
            return None

    @db_connection
    def update_topic(self, cursor, topic_id, slug, title, description, category_ids, is_published, card_color_light='#ffffff', card_color_dark='#1a1a1a', logo_filename_light=None, logo_filename_dark=None):
        try:
            if not slug or not title:
                raise ValueError("Slug and title are required")
            
            if len(slug) > 100 or len(title) > 200:
                raise ValueError("Slug or title too long")
            
            if not category_ids:
                raise ValueError("At least one category is required")
            
            cursor.execute(
                'UPDATE topic SET slug = ?, title = ?, description = ?, is_published = ?, card_color_light = ?, card_color_dark = ?, logo_filename_light = ?, logo_filename_dark = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (slug, title, description, 1 if is_published else 0, card_color_light, card_color_dark, logo_filename_light, logo_filename_dark, topic_id)
            )
            
            from app.models.topic_category import TopicCategoryModel
            topic_category_model = TopicCategoryModel()
            topic_category_model.set_topic_categories(topic_id, category_ids)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error updating topic {topic_id}: {e}")
            return False
    
    @db_connection
    def delete_topic(self, cursor, topic_id):
        try:
            cursor.execute('DELETE FROM topic WHERE id = ?', (topic_id,))
            return True
        except Exception as e:
            current_app.logger.error(f"Error deleting topic {topic_id}: {e}")
            return False
        
    @db_connection
    def refresh_updated_at(self, cursor, topic_id):
        try:
            cursor.execute('UPDATE topic SET updated_at = CURRENT_TIMESTAMP WHERE id = ?', (topic_id,))
            return True
        except Exception as e:
            current_app.logger.error(f"Error refreshing topic timestamp {topic_id}: {e}")
            return False
    
    @db_connection
    def get_all_categories(self, cursor):
        try:
            cursor.execute('SELECT id, name FROM category ORDER BY display_order, name')
            categories_data = cursor.fetchall()
            return [(cat['id'], cat['name']) for cat in categories_data]
        except Exception as e:
            current_app.logger.error(f"Error getting all categories: {e}")
            return []
    
    @db_connection
    def get_categories_for_topic(self, cursor, topic_id):
        try:
            from app.models.topic_category import TopicCategoryModel
            topic_category_model = TopicCategoryModel()
            return topic_category_model.get_categories_for_topic(topic_id)
        except Exception as e:
            current_app.logger.error(f"Error getting categories for topic {topic_id}: {e}")
            return []
    
    def _dict_to_topic(self, topic_data):
        if not isinstance(topic_data, dict):
            topic_data = dict(topic_data)

        topic = TopicModel()
        topic.id = topic_data['id']
        topic.slug = topic_data['slug']
        topic.title = topic_data['title']
        topic.description = topic_data['description']
        topic.is_published = bool(topic_data['is_published'])
        topic.user_id = topic_data['user_id']
        topic.card_color_light = topic_data.get('card_color_light', '#ffffff')
        topic.card_color_dark = topic_data.get('card_color_dark', '#1a1a1a')
        topic.logo_filename_light = topic_data.get('logo_filename_light')
        topic.logo_filename_dark = topic_data.get('logo_filename_dark')
        topic.view_count = topic_data.get('view_count', 0)
        topic.created_at = topic_data['created_at']
        topic.updated_at = topic_data['updated_at']
        
        topic.categories = []
        topic.category_ids = []
        
        return topic