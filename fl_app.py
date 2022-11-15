import flask 
from flask import Flask, Response, render_template, request, send_from_directory
import os
from PIL import Image
import time
import natsort
from pdf2image import convert_from_path
import pathlib
from datetime import datetime
imsx = 1990 # image size
imsz = 3835 # image size

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['IMAGE_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads/'
app.config['IMAGE_PATH'] = 'images/'
app.config['ARCHIVE'] = 'archive/'

def gen():# image updating
    i = 0

    while True:
        try:
            
            images = natsort.natsorted(get_all_images())
            image_name = images[i]
            im = open(app.config['IMAGE_PATH'] + image_name, 'rb').read()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + im + b'\r\n')
            i += 1
            if i >= len(images):
                i = 0
            time.sleep(10)
        except:
            return
@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/upload')
def upload():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('upload.html', files=files)

def get_all_images():# images
    images = [img for img in os.listdir(app.config['IMAGE_PATH'])
              if img.endswith(".jpg") or
              img.endswith(".jpeg") or
              img.endswith("png")]
    return images


@app.route('/pic1')
def slideshow():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/pics')
def safety_page():
    return render_template('pics.html')

@app.route('/upload1', methods=['POST'])
def upload_files():
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    if filename != '':
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        time.sleep(10)
        if filename.endswith(".pdf"):
            count1 = 0
            pages = convert_from_path(pdf_path=(app.config['UPLOAD_PATH']+filename), dpi = 400)
            for page in pages: # looping through PDF for pages in doc 
                        image_name = str(count1)+".png"
                        page.save(app.config['IMAGE_PATH']+image_name, "png")
                        image = Image.open(app.config['IMAGE_PATH']+image_name)
                        image.resize((imsz, imsx)).save(app.config['IMAGE_PATH']+image_name, "png")
                        count1 += 1 
            pathlib.Path(app.config['UPLOAD_PATH']+filename).rename(app.config['ARCHIVE']+dt_string+filename )
        
        elif filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
            pathlib.Path(app.config['UPLOAD_PATH']+filename).rename(app.config['IMAGE_PATH']+dt_string+filename)

        else:
            pathlib.Path(app.config['UPLOAD_PATH']+filename).rename(app.config['ARCHIVE']+dt_string+filename)

    return '', 204




@app.route('/uploads/<filename>')
def uploaded(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)