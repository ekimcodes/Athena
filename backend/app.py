from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
from services.scanner import generate_mock_hotspots
from services.inspector import get_random_image, analyze_image

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
TTPLA_DIR = os.path.join(DATA_DIR, 'TTPLA', 'data_original_size')

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "Athena Backend"})

# --- Phase 1: Macro Scanner ---

@app.route('/api/v1/hotspots', methods=['GET'])
def get_hotspots():
    """Returns mock hotspot data for the map."""
    # region = request.args.get('region', 'california')
    hotspots = generate_mock_hotspots()
    return jsonify(hotspots)

# --- Phase 2: Micro Inspector ---

@app.route('/api/v1/inspect/random', methods=['GET'])
def get_random_inspection_image():
    """Returns a random image ID from the TTPLA dataset."""
    image_info = get_random_image(TTPLA_DIR)
    return jsonify(image_info)

@app.route('/api/v1/inspect/analyze', methods=['POST'])
def analyze_inspection_image():
    """Simulates inference on an image."""
    data = request.json
    image_id = data.get('image_id')
    if not image_id:
        return jsonify({"error": "image_id is required"}), 400
        
    result = analyze_image(TTPLA_DIR, image_id)
    return jsonify(result)

@app.route('/data/images/<path:filename>')
def serve_image(filename):
    """Serves images from the TTPLA dataset."""
    return send_from_directory(TTPLA_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
