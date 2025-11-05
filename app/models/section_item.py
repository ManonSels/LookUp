from .database import db_connection

class SectionItemModel:
    @db_connection
    def get_by_section(self, cursor, section_id):
        cursor.execute(
            'SELECT * FROM section_item WHERE section_id = ? ORDER BY display_order, id',
            (section_id,)
        )
        items_data = cursor.fetchall()
        return [self._dict_to_item(item) for item in items_data]
    
    @db_connection
    def get_by_id(self, cursor, item_id):
        cursor.execute('SELECT * FROM section_item WHERE id = ?', (item_id,))
        item_data = cursor.fetchone()
        return self._dict_to_item(item_data) if item_data else None
    
    @db_connection
    def create_item(self, cursor, title, section_id, markdown_content="", display_order=0, card_size='normal', bookmark_color='#3b82f6'):
        cursor.execute(
            'INSERT INTO section_item (title, markdown_content, display_order, card_size, bookmark_color, section_id) VALUES (?, ?, ?, ?, ?, ?)',
            (title, markdown_content, display_order, card_size, bookmark_color, section_id)
        )
        
        cursor.execute('''
            UPDATE topic SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = (SELECT topic_id FROM section WHERE id = ?)
        ''', (section_id,))
        
        return cursor.lastrowid
    
    @db_connection
    def update_item(self, cursor, item_id, title, markdown_content, display_order, card_size='normal', bookmark_color='#3b82f6'):
        cursor.execute(
            'UPDATE section_item SET title = ?, markdown_content = ?, display_order = ?, card_size = ?, bookmark_color = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (title, markdown_content, display_order, card_size, bookmark_color, item_id)
        )
        
        cursor.execute('''
            UPDATE topic SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = (
                SELECT topic_id FROM section 
                WHERE id = (SELECT section_id FROM section_item WHERE id = ?)
            )
        ''', (item_id,))
        
        return True
    
    @db_connection
    def delete_item(self, cursor, item_id):
        cursor.execute('SELECT section_id FROM section_item WHERE id = ?', (item_id,))
        result = cursor.fetchone()
        section_id = result['section_id'] if result else None
        
        cursor.execute('DELETE FROM section_item WHERE id = ?', (item_id,))
        
        if section_id:
            cursor.execute('''
                UPDATE topic SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = (SELECT topic_id FROM section WHERE id = ?)
            ''', (section_id,))
        
        return True
    
    def _dict_to_item(self, item_data):
        item = SectionItemModel()
        item.id = item_data['id']
        item.title = item_data['title']
        item.markdown_content = item_data['markdown_content']
        item.display_order = item_data['display_order']
        
        try:
            item.card_size = item_data['card_size']
        except (KeyError, AttributeError):
            item.card_size = 'normal'
        
        try:
            item.bookmark_color = item_data['bookmark_color']
        except (KeyError, AttributeError):
            item.bookmark_color = '#3b82f6'
        
        item.section_id = item_data['section_id']
        item.created_at = item_data['created_at']
        item.updated_at = item_data['updated_at']
        return item