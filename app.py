from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import os
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.secret_key = 'your-secret-key'  # Tambahkan secret key untuk flash messages

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        try:
            # Coba buka gambar untuk memastikan file valid
            img = Image.open(file)
            img.verify()  # Verifikasi file gambar
            
            # Reset pointer file
            file.seek(0)
            
            # Simpan file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            return render_template('index.html', 
                                original_filename=file.filename,
                                processed_filename=None)
        except Exception as e:
            flash('File yang diupload bukan gambar yang valid', 'error')
            return redirect(url_for('index'))
    else:
        flash('Format file tidak didukung. Gunakan format: ' + ', '.join(ALLOWED_EXTENSIONS), 'error')
        return redirect(url_for('index'))

@app.route('/process_image', methods=['POST'])
def process_image():
    filename = request.form['filename']
    operation = request.form['operation']
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = Image.open(filepath)
    
    if operation == 'contrast':
        img = adjust_contrast(img)
    elif operation == 'noise':
        img = reduce_noise(img)
    elif operation == 'sharpen':
        img = sharpen_image(img)
    
    processed_filename = f'processed_{operation}_{filename}'
    processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
    img.save(processed_filepath)
    
    return jsonify({'processed_filename': processed_filename})

def adjust_contrast(img):
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(1.5)

def reduce_noise(img):
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    img_cv = cv2.GaussianBlur(img_cv, (5, 5), 0)
    
    return Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

def sharpen_image(img):
    return img.filter(ImageFilter.SHARPEN)

if __name__ == '__main__':
    app.run(debug=True)
