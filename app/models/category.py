from .database import db_connection

class CategoryModel:
    # ------- ALL ------- #
    @db_connection
    def get_all(self, cursor):
        cursor.execute('SELECT * FROM category ORDER BY display_order, name')
        categories_data = cursor.fetchall()
        return [self._dict_to_category(category) for category in categories_data]
    
    # ------- BY ID ------- #
    @db_connection
    def get_by_id(self, cursor, category_id):
        cursor.execute('SELECT * FROM category WHERE id = ?', (category_id,))
        category_data = cursor.fetchone()
        if not category_data:
            return None
        return self._dict_to_category(category_data)
    
    # ------- CREATE ------- #
    @db_connection
    def create(self, cursor, name, display_order=None):
        try:
            if display_order is None:
                cursor.execute('SELECT COALESCE(MAX(display_order), -1) FROM category')
                result = cursor.fetchone()
                display_order = (result[0] or -1) + 1
            
            cursor.execute(
                'INSERT INTO category (name, display_order) VALUES (?, ?)',
                (name, display_order)
            )
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating category: {e}")
            return None
    
    # ------- UPDATE ------- #
    @db_connection
    def update(self, cursor, category_id, name, display_order):
        try:
            if self.is_display_order_taken(display_order, category_id):
                display_order = self.get_next_available_display_order()
                print(f"Display order conflict resolved: using {display_order}")
            
            cursor.execute(
                'UPDATE category SET name = ?, display_order = ? WHERE id = ?',
                (name, display_order, category_id)
            )
            return True
        except Exception as e:
            print(f"Error updating category: {e}")
            return False
    
    # ------- DELETE ------- #
    @db_connection
    def delete(self, cursor, category_id):
        try:
            cursor.execute('DELETE FROM category WHERE id = ?', (category_id,))
            return True
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False
    
    # ------- REORDER CATEGORIES ------- #
    @db_connection
    def reorder_categories(self, cursor, category_order):
        try:
            cursor.execute('UPDATE category SET display_order = display_order + 1000')
            
            for display_order, category_id in enumerate(category_order):
                cursor.execute(
                    'UPDATE category SET display_order = ? WHERE id = ?',
                    (display_order, category_id)
                )
            
            return True
        except Exception as e:
            print(f"Error reordering categories: {e}")
            return False
    
    # ------- BY CATEGORY WITH TOPICS ------- #
    @db_connection
    def get_topics_by_category(self, cursor):
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
            
            if category_data['topic_ids']:
                topic_ids = [int(id) for id in category_data['topic_ids'].split(',')]
                placeholders = ','.join(['?'] * len(topic_ids))
                
                cursor.execute(f'''
                    SELECT * FROM topic 
                    WHERE id IN ({placeholders}) 
                    ORDER BY display_order, title
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
        
        return dict(sorted(categorized_topics.items(), key=lambda x: x[1]['display_order']))
    
    # ------- DISPLAY ORDER VALIDATION ------- #
    @db_connection
    def is_display_order_taken(self, cursor, display_order, exclude_category_id=None):
        query = 'SELECT id FROM category WHERE display_order = ?'
        params = [display_order]
        
        if exclude_category_id:
            query += ' AND id != ?'
            params.append(exclude_category_id)
            
        cursor.execute(query, params)
        return cursor.fetchone() is not None

    # ------- NEXT AVAILABLE DISPLAY ORDER ------- #
    @db_connection
    def get_next_available_display_order(self, cursor):
        cursor.execute('SELECT MAX(display_order) FROM category')
        result = cursor.fetchone()
        return (result[0] or -1) + 1

    # ------- CONVERT DB ROW TO CATEGORY OBJECT ------- #
    def _dict_to_category(self, category_data):
        category = CategoryModel()
        category.id = category_data['id']
        category.name = category_data['name']
        category.display_order = category_data['display_order']
        category.created_at = category_data['created_at']
        return category