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
        
        if not item_data:
            return None
        
        return self._dict_to_item(item_data)
    
    @db_connection
    def create_item(self, cursor, title, section_id, markdown_content="", display_order=0):
        cursor.execute(
            'INSERT INTO section_item (title, markdown_content, display_order, section_id) VALUES (?, ?, ?, ?)',
            (title, markdown_content, display_order, section_id)
        )
        return cursor.lastrowid
    
    @db_connection
    def update_item(self, cursor, item_id, title, markdown_content, display_order):
        cursor.execute(
            'UPDATE section_item SET title = ?, markdown_content = ?, display_order = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (title, markdown_content, display_order, item_id)
        )
        return True
    
    @db_connection
    def delete_item(self, cursor, item_id):
        cursor.execute('DELETE FROM section_item WHERE id = ?', (item_id,))
        return True
    
    def _dict_to_item(self, item_data):
        item = SectionItemModel()
        item.id = item_data['id']
        item.title = item_data['title']
        item.markdown_content = item_data['markdown_content']
        item.display_order = item_data['display_order']
        item.section_id = item_data['section_id']
        item.created_at = item_data['created_at']
        item.updated_at = item_data['updated_at']
        return item