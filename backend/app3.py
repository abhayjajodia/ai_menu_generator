import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from deepseek_planner import DeepSeekPlanner
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, 'templates')
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')

app.template_folder = TEMPLATES_DIR
app.static_folder = STATIC_DIR

# API key verification
if not os.getenv('DEEPSEEK_API_KEY'):
    print("⚠️ WARNING: DEEPSEEK_API_KEY not found in environment variables!")
else:
    print("✅ DeepSeek API key loaded successfully")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/plan', methods=['POST'])
def plan_event():
    try:
        data = request.json
        print("Received form data:", data)
        
        # Validate required fields
        required_fields = ['event_type', 'cuisine', 'formality', 'guest_count', 'service_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        planner = DeepSeekPlanner()
        menu = planner.generate_menu(data)
        print("Generated menu:", json.dumps(menu, indent=2))
        
        grocery = None
        if data.get('service_type') == 'self':
            grocery = planner.generate_grocery_list(menu, data['guest_count'])
            print("Generated grocery list:", json.dumps(grocery, indent=2))
        
        return jsonify({
            "status": "success",
            "menu": menu,
            "grocery_list": grocery
        })
        
    except Exception as e:
        print("Error in plan_event:", str(e))
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)