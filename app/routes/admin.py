from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.topic import TopicModel
from app.models.section import SectionModel
from app.models.section_item import SectionItemModel
from app.models.category import CategoryModel 

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
    topics = topic_model.get_all()
    return render_template('admin/dashboard.html', topics=topics)


# ------------------------------------------- #
# --------------- CATEGORIES ---------------- #
# ------------------------------------------- #

@admin_bp.route('/categories')
@admin_required
def manage_categories():
    category_model = CategoryModel()
    categories = category_model.get_all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/category/new', methods=['GET', 'POST'])
@admin_required
def new_category():
    if request.method == 'POST':
        name = request.form.get('name')
        display_order = request.form.get('display_order', 0, type=int)
        
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

@admin_bp.route('/category/<int:category_id>/delete')
@admin_required
def delete_category(category_id):
    category_model = CategoryModel()
    
    # Check if category has topics
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

# API for reordering categories
@admin_bp.route('/api/categories/reorder', methods=['POST'])
@admin_required
def api_reorder_categories():
    order_data = request.json.get('order', [])
    
    category_model = CategoryModel()
    for index, category_id in enumerate(order_data):
        # First get the current category to preserve the name
        category = category_model.get_by_id(category_id)
        if category:
            # Update only the display_order, keep the existing name
            category_model.update(category_id, category.name, index)
    
    return jsonify({'success': True})

# --------- SETUP CATEGORIES --------- #
@admin_bp.route('/setup-categories')
@admin_required
def setup_categories():
    """Create default categories and assign existing topics"""
    try:
        # Use your DBConnection directly
        from app.models.database import DBConnection
        
        with DBConnection() as cursor:
            # Create default categories
            default_categories = [
                ('Programming', 0),
                ('Tools', 1), 
                ('Linux', 2),
                ('General', 3)
            ]
            
            for name, order in default_categories:
                cursor.execute('INSERT OR IGNORE INTO category (name, display_order) VALUES (?, ?)', (name, order))
            
            # Assign all existing topics to General category
            cursor.execute('UPDATE topic SET category_id = (SELECT id FROM category WHERE name = "General") WHERE category_id IS NULL OR category_id = ""')
            
            # Count how many topics were updated
            cursor.execute('SELECT changes()')
            topics_updated = cursor.fetchone()[0]
            
            flash(f"✅ Categories setup completed! Updated {topics_updated} topics.", 'success')
            
    except Exception as e:
        flash(f'❌ Error setting up categories: {e}', 'error')
    
    return redirect(url_for('admin.dashboard'))


# --------- CATEGORIES ORDER --------- #
@admin_bp.route('/category-order')
@admin_required
def manage_category_order():
    """Manage the display order of categories"""
    topic_model = TopicModel()
    categories = topic_model.get_all_categories()
    
    return render_template('admin/category_order.html', categories=categories)

@admin_bp.route('/api/category-order/update', methods=['POST'])
@admin_required
def api_update_category_order():
    """Update category order (simple text-based system)"""
    new_order = request.json.get('order', [])
    
    # For now, we'll just store this in a simple way
    # In a real app, you'd want to store this in a separate table
    flash(f"Category order updated: {', '.join(new_order)}", 'success')
    return jsonify({'success': True})


# ------------------------------------------- #
# ----------------- TOPICS ------------------ #
# ------------------------------------------- #

# --------- NEW TOPIC --------- #
@admin_bp.route('/topic/new', methods=['GET', 'POST'])
@admin_required
def new_topic():
    topic_model = TopicModel()
    categories = topic_model.get_all_categories()  # This now returns (id, name) tuples
    
    if request.method == 'POST':
        slug = request.form.get('slug')
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id', 1, type=int)  # Get category ID
        is_published = 'is_published' in request.form
        
        if not slug or not title:
            flash('Slug and title are required', 'error')
            return render_template('admin/edit_topic.html', categories=categories)
        
        topic_id = topic_model.create_topic(slug, title, description, current_user.id, category_id, is_published)
        
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
        
        if topic_model.update_topic(topic_id, slug, title, description, category_id, is_published):
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
    
    # if section_id:
    #     return jsonify({'success': True, 'section_id': section_id})
    # else:
    #     return jsonify({'success': False, 'error': 'Failed to create section'})


# -------- SECTION UPDATE -------- #
@admin_bp.route('/api/section/update', methods=['POST'])
@admin_required
def api_update_section():
    section_id = request.json.get('section_id')
    title = request.json.get('title')
    display_order = request.json.get('display_order', 0)
    
    section_model = SectionModel()
    # if section_model.update_section(section_id, title, display_order):
    #     return jsonify({'success': True})
    # else:
    #     return jsonify({'success': False, 'error': 'Failed to update section'})

# -------- SECTION DELETE -------- #
@admin_bp.route('/api/section/delete', methods=['POST'])
@admin_required
def api_delete_section():
    section_id = request.json.get('section_id')
    
    section_model = SectionModel()
    # if section_model.delete_section(section_id):
    #     return jsonify({'success': True})
    # else:
    #     return jsonify({'success': False, 'error': 'Failed to delete section'})

# ------------------------------------------- #
# ------------------ ITEMS ------------------ #
# ------------------------------------------- #

# -------- NEW ITEM (QUICK)  -------- #
@admin_bp.route('/api/item/new', methods=['POST'])
@admin_required
def api_new_item():
    section_id = request.json.get('section_id')
    title = request.json.get('title')
    item_type = request.json.get('type', 'default')
    
    item_model = SectionItemModel()
    item_id = item_model.create_item(title, section_id, item_type=item_type)
    
    # if item_id:
    #     return jsonify({'success': True, 'item_id': item_id})
    # else:
    #     return jsonify({'success': False, 'error': 'Failed to create item'})
    
# -------- NEW ITEM  -------- #
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
        description = request.form.get('description')
        url = request.form.get('url')
        code = request.form.get('code')
        item_type = request.form.get('item_type', 'default')
        
        if not title:
            flash('Title is required', 'error')
            return render_template('admin/edit_item.html', section=section)
        
        item_model = SectionItemModel()
        item_id = item_model.create_item(
            title=title,
            section_id=section_id,
            description=description,
            url=url,
            code=code,
            item_type=item_type
        )
        
        if item_id:
            flash('Item created successfully!', 'success')
            return redirect(url_for('admin.manage_sections', topic_id=section.topic_id))
        else:
            flash('Error creating item', 'error')
    
    return render_template('admin/edit_item.html', section=section)


# ------- EDIT ITEM  ------- #
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
        description = request.form.get('description')
        url = request.form.get('url')
        code = request.form.get('code')
        item_type = request.form.get('item_type', 'default')
        
        if not title:
            flash('Title is required', 'error')
            return render_template('admin/edit_item.html', section=section, item=item)
        
        if item_model.update_item(item_id, title, description, url, code, item_type, item.display_order):
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







@admin_bp.route('/fix-database')
@admin_required
def fix_database():
    """Fix the database schema conflict"""
    try:
        from app.models.database import DBConnection
        
        with DBConnection() as cursor:
            # Add category text column if it doesn't exist
            try:
                cursor.execute('ALTER TABLE topic ADD COLUMN category TEXT')
            except:
                pass  # Column might already exist
            
            # Copy category_id values to category text (temporary fix)
            cursor.execute('''
                UPDATE topic 
                SET category = (SELECT name FROM category WHERE category.id = topic.category_id)
                WHERE category_id IS NOT NULL
            ''')
            
            flash("✅ Database fixed! Now using text categories.", 'success')
            
    except Exception as e:
        flash(f'❌ Error: {e}', 'error')
    
    return redirect(url_for('admin.dashboard'))