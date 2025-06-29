import os
import json
import re
import traceback
from flask import Flask, request, jsonify, render_template, send_from_directory
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

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

# Initialize OpenAI client
api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    print("⚠️ WARNING: DEEPSEEK_API_KEY not found in environment variables!")
else:
    print("✅ DeepSeek API key loaded successfully")

client = None
if api_key:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        # Test connection
        test_response = client.models.list()
        print("🔌 API Connection Test Successful")
    except Exception as e:
        print(f"🔴 API Connection Failed: {str(e)}")
        client = None

class MenuModel(BaseModel):
    appetizers: list[str]
    main_courses: list[str]
    desserts: list[str]
    beverages: list[str]
    preparation_notes: str

def log_error(message, error=None):
    """Log errors with traceback"""
    error_msg = f"🔴 ERROR: {message}"
    if error:
        error_msg += f"\n🔴 TRACEBACK: {traceback.format_exc()}"
    print(error_msg)
    return error_msg

def generate_with_deepseek(prompt, max_tokens=500):
    """Generate content with DeepSeek API"""
    if not client:
        return {"error": "API client not initialized"}
        
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            # model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            # max_tokens=max_tokens
        )
        print(response)
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return {"error": log_error("DeepSeek API call failed", e)}


def generate_menu_ai(prompt, max_tokens=500):
    """Generate content with DeepSeek API"""
    if not client:
        return {"error": "API client not initialized"}
        
    try:
        response = client.beta.chat.completions.parse(
            model="deepseek/deepseek-r1-0528:free",
            # model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format=MenuModel
        )
        print("Response::",response)
        
        return response.choices[0].message
        
    except Exception as e:
        return {"error": log_error("DeepSeek API call failed", e)}



def parse_menu_response(text):
    """Convert text response to structured menu"""
    menu = {
        "appetizers": [],
        "main_courses": [],
        "desserts": [],
        "beverages": [],
        "preparation_notes": ""
    }
    
    # Simple parsing logic
    sections = {
        "appetizers": r'appetizers?[:\s]*([\s\S]+?)(?=\n\s*main course|dessert|beverage|$)',
        "main_courses": r'main courses?[:\s]*([\s\S]+?)(?=\n\s*dessert|beverage|$)',
        "desserts": r'desserts?[:\s]*([\s\S]+?)(?=\n\s*beverage|$)',
        "beverages": r'beverages?[:\s]*([\s\S]+?)(?=\n|$)',
        "notes": r'notes?[:\s]*([\s\S]+)'
    }
    
    for key, pattern in sections.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            if key == "notes":
                menu["preparation_notes"] = content
            else:
                # Split into items
                items = [item.strip() for item in re.split(r'\n\s*[-*•]', content) if item.strip()]
                menu[key] = items
    
    return menu

def generate_menu(data):
    """Generate menu with simplified instructions"""
    try:
        prompt = f"""
        Create a menu for a {data['formality']} {data['event_type']} event with {data['guest_count']} guests.
        Cuisine style: {data['cuisine']}
        Service type: {data['service_type']}
        
        Provide the menu in this format:
        
        Appetizers:
        - Appetizer 1
        - Appetizer 2
        
        Main Courses:
        - Main Course 1
        - Main Course 2
        
        Desserts:
        - Dessert 1
        - Dessert 2
        
        Beverages:
        - Beverage 1
        - Beverage 2
        
        Notes: Preparation instructions or special notes
        """
        raw_response = generate_menu_ai(prompt)
        
        if isinstance(raw_response, dict) and "error" in raw_response:
            return raw_response
            
        print("🍽️ RAW MENU RESPONSE:\n", raw_response)
        # return raw_response
        return {
            "appetizers": raw_response.parsed.appetizers,
            "main_courses": raw_response.parsed.main_courses,
            "desserts": raw_response.parsed.desserts,
            "beverages": raw_response.parsed.beverages,
            "preparation_notes": raw_response.parsed.preparation_notes
        }
        
    except Exception as e:
        return {"error": log_error("Menu generation failed", e)}

def generate_grocery_list(menu, guest_count):
    """Generate simplified grocery list"""
    try:
        if not menu or not isinstance(menu, dict):
            return {"error": "Invalid menu input"}
            
        menu_text = "\n".join(
            [f"{section}:\n" + "\n".join(f"- {item}" for item in items)
            for section, items in menu.items() if items]
        )
            
        prompt = f"""
        Create a grocery shopping list for {guest_count} people based on this menu:
        {menu_text}
        
        Provide the list in this format:
        - Item 1 (quantity)
        - Item 2 (quantity)
        - Item 3 (quantity)
        """
        return generate_with_deepseek(prompt)
    except Exception as e:
        return {"error": log_error("Grocery list generation failed", e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/plan', methods=['POST'])
def plan_event():
    try:
        # Check if API is available
        if not client:
            return jsonify({
                "status": "error",
                "message": "API service unavailable. Please check backend logs."
            }), 503
            
        data = request.json
        print("📝 Received form data:", json.dumps(data, indent=2) if data else "No data")
        
        # Validate required fields
        required_fields = ['event_type', 'cuisine', 'formality', 'guest_count', 'service_type']
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data received"
            }), 400
            
        missing = [field for field in required_fields if field not in data or not data[field]]
        if missing:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing)}"
            }), 400
        
        # Generate menu
        menu = generate_menu(data)
        print("🍽️ STRUCTURED MENU:", json.dumps(menu, indent=2))
        
        # Check if menu generation failed
        if "error" in menu:
            return jsonify({
                "status": "error",
                "message": f"Menu generation failed: {menu['error']}"
            }), 500
            
        # Generate grocery list if self-service
        grocery = None
        if data.get('service_type') == 'self':
            grocery = generate_grocery_list(menu, data['guest_count'])
            print("🛒 GROCERY LIST:", grocery if grocery else "None")
            
            if isinstance(grocery, dict) and "error" in grocery:
                return jsonify({
                    "status": "error",
                    "message": f"Grocery list generation failed: {grocery['error']}"
                }), 500
        
        # Prepare success response
        response = {
            "status": "success",
            "message": "Here is your menu",
            "menu": menu,
        }
        
        if grocery:
            response["grocery_list"] = grocery
            
        return jsonify(response)
        
    except Exception as e:
        error_msg = log_error("Server error in plan_event", e)
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {error_msg}"
        }), 500

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)