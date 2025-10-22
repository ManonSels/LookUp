from .database import db_connection

class TopicModel:
    @db_connection
    def get_all_published(self, cursor):
        cursor.execute('SELECT * FROM topic WHERE is_published = 1 ORDER BY title')
        topics_data = cursor.fetchall()
        return [self._dict_to_topic(topic) for topic in topics_data]
    
    @db_connection
    def get_by_slug(self, cursor, slug):
        cursor.execute('SELECT * FROM topic WHERE slug = ? AND is_published = 1', (slug,))
        topic_data = cursor.fetchone()
        
        if not topic_data:
            return None
        
        return self._dict_to_topic(topic_data)
    
    @db_connection
    def get_all(self, cursor):
        cursor.execute('SELECT * FROM topic ORDER BY title')
        topics_data = cursor.fetchall()
        return [self._dict_to_topic(topic) for topic in topics_data]
    
    @db_connection
    def get_by_id(self, cursor, topic_id):
        cursor.execute('SELECT * FROM topic WHERE id = ?', (topic_id,))
        topic_data = cursor.fetchone()
        
        if not topic_data:
            return None
        
        return self._dict_to_topic(topic_data)
    

    @db_connection
    def get_topics_by_category(self, cursor):
        """Get all published topics grouped by category"""
        cursor.execute('''
            SELECT category, 
                   GROUP_CONCAT(id) as topic_ids,
                   COUNT(*) as topic_count
            FROM topic 
            WHERE is_published = 1 
            GROUP BY category 
            ORDER BY category
        ''')
        categories_data = cursor.fetchall()
        
        # Now get all topics for each category
        categorized_topics = {}
        for category_data in categories_data:
            category = category_data['category']
            topic_ids = category_data['topic_ids'].split(',')
            
            # Get topics for this category
            placeholders = ','.join(['?'] * len(topic_ids))
            cursor.execute(f'''
                SELECT * FROM topic 
                WHERE id IN ({placeholders}) 
                ORDER BY title
            ''', topic_ids)
            
            topics_data = cursor.fetchall()
            categorized_topics[category] = [self._dict_to_topic(topic) for topic in topics_data]
        
        return categorized_topics
    
    @db_connection
    def get_all_categories(self, cursor):
        """Get all unique categories"""
        cursor.execute('SELECT DISTINCT category FROM topic WHERE is_published = 1 ORDER BY category')
        categories_data = cursor.fetchall()
        return [category['category'] for category in categories_data]
    
    
    @db_connection
    def create_topic(self, cursor, slug, title, description, user_id, is_published=False):
        try:
            # Use a default category_id (1 = General)
            cursor.execute(
                'INSERT INTO topic (slug, title, description, category_id, user_id, is_published) VALUES (?, ?, ?, ?, ?, ?)',
                (slug, title, description, 1, user_id, 1 if is_published else 0)  # Added category_id=1
            )
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating topic: {e}")
            print(f"Slug: {slug}, Title: {title}, User ID: {user_id}")
            return None

    @db_connection
    def update_topic(self, cursor, topic_id, slug, title, description, is_published):
        try:
            cursor.execute(
                'UPDATE topic SET slug = ?, title = ?, description = ?, is_published = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (slug, title, description, 1 if is_published else 0, topic_id)
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
        
    
    
    def _dict_to_topic(self, topic_data):
        """Convert database row to Topic object"""

        if not isinstance(topic_data, dict):
            topic_data = dict(topic_data)

        topic = TopicModel()
        topic.id = topic_data['id']
        topic.slug = topic_data['slug']
        topic.title = topic_data['title']
        topic.description = topic_data['description']
        topic.category = topic_data.get('category', 'General')
        topic.is_published = bool(topic_data['is_published'])
        topic.user_id = topic_data['user_id']
        topic.created_at = topic_data['created_at']
        topic.updated_at = topic_data['updated_at']
        return topic