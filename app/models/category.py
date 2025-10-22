from .database import db_connection

class CategoryModel:
    @db_connection
    def get_all(self, cursor):
        """Get all categories ordered by display_order"""
        cursor.execute('SELECT * FROM category ORDER BY display_order, name')
        categories_data = cursor.fetchall()
        return [self._dict_to_category(category) for category in categories_data]
    
    @db_connection
    def get_by_id(self, cursor, category_id):
        cursor.execute('SELECT * FROM category WHERE id = ?', (category_id,))
        category_data = cursor.fetchone()
        if not category_data:
            return None
        return self._dict_to_category(category_data)
    
    @db_connection
    def create(self, cursor, name, display_order=0):
        try:
            cursor.execute(
                'INSERT INTO category (name, display_order) VALUES (?, ?)',
                (name, display_order)
            )
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating category: {e}")
            return None
    
    @db_connection
    def update(self, cursor, category_id, name, display_order):
        try:
            cursor.execute(
                'UPDATE category SET name = ?, display_order = ? WHERE id = ?',
                (name, display_order, category_id)
            )
            return True
        except Exception as e:
            print(f"Error updating category: {e}")
            return False
    
    @db_connection
    def delete(self, cursor, category_id):
        try:
            cursor.execute('DELETE FROM category WHERE id = ?', (category_id,))
            return True
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False
    
    @db_connection
    def get_topics_by_category(self, cursor):
        """Get all published topics grouped by category with manual ordering"""
        cursor.execute('''
            SELECT c.id as category_id, c.name as category_name, c.display_order,
                   GROUP_CONCAT(t.id) as topic_ids
            FROM category c
            LEFT JOIN topic t ON c.id = t.category_id AND t.is_published = 1
            GROUP BY c.id
            ORDER BY c.display_order, c.name
        ''')
        categories_data = cursor.fetchall()
        
        categorized_topics = {}
        for category_data in categories_data:
            category_id = category_data['category_id']
            category_name = category_data['category_name']
            display_order = category_data['display_order']
            
            # Get topics for this category
            if category_data['topic_ids']:
                topic_ids = category_data['topic_ids'].split(',')
                placeholders = ','.join(['?'] * len(topic_ids))
                cursor.execute(f'''
                    SELECT * FROM topic 
                    WHERE id IN ({placeholders}) 
                    ORDER BY title
                ''', topic_ids)
                topics_data = cursor.fetchall()
                
                from app.models.topic import TopicModel
                topic_model = TopicModel()
                topics = [topic_model._dict_to_topic(topic) for topic in topics_data]
            else:
                topics = []
            
            categorized_topics[category_name] = {
                'topics': topics,
                'display_order': display_order,
                'id': category_id
            }
        
        # Sort by display_order
        return dict(sorted(categorized_topics.items(), key=lambda x: x[1]['display_order']))
    
    def _dict_to_category(self, category_data):
        """Convert database row to Category object"""
        category = CategoryModel()
        category.id = category_data['id']
        category.name = category_data['name']
        category.display_order = category_data['display_order']
        category.created_at = category_data['created_at']
        return category