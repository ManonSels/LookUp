from flask import Blueprint, render_template, current_app
from app.models.topic import TopicModel
from app.models.section import SectionModel
from app.models.section_item import SectionItemModel
from datetime import datetime

bp = Blueprint('home', __name__)

def get_footer_data():
    """function to get data for footer (recent and most viewed topics)"""
    try:
        topic_model = TopicModel()
        all_topics = topic_model.get_all()
        
        def get_updated_at(topic):
            updated_at = getattr(topic, 'updated_at', None)
            if not updated_at:
                return getattr(topic, 'created_at', datetime.now())
            return updated_at
        
        recent_topics = sorted(all_topics, key=get_updated_at, reverse=True)[:4]
        most_viewed_topics = topic_model.get_most_viewed(limit=4)
        
        return recent_topics, most_viewed_topics
    except Exception as e:
        current_app.logger.error(f"Error getting footer data: {e}")
        return [], []

@bp.route('/')
def index():
    try:
        topic_model = TopicModel()
        categorized_topics = topic_model.get_all_grouped_by_category()
        
        recent_topics, most_viewed_topics = get_footer_data()
        
        return render_template('home.html', 
                            categorized_topics=categorized_topics,
                            recent_topics=recent_topics,
                            most_viewed_topics=most_viewed_topics)
    
    except Exception as e:
        current_app.logger.error(f"Error in home route: {e}")
        recent_topics, most_viewed_topics = get_footer_data()
        return render_template('home.html', 
                            categorized_topics={},
                            recent_topics=recent_topics,
                            most_viewed_topics=most_viewed_topics)

@bp.route('/<topic_slug>')
def cheatsheet(topic_slug):
    try:
        topic_model = TopicModel()
        section_model = SectionModel()
        item_model = SectionItemModel()
        topic = topic_model.get_by_slug(topic_slug)
        if not topic:
            return "Topic not found", 404
        
        sections = section_model.get_by_topic(topic.id)
        for section in sections:
            section.items = item_model.get_by_section(section.id)
        
        topic.sections = sections
        
        # Get footer data for cheatsheet pages too
        recent_topics, most_viewed_topics = get_footer_data()
        
        return render_template('cheatsheet.html', 
                            topic=topic,
                            recent_topics=recent_topics,
                            most_viewed_topics=most_viewed_topics)
    except Exception as e:
        current_app.logger.error(f"Error in cheatsheet route for {topic_slug}: {e}")
        return "Error loading topic", 500