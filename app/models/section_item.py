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
    def create_item(self, cursor, title, section_id, description=None, url=None, code=None, item_type='default', display_order=0):
        cursor.execute(
            'INSERT INTO section_item (title, description, url, code, item_type, display_order, section_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, description, url, code, item_type, display_order, section_id)
        )
        return cursor.lastrowid
    
    @db_connection
    def update_item(self, cursor, item_id, title, description, url, code, item_type, display_order):
        cursor.execute(
            'UPDATE section_item SET title = ?, description = ?, url = ?, code = ?, item_type = ?, display_order = ? WHERE id = ?',
            (title, description, url, code, item_type, display_order, item_id)
        )
        return True
    
    @db_connection
    def delete_item(self, cursor, item_id):
        cursor.execute('DELETE FROM section_item WHERE id = ?', (item_id,))
        return True
    
    def _dict_to_item(self, item_data):
        """Convert database row to SectionItem object"""
        item = SectionItemModel()
        item.id = item_data['id']
        item.title = item_data['title']
        item.description = item_data['description']
        item.url = item_data['url']
        item.code = item_data['code']
        item.item_type = item_data['item_type']
        item.display_order = item_data['display_order']
        item.section_id = item_data['section_id']
        return item