import os
from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import tensorflow as tf
import numpy as np

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
IMG_SIZE = [224, 224]

model = tf.keras.models.load_model('trained_face_mask.h5')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')

        # Load the model and perform the prediction
        file_save = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image = tf.keras.preprocessing.image.load_img(path=file_save,
                                             target_size=tuple(IMG_SIZE))

        input_arr = tf.keras.preprocessing.image.img_to_array(image)
        input_arr = np.array([input_arr])  # Convert single image to a batch.
        predictions = model.predict(input_arr)
        print(np.around(predictions))

        # Image Display and Prediction
        if np.around(predictions) == 1:
            print('###$$$ Without Mask')
        else:
            print("###$$$ With Mask")

        return render_template('upload.html', filename=filename)
    else:
        flash('Allowed image types are -> png, jpg, jpeg')
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run()
