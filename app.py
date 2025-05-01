from flask import Flask, render_template, request, redirect, url_for, jsonify
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import os
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        return render_template('index.html', 
                             original_filename=file.filename,
                             processed_filename=None)

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

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

if __name__ == '__main__':
    app.run(debug=True)
