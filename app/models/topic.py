from .database import db_connection

class TopicModel:
    # ----- ALL PUBLISHED ----- #
    @db_connection
    def get_all_published(self, cursor):
        cursor.execute('''
            SELECT t.*, c.name as category_name 
            FROM topic t
            LEFT JOIN category c ON t.category_id = c.id
            WHERE t.is_published = 1 
            ORDER BY t.title
        ''')
        topics_data = cursor.fetchall()
        return [self._dict_to_topic(topic) for topic in topics_data]
    
    # ----- BY SLUG ----- #
    @db_connection
    def get_by_slug(self, cursor, slug):
        cursor.execute('''
            SELECT t.*, c.name as category_name 
            FROM topic t
            LEFT JOIN category c ON t.category_id = c.id
            WHERE t.slug = ? AND t.is_published = 1
        ''', (slug,))
        topic_data = cursor.fetchone()
        
        if not topic_data:
            return None
        
        return self._dict_to_topic(topic_data)
    
    # ----- ALL ----- #
    @db_connection
    def get_all(self, cursor):
        cursor.execute('''
            SELECT t.*, c.name as category_name, c.display_order as category_display_order
            FROM topic t
            LEFT JOIN category c ON t.category_id = c.id
            ORDER BY c.display_order, t.display_order, t.title
        ''')
        topics_data = cursor.fetchall()
        return [self._dict_to_topic(topic) for topic in topics_data]

    # ----- ALL GROUPED BY CATEGORY ----- #
    @db_connection
    def get_all_grouped_by_category(self, cursor):
        cursor.execute('''
            SELECT t.*, c.name as category_name, c.id as category_id, c.display_order as category_display_order
            FROM topic t
            LEFT JOIN category c ON t.category_id = c.id
            ORDER BY c.display_order ASC, t.display_order ASC, t.title ASC
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
    
    # ----- BY ID ----- #
    @db_connection
    def get_by_id(self, cursor, topic_id):
        cursor.execute('''
            SELECT t.*, c.name as category_name 
            FROM topic t
            LEFT JOIN category c ON t.category_id = c.id
            WHERE t.id = ?
        ''', (topic_id,))
        topic_data = cursor.fetchone()
        
        if not topic_data:
            return None
        
        return self._dict_to_topic(topic_data)
    
    # ----- BY CATEGORY ----- #
    @db_connection
    def get_by_category(self, cursor, category_id):
        cursor.execute('''
            SELECT t.*, c.name as category_name 
            FROM topic t
            LEFT JOIN category c ON t.category_id = c.id
            WHERE t.category_id = ?
            ORDER BY t.title
        ''', (category_id,))
        topics_data = cursor.fetchall()
        return [self._dict_to_topic(topic) for topic in topics_data]
    
    # ----- CREATE TOPIC ----- #
    @db_connection
    def create_topic(self, cursor, slug, title, description, user_id, category_id=1, is_published=False, card_color_light='#ffffff', card_color_dark='#1a1a1a', logo_filename_light=None, logo_filename_dark=None):  # UPDATE PARAMS
        try:
            cursor.execute(
                'SELECT COALESCE(MAX(display_order), -1) FROM topic WHERE category_id = ?',
                (category_id,)
            )
            result = cursor.fetchone()
            next_display_order = (result[0] or -1) + 1
            
            cursor.execute(
                'INSERT INTO topic (slug, title, description, category_id, user_id, is_published, display_order, card_color_light, card_color_dark, logo_filename_light, logo_filename_dark) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',  # UPDATE
                (slug, title, description, category_id, user_id, 1 if is_published else 0, next_display_order, card_color_light, card_color_dark, logo_filename_light, logo_filename_dark)  # UPDATE
            )
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating topic: {e}")
            return None

    # ----- UPDATE TOPIC ----- #
    @db_connection
    def update_topic(self, cursor, topic_id, slug, title, description, category_id, is_published, card_color_light='#ffffff', card_color_dark='#1a1a1a', logo_filename_light=None, logo_filename_dark=None):  # UPDATE PARAMS
        try:
            cursor.execute(
                'UPDATE topic SET slug = ?, title = ?, description = ?, category_id = ?, is_published = ?, card_color_light = ?, card_color_dark = ?, logo_filename_light = ?, logo_filename_dark = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',  # UPDATE
                (slug, title, description, category_id, 1 if is_published else 0, card_color_light, card_color_dark, logo_filename_light, logo_filename_dark, topic_id)  # UPDATE
            )
            return True
        except Exception as e:
            print(f"Error updating topic: {e}")
            return False
    
    # ----- DELETE TOPIC ----- #
    @db_connection
    def delete_topic(self, cursor, topic_id):
        try:
            cursor.execute('DELETE FROM topic WHERE id = ?', (topic_id,))
            return True
        except Exception as e:
            print(f"Error deleting topic: {e}")
            return False
    
    # ----- ALL CATEGORIES ----- #
    @db_connection
    def get_all_categories(self, cursor):
        cursor.execute('SELECT id, name FROM category ORDER BY display_order, name')
        categories_data = cursor.fetchall()
        return [(cat['id'], cat['name']) for cat in categories_data]
    
    # ----- CONVERT DB ROW TO TOPIC ----- #
    def _dict_to_topic(self, topic_data):
        if not isinstance(topic_data, dict):
            topic_data = dict(topic_data)

        topic = TopicModel()
        topic.id = topic_data['id']
        topic.slug = topic_data['slug']
        topic.title = topic_data['title']
        topic.description = topic_data['description']
        topic.category_id = topic_data['category_id']
        topic.category_name = topic_data.get('category_name', 'General')
        topic.is_published = bool(topic_data['is_published'])
        topic.user_id = topic_data['user_id']
        topic.card_color_light = topic_data.get('card_color_light', '#ffffff')
        topic.card_color_dark = topic_data.get('card_color_dark', '#1a1a1a')
        topic.logo_filename_light = topic_data.get('logo_filename_light')  # UPDATE
        topic.logo_filename_dark = topic_data.get('logo_filename_dark')    # ADD
        topic.created_at = topic_data['created_at']
        topic.updated_at = topic_data['updated_at']
        return topic