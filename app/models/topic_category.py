from .database import db_connection

class TopicCategoryModel:
    # ----- GET CATEGORIES FOR TOPIC ----- #
    @db_connection
    def get_categories_for_topic(self, cursor, topic_id):
        cursor.execute('''
            SELECT c.* FROM category c
            JOIN topic_category tc ON c.id = tc.category_id
            WHERE tc.topic_id = ?
            ORDER BY tc.display_order, c.name
        ''', (topic_id,))
        categories_data = cursor.fetchall()
        
        from app.models.category import CategoryModel
        category_model = CategoryModel()
        return [category_model._dict_to_category(cat) for cat in categories_data]
    
    # ----- GET TOPICS FOR CATEGORY ----- #
    @db_connection
    def get_topics_for_category(self, cursor, category_id):
        cursor.execute('''
            SELECT t.* FROM topic t
            JOIN topic_category tc ON t.id = tc.topic_id
            WHERE tc.category_id = ? AND t.is_published = 1
            ORDER BY tc.display_order, t.title
        ''', (category_id,))
        topics_data = cursor.fetchall()
        
        from app.models.topic import TopicModel
        topic_model = TopicModel()
        return [topic_model._dict_to_topic(topic) for topic in topics_data]
    
    # ----- ADD TOPIC TO CATEGORY ----- #
    @db_connection
    def add_topic_to_category(self, cursor, topic_id, category_id, display_order=None):
        if display_order is None:
            cursor.execute('SELECT COALESCE(MAX(display_order), -1) FROM topic_category WHERE category_id = ?', (category_id,))
            result = cursor.fetchone()
            display_order = (result[0] or -1) + 1
        
        try:
            cursor.execute(
                'INSERT INTO topic_category (topic_id, category_id, display_order) VALUES (?, ?, ?)',
                (topic_id, category_id, display_order)
            )
            return True
        except Exception as e:
            print(f"Error adding topic to category: {e}")
            return False
    
    # ----- REMOVE TOPIC FROM CATEGORY ----- #
    @db_connection
    def remove_topic_from_category(self, cursor, topic_id, category_id):
        cursor.execute(
            'DELETE FROM topic_category WHERE topic_id = ? AND category_id = ?',
            (topic_id, category_id)
        )
        return True
    
    # ----- SET TOPIC CATEGORIES ----- #
    @db_connection
    def set_topic_categories(self, cursor, topic_id, category_ids):
        # Remove existing categories
        cursor.execute('DELETE FROM topic_category WHERE topic_id = ?', (topic_id,))
        
        # Add new categories with proper display order
        for display_order, category_id in enumerate(category_ids):
            cursor.execute(
                'INSERT INTO topic_category (topic_id, category_id, display_order) VALUES (?, ?, ?)',
                (topic_id, category_id, display_order)
            )
        return True
    
    # ----- UPDATE TOPIC CATEGORY ORDER ----- #
    @db_connection
    def update_topic_category_order(self, cursor, topic_id, category_id, display_order):
        cursor.execute(
            'UPDATE topic_category SET display_order = ? WHERE topic_id = ? AND category_id = ?',
            (display_order, topic_id, category_id)
        )
        return True
    
    # ----- GET ALL TOPIC CATEGORIES ----- #
    @db_connection
    def get_all_topic_categories(self, cursor):
        cursor.execute('''
            SELECT t.id as topic_id, t.title as topic_title, 
                   c.id as category_id, c.name as category_name,
                   tc.display_order
            FROM topic_category tc
            JOIN topic t ON tc.topic_id = t.id
            JOIN category c ON tc.category_id = c.id
            ORDER BY c.display_order, tc.display_order
        ''')
        return cursor.fetchall()
    
    # ----- CHECK IF TOPIC IN CATEGORY ----- #
    @db_connection
    def is_topic_in_category(self, cursor, topic_id, category_id):
        cursor.execute(
            'SELECT id FROM topic_category WHERE topic_id = ? AND category_id = ?',
            (topic_id, category_id)
        )
        return cursor.fetchone() is not None