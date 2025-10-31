from flask import Blueprint, render_template
from app.models.topic import TopicModel
from app.models.section import SectionModel
from app.models.section_item import SectionItemModel
from app.models.category import CategoryModel
from datetime import datetime

bp = Blueprint('home', __name__)

# ----- HOME ROUTE ----- #
@bp.route('/')
def index():
    category_model = CategoryModel()
    categorized_topics = category_model.get_topics_by_category()
    
    # Get ALL topics (including unpublished) for recent updates
    topic_model = TopicModel()
    all_topics = topic_model.get_all()  # Changed from get_all_published()
    
    # Sort by updated_at properly
    def get_updated_at(topic):
        # Handle both string and datetime objects
        updated_at = getattr(topic, 'updated_at', None)
        if not updated_at:
            return getattr(topic, 'created_at', '2000-01-01')
        return updated_at
    
    # Sort by updated_at in descending order (most recent first)
    recent_topics = sorted(all_topics, key=get_updated_at, reverse=True)[:4]
    
    return render_template('home.html', 
                         categorized_topics=categorized_topics,
                         recent_topics=recent_topics)

# ----- TOPIC SLUG ----- #
@bp.route('/<topic_slug>')
def cheatsheet(topic_slug):
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