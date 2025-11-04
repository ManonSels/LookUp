from flask import Blueprint, render_template, current_app
from app.models.topic import TopicModel
from app.models.section import SectionModel
from app.models.section_item import SectionItemModel
from app.models.category import CategoryModel
from datetime import datetime

bp = Blueprint('home', __name__)

# ----- HOME ROUTE ----- #
@bp.route('/')
def index():
    try:
        category_model = CategoryModel()
        
        # Use the same method as admin dashboard for consistent ordering
        topic_model = TopicModel()
        categorized_topics = topic_model.get_all_grouped_by_category()
        
        # Get ALL topics (including unpublished) for recent updates
        all_topics = topic_model.get_all()
        
        # Sort by updated_at properly
        def get_updated_at(topic):
            updated_at = getattr(topic, 'updated_at', None)
            if not updated_at:
                return getattr(topic, 'created_at', '2000-01-01')
            return updated_at
        
        # Sort by updated_at in descending order (most recent first)
        recent_topics = sorted(all_topics, key=get_updated_at, reverse=True)[:4]
        
        # Get most viewed topics
        most_viewed_topics = topic_model.get_most_viewed(limit=4)
        
        return render_template('home.html', 
                            categorized_topics=categorized_topics,
                            recent_topics=recent_topics,
                            most_viewed_topics=most_viewed_topics)
    except Exception as e:
        current_app.logger.error(f"Error in home route: {e}")
        return render_template('home.html', 
                            categorized_topics={},
                            recent_topics=[],
                            most_viewed_topics=[])


# ----- TOPIC SLUG ----- #
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
        return render_template('cheatsheet.html', topic=topic)
    except Exception as e:
        current_app.logger.error(f"Error in cheatsheet route for {topic_slug}: {e}")
        return "Error loading topic", 500