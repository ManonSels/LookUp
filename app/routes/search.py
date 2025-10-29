from flask import Blueprint, request, jsonify
from app.models.topic import TopicModel
from app.models.section import SectionModel
from app.models.section_item import SectionItemModel
from app.models.category import CategoryModel

search_bp = Blueprint('search', __name__)

@search_bp.route('/search/topics')
def get_all_topics():
    """Get all published topics for the left sidebar"""
    topic_model = TopicModel()
    category_model = CategoryModel()
    
    # Get categorized topics
    categorized_topics = category_model.get_topics_by_category()
    
    # Flatten the structure for the search sidebar
    all_topics = []
    for category_name, category_data in categorized_topics.items():
        for topic in category_data['topics']:
            all_topics.append({
                'id': topic.id,
                'slug': topic.slug,
                'title': topic.title,
                'description': topic.description,
                'category': category_name
            })
    
    return jsonify({'topics': all_topics})

@search_bp.route('/search/topic/<int:topic_id>')
def get_topic_content(topic_id):
    """Get all sections and items for a specific topic"""
    section_model = SectionModel()
    item_model = SectionItemModel()
    topic_model = TopicModel()
    
    topic = topic_model.get_by_id(topic_id)
    if not topic:
        return jsonify({'error': 'Topic not found'}), 404
    
    sections = section_model.get_by_topic(topic_id)
    
    for section in sections:
        section.items = item_model.get_by_section(section.id)
    
    return jsonify({
        'topic': {
            'id': topic.id,
            'slug': topic.slug,
            'title': topic.title,
            'description': topic.description
        },
        'sections': [{
            'id': section.id,
            'title': section.title,
            'items': [{
                'id': item.id,
                'title': item.title
            } for item in section.items]
        } for section in sections]
    })

@search_bp.route('/search/query')
def search_query():
    """Search across all content and return complete topic structures for matches"""
    query = request.args.get('q', '').strip().lower()
    
    topic_model = TopicModel()
    section_model = SectionModel()
    item_model = SectionItemModel()
    
    # Get all published topics
    all_topics = topic_model.get_all_published()
    matching_topics = []
    
    if not query:
        return jsonify({'results': []})
    
    for topic in all_topics:
        # Check if topic matches
        topic_matches = (query in topic.title.lower() or 
                        (topic.description and query in topic.description.lower()))
        
        # Get all sections for this topic to check for matches
        sections = section_model.get_by_topic(topic.id)
        matching_sections = []
        
        for section in sections:
            section_matches = query in section.title.lower()
            
            # Get all items for this section to check for matches
            items = item_model.get_by_section(section.id)
            matching_items = []
            
            for item in items:
                item_matches = (query in item.title.lower() or 
                               query in (item.markdown_content or '').lower())
                
                if item_matches:
                    matching_items.append({
                        'id': item.id,
                        'title': item.title
                    })
            
            # Include section if it matches or has matching items
            if section_matches or matching_items:
                matching_sections.append({
                    'id': section.id,
                    'title': section.title,
                    'items': matching_items
                })
            # If topic matches, include ALL sections with ALL items
            elif topic_matches:
                matching_sections.append({
                    'id': section.id,
                    'title': section.title,
                    'items': [{
                        'id': item.id,
                        'title': item.title
                    } for item in items]
                })
        
        # If topic matches, include ALL sections (even if they don't match individually)
        if topic_matches:
            # Re-fetch all sections with all items for this topic
            all_sections = section_model.get_by_topic(topic.id)
            complete_sections = []
            
            for section in all_sections:
                items = item_model.get_by_section(section.id)
                complete_sections.append({
                    'id': section.id,
                    'title': section.title,
                    'items': [{
                        'id': item.id,
                        'title': item.title
                    } for item in items]
                })
            
            matching_topics.append({
                'topic': {
                    'id': topic.id,
                    'slug': topic.slug,
                    'title': topic.title,
                    'description': topic.description
                },
                'sections': complete_sections,
                'match_type': 'topic'
            })
        # If we have matching sections/items (but topic doesn't match)
        elif matching_sections:
            matching_topics.append({
                'topic': {
                    'id': topic.id,
                    'slug': topic.slug,
                    'title': topic.title,
                    'description': topic.description
                },
                'sections': matching_sections,
                'match_type': 'content'
            })
    
    return jsonify({'results': matching_topics})