import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.topic import TopicModel
from app.models.section import SectionModel
from app.models.section_item import SectionItemModel
from app.models.category import CategoryModel 
from werkzeug.utils import secure_filename
from app.utils.upload import save_topic_logo, delete_topic_logo

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'error')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------- #
# ---------------- DASHBOARD ---------------- #
# ------------------------------------------- #

@admin_bp.route('/')
@admin_required
def dashboard():
    topic_model = TopicModel()
    category_model = CategoryModel()
    categorized_topics = topic_model.get_all_grouped_by_category()
    categories = category_model.get_all()
    
    return render_template('admin/dashboard.html', 
                         categorized_topics=categorized_topics,
                         categories=categories)


# ------------------------------------------- #
# --------------- CATEGORIES ---------------- #
# ------------------------------------------- #

@admin_bp.route('/categories')
@admin_required
def manage_categories():
    category_model = CategoryModel()
    categories = category_model.get_all()
    return render_template('admin/categories.html', categories=categories)

# ------- NEW CATEGORY ------- #
@admin_bp.route('/category/new', methods=['GET', 'POST'])
@admin_required
def new_category():
    if request.method == 'POST':
        name = request.form.get('name')
        display_order = request.form.get('display_order', type=int)
        
        if not name:
            flash('Category name is required', 'error')
            return render_template('admin/edit_category.html')
        
        category_model = CategoryModel()
        category_id = category_model.create(name, display_order)
        
        if category_id:
            flash('Category created successfully!', 'success')
            return redirect(url_for('admin.manage_categories'))
        else:
            flash('Error creating category. Name might already exist.', 'error')
    
    return render_template('admin/edit_category.html')

# ------- EDIT CATEGORY ------- #
@admin_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    category_model = CategoryModel()
    category = category_model.get_by_id(category_id)
    
    if not category:
        flash('Category not found', 'error')
        return redirect(url_for('admin.manage_categories'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        display_order = request.form.get('display_order', 0, type=int)
        
        if category_model.update(category_id, name, display_order):
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin.manage_categories'))
        else:
            flash('Error updating category', 'error')
    
    return render_template('admin/edit_category.html', category=category)


# ------- DELETE CATEGORY ------- #
@admin_bp.route('/category/<int:category_id>/delete')
@admin_required
def delete_category(category_id):
    category_model = CategoryModel()
    
    topic_model = TopicModel()
    topics = topic_model.get_by_category(category_id)
    
    if topics:
        flash('Cannot delete category that has topics. Move or delete the topics first.', 'error')
    else:
        if category_model.delete(category_id):
            flash('Category deleted successfully!', 'success')
        else:
            flash('Error deleting category', 'error')
    
    return redirect(url_for('admin.manage_categories'))

# ------ REORDER CATEGORIES ------ #
@admin_bp.route('/api/categories/reorder', methods=['POST'])
@admin_required
def api_reorder_categories():
    order_data = request.json.get('order', [])
    
    category_model = CategoryModel()
    
    if category_model.reorder_categories(order_data):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to reorder categories'})
    

# ------------------------------------------- #
# ----------------- TOPICS ------------------ #
# ------------------------------------------- #

# --------- NEW TOPIC --------- #
@admin_bp.route('/topic/new', methods=['GET', 'POST'])
@admin_required
def new_topic():
    topic_model = TopicModel()
    categories = topic_model.get_all_categories()
    
    if request.method == 'POST':
        slug = request.form.get('slug')
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id', 1, type=int)
        is_published = 'is_published' in request.form
        card_color_light = request.form.get('card_color_light', '#ffffff')
        card_color_dark = request.form.get('card_color_dark', '#1a1a1a')
        
        # Handle logo uploads
        logo_filename_light = None
        logo_filename_dark = None
        
        if 'logo_light' in request.files:
            file = request.files['logo_light']
            if file and file.filename:
                logo_filename_light = save_topic_logo(file)
                if not logo_filename_light:
                    flash('Error uploading light theme logo', 'error')
        
        if 'logo_dark' in request.files:
            file = request.files['logo_dark']
            if file and file.filename:
                logo_filename_dark = save_topic_logo(file)
                if not logo_filename_dark:
                    flash('Error uploading dark theme logo', 'error')
        
        if not slug or not title:
            flash('Slug and title are required', 'error')
            return render_template('admin/edit_topic.html', categories=categories)
        
        topic_id = topic_model.create_topic(slug, title, description, current_user.id, category_id, is_published, card_color_light, card_color_dark, logo_filename_light, logo_filename_dark)
        
        if topic_id:
            flash('Topic created successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Error creating topic. Slug might already exist.', 'error')
    
    return render_template('admin/edit_topic.html', categories=categories)

# -------- EDIT TOPIC -------- #
@admin_bp.route('/topic/<int:topic_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_topic(topic_id):
    topic_model = TopicModel()
    topic = topic_model.get_by_id(topic_id)
    categories = topic_model.get_all_categories()
    
    if not topic:
        flash('Topic not found', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        slug = request.form.get('slug')
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id', 1, type=int)
        is_published = 'is_published' in request.form
        card_color_light = request.form.get('card_color_light', '#ffffff')
        card_color_dark = request.form.get('card_color_dark', '#1a1a1a')
        remove_logo_light = 'remove_logo_light' in request.form
        remove_logo_dark = 'remove_logo_dark' in request.form
        
        # Handle logo uploads/removals
        logo_filename_light = topic.logo_filename_light if hasattr(topic, 'logo_filename_light') else None
        logo_filename_dark = topic.logo_filename_dark if hasattr(topic, 'logo_filename_dark') else None
        
        # Handle light theme logo
        if remove_logo_light and logo_filename_light:
            delete_topic_logo(logo_filename_light)
            logo_filename_light = None
        elif 'logo_light' in request.files:
            file = request.files['logo_light']
            if file and file.filename:
                if logo_filename_light:
                    delete_topic_logo(logo_filename_light)
                new_logo_filename = save_topic_logo(file)
                if new_logo_filename:
                    logo_filename_light = new_logo_filename
                else:
                    flash('Error uploading light theme logo', 'error')
        
        # Handle dark theme logo
        if remove_logo_dark and logo_filename_dark:
            delete_topic_logo(logo_filename_dark)
            logo_filename_dark = None
        elif 'logo_dark' in request.files:
            file = request.files['logo_dark']
            if file and file.filename:
                if logo_filename_dark:
                    delete_topic_logo(logo_filename_dark)
                new_logo_filename = save_topic_logo(file)
                if new_logo_filename:
                    logo_filename_dark = new_logo_filename
                else:
                    flash('Error uploading dark theme logo', 'error')
        
        if topic_model.update_topic(topic_id, slug, title, description, category_id, is_published, card_color_light, card_color_dark, logo_filename_light, logo_filename_dark):
            flash('Topic updated successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Error updating topic', 'error')
    
    return render_template('admin/edit_topic.html', topic=topic, categories=categories)

# -------- DELETE TOPIC -------- #
@admin_bp.route('/topic/<int:topic_id>/delete')
@admin_required
def delete_topic(topic_id):
    topic_model = TopicModel()
    if topic_model.delete_topic(topic_id):
        flash('Topic deleted successfully!', 'success')
    else:
        flash('Error deleting topic', 'error')
    
    return redirect(url_for('admin.dashboard'))

# ------ REORDER TOPICS ------ #
@admin_bp.route('/api/topics/reorder', methods=['POST'])
@admin_required
def api_reorder_topics():
    try:
        from app.models.database import DBConnection
        with DBConnection() as cursor:
            category_id = request.json.get('category_id')
            order_data = request.json.get('order', [])
            
            for display_order, topic_id in enumerate(order_data):
                cursor.execute(
                    'UPDATE topic SET display_order = ? WHERE id = ? AND category_id = ?',
                    (display_order, topic_id, category_id)
                )
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error reordering topics: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ------ CHANGE TOPIC CATEGORY ------ #
@admin_bp.route('/api/topics/change_category', methods=['POST'])
@admin_required
def api_change_topic_category():
    try:
        from app.models.database import DBConnection
        with DBConnection() as cursor:
            topic_id = request.json.get('topic_id')
            category_id = request.json.get('category_id')
            
            cursor.execute(
                'UPDATE topic SET category_id = ? WHERE id = ?',
                (category_id, topic_id)
            )
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error changing topic category: {e}")
        return jsonify({'success': False, 'error': str(e)})


# ------------------------------------------- #
# ---------------- SECTIONS ----------------- #
# ------------------------------------------- #

# ------- MANAGE SECTIONS ------- #
@admin_bp.route('/topic/<int:topic_id>/sections')
@admin_required
def manage_sections(topic_id):
    topic_model = TopicModel()
    section_model = SectionModel()
    item_model = SectionItemModel()
    
    topic = topic_model.get_by_id(topic_id)
    if not topic:
        flash('Topic not found', 'error')
        return redirect(url_for('admin.dashboard'))
    
    sections = section_model.get_by_topic(topic_id)
    
    for section in sections:
        section.items = item_model.get_by_section(section.id)
    
    return render_template('admin/manage_sections.html', topic=topic, sections=sections)

# --------- NEW SECTION --------- #
@admin_bp.route('/api/section/new', methods=['POST'])
@admin_required
def api_new_section():
    topic_id = request.json.get('topic_id')
    title = request.json.get('title')
    
    section_model = SectionModel()
    section_id = section_model.create_section(title, topic_id)
    
    if section_id:
        return jsonify({'success': True, 'section_id': section_id})
    else:
        return jsonify({'success': False, 'error': 'Failed to create section'})


# -------- UPDATE SECTION -------- #
@admin_bp.route('/api/section/update', methods=['POST'])
@admin_required
def api_update_section():
    section_id = request.json.get('section_id')
    title = request.json.get('title')
    display_order = request.json.get('display_order', 0)
    
    section_model = SectionModel()
    if section_model.update_section(section_id, title, display_order):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to update section'})

# -------- DELETE SECTION -------- #
@admin_bp.route('/api/section/delete', methods=['POST'])
@admin_required
def api_delete_section():
    section_id = request.json.get('section_id')
    
    section_model = SectionModel()
    if section_model.delete_section(section_id):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to delete section'})
    
# ------ REORDER SECTIONS ------ #
@admin_bp.route('/api/sections/reorder', methods=['POST'])
@admin_required
def api_reorder_sections():
    topic_id = request.json.get('topic_id')
    order_data = request.json.get('order', [])
    
    try:
        from app.models.database import DBConnection
        with DBConnection() as cursor:
            for display_order, section_id in enumerate(order_data):
                cursor.execute(
                    'UPDATE section SET display_order = ? WHERE id = ? AND topic_id = ?',
                    (display_order, section_id, topic_id)
                )
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error reordering sections: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ------ REORDER ITEMS ------ #
@admin_bp.route('/api/items/reorder', methods=['POST'])
@admin_required
def api_reorder_items():
    section_id = request.json.get('section_id')
    order_data = request.json.get('order', [])
    
    try:
        from app.models.database import DBConnection
        with DBConnection() as cursor:
            for display_order, item_id in enumerate(order_data):
                cursor.execute(
                    'UPDATE section_item SET display_order = ? WHERE id = ? AND section_id = ?',
                    (display_order, item_id, section_id)
                )
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error reordering items: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ------ CHANGE ITEM SECTION ------ #
@admin_bp.route('/api/items/change_section', methods=['POST'])
@admin_required
def api_change_item_section():
    try:
        from app.models.database import DBConnection
        with DBConnection() as cursor:
            item_id = request.json.get('item_id')
            section_id = request.json.get('section_id')
            
            cursor.execute(
                'UPDATE section_item SET section_id = ? WHERE id = ?',
                (section_id, item_id)
            )
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error changing item section: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ------------------------------------------- #
# ------------------ ITEMS ------------------ #
# ------------------------------------------- #
    
# -------- NEW ITEM -------- #
@admin_bp.route('/section/<int:section_id>/item/new', methods=['GET', 'POST'])
@admin_required
def new_item(section_id):
    section_model = SectionModel()
    section = section_model.get_by_id(section_id)
    
    if not section:
        flash('Section not found', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        markdown_content = request.form.get('markdown_content', '')
        card_size = request.form.get('card_size', 'normal')
        bookmark_color = request.form.get('bookmark_color', '#3b82f6')  # ADD THIS
        
        if not title:
            flash('Title is required', 'error')
            return render_template('admin/edit_item.html', section=section)
        
        item_model = SectionItemModel()
        item_id = item_model.create_item(
            title=title,
            section_id=section_id,
            markdown_content=markdown_content,
            card_size=card_size,
            bookmark_color=bookmark_color  # ADD THIS
        )
        
        if item_id:
            flash('Item created successfully!', 'success')
            return redirect(url_for('admin.manage_sections', topic_id=section.topic_id))
        else:
            flash('Error creating item', 'error')
    
    return render_template('admin/edit_item.html', section=section)

# ------- EDIT ITEM ------- #
@admin_bp.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_item(item_id):
    item_model = SectionItemModel()
    section_model = SectionModel()
    
    item = item_model.get_by_id(item_id)
    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('admin.dashboard'))
    
    section = section_model.get_by_id(item.section_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        markdown_content = request.form.get('markdown_content', '')
        card_size = request.form.get('card_size', 'normal')
        bookmark_color = request.form.get('bookmark_color', '#3b82f6')  # ADD THIS
        
        if not title:
            flash('Title is required', 'error')
            return render_template('admin/edit_item.html', section=section, item=item)
        
        if item_model.update_item(item_id, title, markdown_content, item.display_order, card_size, bookmark_color):  # UPDATE
            flash('Item updated successfully!', 'success')
            return redirect(url_for('admin.manage_sections', topic_id=section.topic_id))
        else:
            flash('Error updating item', 'error')
    
    return render_template('admin/edit_item.html', section=section, item=item)

# -------- DELETE ITEM  -------- #
@admin_bp.route('/item/<int:item_id>/delete')
@admin_required
def delete_item(item_id):
    item_model = SectionItemModel()
    section_model = SectionModel()
    
    item = item_model.get_by_id(item_id)
    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('admin.dashboard'))
    
    section = section_model.get_by_id(item.section_id)
    
    if item_model.delete_item(item_id):
        flash('Item deleted successfully!', 'success')
    else:
        flash('Error deleting item', 'error')
    
    return redirect(url_for('admin.manage_sections', topic_id=section.topic_id))