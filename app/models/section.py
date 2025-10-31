from .database import db_connection

class SectionModel:
    # ----- BY TOPIC ----- #
    @db_connection
    def get_by_topic(self, cursor, topic_id):
        cursor.execute(
            'SELECT * FROM section WHERE topic_id = ? ORDER BY display_order, id',
            (topic_id,)
        )
        sections_data = cursor.fetchall()
        return [self._dict_to_section(section) for section in sections_data]
    
    # ----- BY ID ----- #
    @db_connection
    def get_by_id(self, cursor, section_id):
        cursor.execute('SELECT * FROM section WHERE id = ?', (section_id,))
        section_data = cursor.fetchone()
        
        if not section_data:
            return None
        
        return self._dict_to_section(section_data)
    
    # ----- CREATE SECTION ----- #
    @db_connection
    def create_section(self, cursor, title, topic_id, display_order=0):
        cursor.execute(
            'INSERT INTO section (title, topic_id, display_order) VALUES (?, ?, ?)',
            (title, topic_id, display_order)
        )
        section_id = cursor.lastrowid
        
        # Update topic timestamp in a single query to avoid circular imports
        cursor.execute(
            'UPDATE topic SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (topic_id,)
        )
        
        return section_id
    
    # ----- UPDATE SECTION ----- #
    @db_connection
    def update_section(self, cursor, section_id, title, display_order):
        try:
            # Get topic_id first
            cursor.execute('SELECT topic_id FROM section WHERE id = ?', (section_id,))
            result = cursor.fetchone()
            topic_id = result['topic_id'] if result else None
            
            cursor.execute(
                'UPDATE section SET title = ?, display_order = ? WHERE id = ?',
                (title, display_order, section_id)
            )
            
            # Update topic timestamp
            if topic_id:
                cursor.execute(
                    'UPDATE topic SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (topic_id,)
                )
            
            return True
        except Exception as e:
            print(f"Error updating section: {e}")
            return False
    
    # ----- DELETE SECTION ----- #
    @db_connection
    def delete_section(self, cursor, section_id):
        try:
            # Get topic_id first
            cursor.execute('SELECT topic_id FROM section WHERE id = ?', (section_id,))
            result = cursor.fetchone()
            topic_id = result['topic_id'] if result else None
            
            cursor.execute('DELETE FROM section WHERE id = ?', (section_id,))
            
            # Update topic timestamp
            if topic_id:
                cursor.execute(
                    'UPDATE topic SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (topic_id,)
                )
            
            return True
        except Exception as e:
            print(f"Error deleting section: {e}")
            return False
        
    # ----- CONVERT DB ROW TO SECTION OBJECT ----- #
    def _dict_to_section(self, section_data):
        section = SectionModel()
        section.id = section_data['id']
        section.title = section_data['title']
        section.display_order = section_data['display_order']
        section.topic_id = section_data['topic_id']
        return section