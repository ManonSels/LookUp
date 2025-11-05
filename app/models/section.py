from .database import db_connection

class SectionModel:
    @db_connection
    def get_by_topic(self, cursor, topic_id):
        cursor.execute(
            'SELECT * FROM section WHERE topic_id = ? ORDER BY display_order, id',
            (topic_id,)
        )
        sections_data = cursor.fetchall()
        return [self._dict_to_section(section) for section in sections_data]
    
    @db_connection
    def get_by_id(self, cursor, section_id):
        cursor.execute('SELECT * FROM section WHERE id = ?', (section_id,))
        section_data = cursor.fetchone()
        return self._dict_to_section(section_data) if section_data else None
    
    @db_connection
    def create_section(self, cursor, title, topic_id, display_order=0):
        cursor.execute(
            'INSERT INTO section (title, topic_id, display_order) VALUES (?, ?, ?)',
            (title, topic_id, display_order)
        )
        section_id = cursor.lastrowid
        
        cursor.execute(
            'UPDATE topic SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (topic_id,)
        )
        
        return section_id
    
    @db_connection
    def update_section(self, cursor, section_id, title, display_order):
        try:
            cursor.execute('SELECT topic_id FROM section WHERE id = ?', (section_id,))
            result = cursor.fetchone()
            topic_id = result['topic_id'] if result else None
            
            cursor.execute(
                'UPDATE section SET title = ?, display_order = ? WHERE id = ?',
                (title, display_order, section_id)
            )
            
            if topic_id:
                cursor.execute(
                    'UPDATE topic SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (topic_id,)
                )
            
            return True
        except Exception as e:
            print(f"Error updating section: {e}")
            return False
    
    @db_connection
    def delete_section(self, cursor, section_id):
        try:
            cursor.execute('SELECT topic_id FROM section WHERE id = ?', (section_id,))
            result = cursor.fetchone()
            topic_id = result['topic_id'] if result else None
            
            cursor.execute('DELETE FROM section WHERE id = ?', (section_id,))
            
            if topic_id:
                cursor.execute(
                    'UPDATE topic SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (topic_id,)
                )
            
            return True
        except Exception as e:
            print(f"Error deleting section: {e}")
            return False
        
    def _dict_to_section(self, section_data):
        section = SectionModel()
        section.id = section_data['id']
        section.title = section_data['title']
        section.display_order = section_data['display_order']
        section.topic_id = section_data['topic_id']
        return section