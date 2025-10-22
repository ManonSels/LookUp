from flask import Blueprint, render_template
from app.models.topic import TopicModel
from app.models.section import SectionModel
from app.models.section_item import SectionItemModel
from app.models.category import CategoryModel

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    category_model = CategoryModel()
    categorized_topics = category_model.get_topics_by_category()
    
    return render_template('home.html', categorized_topics=categorized_topics)

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