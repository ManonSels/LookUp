from flask import Blueprint, request, jsonify
from app.models.topic import TopicModel
from app.models.section import SectionModel
from app.models.section_item import SectionItemModel

search_bp = Blueprint('search', __name__)

@search_bp.route('/search/topics')
def get_all_topics():
    """Get ALL topics (including unpublished) for the admin search sidebar"""
    try:
        topic_model = TopicModel()
        all_topics = topic_model.get_all()
        
        categorized_topics = {}
        for topic in all_topics:
            category_id = topic.category_id
            category_name = topic.category_name if hasattr(topic, 'category_name') else 'Uncategorized'
            
            if category_id not in categorized_topics:
                categorized_topics[category_id] = {
                    'name': category_name,
                    'topics': []
                }
            
            categorized_topics[category_id]['topics'].append({
                'id': topic.id,
                'slug': topic.slug,
                'title': topic.title,
                'description': topic.description,
                'category': category_name,
                'is_published': topic.is_published
            })
        
        all_topics_flat = []
        for category_data in categorized_topics.values():
            for topic in category_data['topics']:
                all_topics_flat.append(topic)
        
        return jsonify({'topics': all_topics_flat})
    except Exception as e:
        print(f"Error in get_all_topics: {e}")
        return jsonify({'topics': []})

@search_bp.route('/search/topic/<int:topic_id>')
def get_topic_content(topic_id):
    """Get all sections and items for a specific topic"""
    try:
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
                'description': topic.description,
                'is_published': topic.is_published
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
    except Exception as e:
        print(f"Error in get_topic_content: {e}")
        return jsonify({'error': 'Error loading topic content'}), 500

@search_bp.route('/search/query')
def search_query():
    """Search across all content and return complete topic structures for matches"""
    try:
        query = request.args.get('q', '').strip().lower()
        
        topic_model = TopicModel()
        section_model = SectionModel()
        item_model = SectionItemModel()
        
        all_topics = topic_model.get_all()
        matching_topics = []
        
        if not query:
            return jsonify({'results': []})
        
        for topic in all_topics:
            topic_matches = (query in topic.title.lower() or 
                            (topic.description and query in topic.description.lower()))
            
            sections = section_model.get_by_topic(topic.id)
            matching_sections = []
            
            for section in sections:
                section_matches = query in section.title.lower()
                
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
                
                if section_matches or matching_items:
                    matching_sections.append({
                        'id': section.id,
                        'title': section.title,
                        'items': matching_items
                    })
                elif topic_matches:
                    matching_sections.append({
                        'id': section.id,
                        'title': section.title,
                        'items': [{
                            'id': item.id,
                            'title': item.title
                        } for item in items]
                    })
            
            if topic_matches:
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
                        'description': topic.description,
                        'is_published': topic.is_published
                    },
                    'sections': complete_sections,
                    'match_type': 'topic'
                })
            elif matching_sections:
                matching_topics.append({
                    'topic': {
                        'id': topic.id,
                        'slug': topic.slug,
                        'title': topic.title,
                        'description': topic.description,
                        'is_published': topic.is_published
                    },
                    'sections': matching_sections,
                    'match_type': 'content'
                })
        
        return jsonify({'results': matching_topics})
    except Exception as e:
        print(f"Error in search_query: {e}")
        return jsonify({'results': []})