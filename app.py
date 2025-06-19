from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
import base64
from cartoonizer import cartoonify
from PIL import Image
import io

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

def decode_image(data):
    image_bytes = base64.b64decode(data)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(image)

def encode_image(img_array):
    _, buffer = cv2.imencode('.png', cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/cartoonify', methods=['POST'])
def cartoonify_endpoint():
    data = request.json
    image_data = data['image']
    params = data.get('params', {})
    line_size = int(params.get('line_size', 7))
    blur_value = int(params.get('blur_value', 7))
    k = int(params.get('k', 9))

    image = decode_image(image_data)
    cartoon = cartoonify(image, line_size, blur_value, k)
    result = encode_image(cartoon)
    return jsonify({'cartoon': result})

if __name__ == '__main__':
    app.run(debug=True)
