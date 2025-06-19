from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
import base64
from cartoonizer import cartoonify
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "Flask backend is running ✅"

def decode_image(data):
    image_bytes = base64.b64decode(data)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(image)

def encode_image(img_array):
    _, buffer = cv2.imencode('.png', cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/cartoonify', methods=['POST'])
def cartoonify_endpoint():
    print("✅ Received cartoonify request")
    data = request.json
    image_data = data['image']
    params = data.get('params', {})
    line_size = int(params.get('line_size', 7))
    blur_value = int(params.get('blur_value', 7))
    k = int(params.get('k', 9))

    try:
        image = decode_image(image_data)
        print("🖼️ Decoded image:", image.shape)

        cartoon = cartoonify(image, line_size, blur_value, k)
        print("🎨 Cartoon image created:", cartoon.shape)

        result = encode_image(cartoon)
        print("📦 Encoded base64 image length:", len(result))

        return jsonify({'cartoon': result})
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
