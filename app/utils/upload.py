import os
from PIL import Image
from flask import current_app
import uuid

def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_topic_logo(file, upload_folder=None):
    if upload_folder is None:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')
    
    # Create upload directory if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{file_ext}"
        filepath = os.path.join(upload_folder, filename)
        
        try:
            # Handle different image types
            if file_ext != 'svg':
                # Open and process image
                img = Image.open(file.stream)
                
                # Resize image (max 64x64 pixels like quickref.me)
                img.thumbnail((64, 64), Image.Resampling.LANCZOS)
                
                # Save processed image
                img.save(filepath, optimize=True, quality=85)
            else:
                # For SVG, just save as-is
                file.save(filepath)
            
            return filename
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    return None

def delete_topic_logo(filename, upload_folder=None):
    if upload_folder is None:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')
    
    if filename:
        filepath = os.path.join(upload_folder, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting logo: {e}")
    
    return False