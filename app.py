from flask import Flask, render_template, request, jsonify
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps
import io, base64, re

app = Flask(__name__)

MODEL_PATH = 'models/mnist_cnn.h5'
model = tf.keras.models.load_model(MODEL_PATH)

def preprocess_image_from_base64(b64data: str) -> np.ndarray:
    match = re.search(r"base64,(.*)", b64data)
    if not match:
        raise ValueError("Invalid image data")
    img_bytes = base64.b64decode(match.group(1))
    img = Image.open(io.BytesIO(img_bytes)).convert('L')

    # Invert warna: digit hitam -> putih seperti MNIST
    img = ImageOps.invert(img)

    # Ubah ke numpy array untuk cropping
    arr = np.array(img)
    coords = np.column_stack(np.where(arr > 0))
    if coords.size > 0:
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        arr = arr[y_min:y_max+1, x_min:x_max+1]
    else:
        arr = np.zeros((28,28), dtype=np.uint8)

    # Resize ke 20x20 sambil menjaga rasio
    img = Image.fromarray(arr)
    img.thumbnail((20, 20), Image.Resampling.LANCZOS)

    # Buat kanvas 28x28 dan tempelkan di tengah
    canvas = Image.new('L', (28, 28), color=0)
    paste_x = (28 - img.width) // 2
    paste_y = (28 - img.height) // 2
    canvas.paste(img, (paste_x, paste_y))

    arr = np.array(canvas).astype('float32') / 255.0
    arr = np.expand_dims(arr, axis=(0, -1))
    return arr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        img_data = data.get('image')
        x = preprocess_image_from_base64(img_data)
        probs = model.predict(x, verbose=0)[0]
        pred = int(np.argmax(probs))
        return jsonify({
            'prediction': pred,
            'probabilities': [float(p) for p in probs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)