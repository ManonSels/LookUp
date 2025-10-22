from flask import Blueprint, render_template, jsonify 
from app.models.topic import TopicModel
from app.models.section import SectionModel
from app.models.section_item import SectionItemModel
from app.models.category import CategoryModel

# Create blueprint (note the variable name matches your import)
bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    try:
        # Try the new category system first
        category_model = CategoryModel()
        categorized_topics = category_model.get_topics_by_category()
        
        # Check if we actually got valid data
        if categorized_topics and len(categorized_topics) > 0:
            print(f"✅ Using category system with {len(categorized_topics)} categories")
            return render_template('home.html', categorized_topics=categorized_topics)
        else:
            # Category system returned empty or None
            print("❌ Category system returned empty, using fallback")
            raise Exception("No categories found")
            
    except Exception as e:
        print(f"Category system failed: {e}")
        # Fallback to simple topic list
        topic_model = TopicModel()
        topics = topic_model.get_all_published()
        print(f"✅ Using fallback with {len(topics)} topics")
        return render_template('home.html', topics=topics)

@bp.route('/<topic_slug>')
def cheatsheet(topic_slug):
    topic_model = TopicModel()
    section_model = SectionModel()
    item_model = SectionItemModel()
    
    topic = topic_model.get_by_slug(topic_slug)
    if not topic:
        return "Topic not found", 404
    
    # Get sections and items for this topic
    sections = section_model.get_by_topic(topic.id)
    for section in sections:
        section.items = item_model.get_by_section(section.id)
    
    topic.sections = sections
    return render_template('cheatsheet.html', topic=topic)




@bp.route('/debug-data')
def debug_data():
    topic_model = TopicModel()
    topics = topic_model.get_all_published()
    
    try:
        category_model = CategoryModel()
        categorized = category_model.get_topics_by_category()
        category_info = f"Categories: {len(categorized)} - {list(categorized.keys())}"
    except Exception as e:
        category_info = f"Category error: {e}"
    
    debug_info = {
        'published_topics_count': len(topics),
        'published_topics': [{'id': t.id, 'title': t.title, 'slug': t.slug, 'is_published': t.is_published} for t in topics],
        'category_system': category_info
    }
    
    return jsonify(debug_info)

@bp.route('/debug-homepage')
def debug_homepage():
    topic_model = TopicModel()
    topics = topic_model.get_all_published()
    
    # Check categories
    try:
        category_model = CategoryModel()
        categorized = category_model.get_topics_by_category()
        has_categories = len(categorized) > 0
    except Exception as e:
        has_categories = False
        category_error = str(e)
    
    return f"""
    <h1>Homepage Debug</h1>
    <p>Published topics: {len(topics)}</p>
    <p>Topics found: {[t.title for t in topics]}</p>
    <p>Categories working: {has_categories}</p>
    <p>Category error: {category_error if not has_categories else 'None'}</p>
    <p>Template variables being passed: categorized_topics={has_categories}, topics={len(topics) > 0}</p>
    """