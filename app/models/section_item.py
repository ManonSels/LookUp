from .database import db_connection

class SectionItemModel:
    # ----- BY SECTION ----- #
    @db_connection
    def get_by_section(self, cursor, section_id):
        cursor.execute(
            'SELECT * FROM section_item WHERE section_id = ? ORDER BY display_order, id',
            (section_id,)
        )
        items_data = cursor.fetchall()
        return [self._dict_to_item(item) for item in items_data]
    
    # ----- BY ID ----- #
    @db_connection
    def get_by_id(self, cursor, item_id):
        cursor.execute('SELECT * FROM section_item WHERE id = ?', (item_id,))
        item_data = cursor.fetchone()
        
        if not item_data:
            return None
        
        return self._dict_to_item(item_data)
    
    # ----- CREATE ITEM ----- #
    @db_connection
    def create_item(self, cursor, title, section_id, markdown_content="", display_order=0, card_size='normal', bookmark_color='#3b82f6'):
        cursor.execute(
            'INSERT INTO section_item (title, markdown_content, display_order, card_size, bookmark_color, section_id) VALUES (?, ?, ?, ?, ?, ?)',
            (title, markdown_content, display_order, card_size, bookmark_color, section_id)
        )
        
        # Update topic timestamp via section in a single query
        cursor.execute('''
            UPDATE topic SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = (SELECT topic_id FROM section WHERE id = ?)
        ''', (section_id,))
        
        return cursor.lastrowid
    
    # ----- UPDATE ITEM ----- #
    @db_connection
    def update_item(self, cursor, item_id, title, markdown_content, display_order, card_size='normal', bookmark_color='#3b82f6'):
        cursor.execute(
            'UPDATE section_item SET title = ?, markdown_content = ?, display_order = ?, card_size = ?, bookmark_color = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (title, markdown_content, display_order, card_size, bookmark_color, item_id)
        )
        
        # Update topic timestamp via section
        cursor.execute('''
            UPDATE topic SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = (
                SELECT topic_id FROM section 
                WHERE id = (SELECT section_id FROM section_item WHERE id = ?)
            )
        ''', (item_id,))
        
        return True
    
    # ----- DELETE ITEM ----- #
    @db_connection
    def delete_item(self, cursor, item_id):
        # Get section_id first
        cursor.execute('SELECT section_id FROM section_item WHERE id = ?', (item_id,))
        result = cursor.fetchone()
        section_id = result['section_id'] if result else None
        
        cursor.execute('DELETE FROM section_item WHERE id = ?', (item_id,))
        
        # Update topic timestamp
        if section_id:
            cursor.execute('''
                UPDATE topic SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = (SELECT topic_id FROM section WHERE id = ?)
            ''', (section_id,))
        
        return True
    
    # ----- CONVERT DB ROW TO SECTION OBJECT ----- #
    def _dict_to_item(self, item_data):
        item = SectionItemModel()
        item.id = item_data['id']
        item.title = item_data['title']
        item.markdown_content = item_data['markdown_content']
        item.display_order = item_data['display_order']
        
        # Handle card_size
        try:
            item.card_size = item_data['card_size']
        except (KeyError, AttributeError):
            item.card_size = 'normal'
        
        # Handle bookmark_color
        try:
            item.bookmark_color = item_data['bookmark_color']
        except (KeyError, AttributeError):
            item.bookmark_color = '#3b82f6'
        
        item.section_id = item_data['section_id']
        item.created_at = item_data['created_at']
        item.updated_at = item_data['updated_at']
        return item