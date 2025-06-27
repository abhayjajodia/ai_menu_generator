from flask import Flask, request, jsonify, render_template, send_from_directory
from deepseek_planner import DeepSeekPlanner
import os

app = Flask(__name__)

# Path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, 'templates')
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')

app.template_folder = TEMPLATES_DIR
app.static_folder = STATIC_DIR

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/plan', methods=['POST'])
def plan_event():
    data = request.json
    planner = DeepSeekPlanner()
    
    # Generate menu
    menu = planner.generate_menu(data)
    
    # Generate grocery list if self-preparation
    grocery = None
    if data.get('service_type') == 'self':
        grocery = planner.generate_grocery_list(menu, data['guest_count'])
    
    return jsonify({"status": "success"})

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)


if __name__ == '__main__':
    app.run(debug=True, port=5000)