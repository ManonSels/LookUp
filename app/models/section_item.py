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
    def create_item(self, cursor, title, section_id, markdown_content="", display_order=0, card_size='normal'):  # ADD card_size
        cursor.execute(
            'INSERT INTO section_item (title, markdown_content, display_order, card_size, section_id) VALUES (?, ?, ?, ?, ?)',  # UPDATE
            (title, markdown_content, display_order, card_size, section_id)  # UPDATE
        )
        return cursor.lastrowid

    # ----- UPDATE ITEM ----- #
    @db_connection
    def update_item(self, cursor, item_id, title, markdown_content, display_order, card_size='normal'):  # ADD card_size
        cursor.execute(
            'UPDATE section_item SET title = ?, markdown_content = ?, display_order = ?, card_size = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',  # UPDATE
            (title, markdown_content, display_order, card_size, item_id)  # UPDATE
        )
        return True
        
    # ----- DELETE ITEM ----- #
    @db_connection
    def delete_item(self, cursor, item_id):
        cursor.execute('DELETE FROM section_item WHERE id = ?', (item_id,))
        return True
    
    # ----- CONVERT DB ROW TO SECTION OBJECT ----- #
    def _dict_to_item(self, item_data):
        # Convert sqlite3.Row to dict if needed
        if hasattr(item_data, 'keys'):
            item_data = dict(item_data)
        
        item = SectionItemModel()
        item.id = item_data['id']
        item.title = item_data['title']
        item.markdown_content = item_data['markdown_content']
        item.display_order = item_data['display_order']
        # Use get() for card_size since it might be a new column in existing databases
        item.card_size = item_data.get('card_size', 'normal') if isinstance(item_data, dict) else getattr(item_data, 'card_size', 'normal')
        item.section_id = item_data['section_id']
        item.created_at = item_data['created_at']
        item.updated_at = item_data['updated_at']
        return item