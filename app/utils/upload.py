import os
import uuid
from flask import current_app
from PIL import Image, ImageFile
import filetype

ImageFile.LOAD_TRUNCATED_IMAGES = True

def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    kind = filetype.guess(header)
    if kind and kind.mime.startswith("image/"):
        return kind.extension
    return None

def save_topic_logo(file, upload_folder=None):
    if upload_folder is None:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')

    os.makedirs(upload_folder, exist_ok=True)

    if not file or file.filename == '':
        return None

    if not allowed_file(file.filename):
        return None

    try:
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{file_ext}"
        filepath = os.path.join(upload_folder, filename)

        if file_ext == 'svg':
            file.save(filepath)
            return filename

        actual_format = validate_image(file.stream)
        if actual_format not in ['jpeg', 'png', 'gif', 'webp']:
            current_app.logger.warning(f"Invalid image format detected: {actual_format}")
            return None

        file.stream.seek(0)
        img = Image.open(file.stream)

        img.verify()
        file.stream.seek(0)
        img = Image.open(file.stream)

        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')

        img.thumbnail((64, 64), Image.Resampling.LANCZOS)

        if img.mode == 'RGBA':
            img.save(filepath, 'PNG', optimize=True)
        else:
            img.save(filepath, 'JPEG', optimize=True, quality=85)

        return filename

    except Exception as e:
        current_app.logger.error(f"Error processing image: {e}")
        return None

def delete_topic_logo(filename, upload_folder=None):
    if upload_folder is None:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')

    if not filename:
        return False

    filepath = os.path.join(upload_folder, filename)

    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        current_app.logger.error(f"Error deleting logo: {e}")

    return False