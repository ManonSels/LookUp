from .database import db_connection

class TopicModel:
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
    
    @db_connection
    def get_all(self, cursor):
        cursor.execute('''
            SELECT t.*, c.name as category_name 
            FROM topic t
            LEFT JOIN category c ON t.category_id = c.id
            ORDER BY t.title
        ''')
        topics_data = cursor.fetchall()
        return [self._dict_to_topic(topic) for topic in topics_data]
    
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
    
    @db_connection
    def create_topic(self, cursor, slug, title, description, user_id, category_id=1, is_published=False):
        try:
            cursor.execute(
                'INSERT INTO topic (slug, title, description, category_id, user_id, is_published) VALUES (?, ?, ?, ?, ?, ?)',
                (slug, title, description, category_id, user_id, 1 if is_published else 0)
            )
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating topic: {e}")
            return None

    @db_connection
    def update_topic(self, cursor, topic_id, slug, title, description, category_id, is_published):
        try:
            cursor.execute(
                'UPDATE topic SET slug = ?, title = ?, description = ?, category_id = ?, is_published = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (slug, title, description, category_id, 1 if is_published else 0, topic_id)
            )
            return True
        except Exception as e:
            print(f"Error updating topic: {e}")
            return False
        
    @db_connection
    def delete_topic(self, cursor, topic_id):
        try:
            cursor.execute('DELETE FROM topic WHERE id = ?', (topic_id,))
            return True
        except Exception as e:
            print(f"Error deleting topic: {e}")
            return False
    
    @db_connection
    def get_all_categories(self, cursor):
        """Get all categories from the category table"""
        cursor.execute('SELECT id, name FROM category ORDER BY display_order, name')
        categories_data = cursor.fetchall()
        return [(cat['id'], cat['name']) for cat in categories_data]
    
    def _dict_to_topic(self, topic_data):
        """Convert database row to Topic object"""
        if not isinstance(topic_data, dict):
            topic_data = dict(topic_data)

        topic = TopicModel()
        topic.id = topic_data['id']
        topic.slug = topic_data['slug']
        topic.title = topic_data['title']
        topic.description = topic_data['description']
        topic.category_id = topic_data['category_id']
        topic.category_name = topic_data.get('category_name', 'General')  # From JOIN
        topic.is_published = bool(topic_data['is_published'])
        topic.user_id = topic_data['user_id']
        topic.created_at = topic_data['created_at']
        topic.updated_at = topic_data['updated_at']
        return topic