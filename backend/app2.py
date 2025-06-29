import os
import json
import random
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from openai import OpenAI

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

# Initialize OpenAI client only if token is available
try:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if GITHUB_TOKEN:
        client = OpenAI(
            base_url="https://api.githubcopilot.com/chat/completions",
            api_key=GITHUB_TOKEN
        )
        print("✅ GitHub Copilot API client initialized")
    else:
        client = None
        print("⚠️ GITHUB_TOKEN not found, using mock data only")
except:
    client = None
    print("⚠️ Failed to initialize GitHub Copilot API client, using mock data")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/plan', methods=['POST'])
def plan_event():
    try:
        data = request.json
        print("Received form data:", data)
        
        # Generate menu
        menu = generate_menu(data)
        print("Generated menu:", menu)
        
        # Generate grocery list if self-preparation
        grocery = None
        if data.get('service_type') == 'self':
            grocery = generate_grocery_list(menu, data['guest_count'])
            print("Generated grocery list:", grocery)
        
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

def generate_menu(event_details: dict) -> dict:
    """Generate menu with fallback to mock data"""
    # First try GitHub Copilot API if available
    if client:
        try:
            return generate_menu_with_api(event_details)
        except Exception as e:
            print("API menu generation failed, using mock data:", str(e))
    
    # Fallback to mock data
    return generate_mock_menu(event_details)

def generate_grocery_list(menu: dict, guest_count: int) -> dict:
    """Generate grocery list with fallback to mock data"""
    # First try GitHub Copilot API if available
    if client:
        try:
            return generate_grocery_list_with_api(menu, guest_count)
        except Exception as e:
            print("API grocery generation failed, using mock data:", str(e))
    
    # Fallback to mock data
    return generate_mock_grocery_list(menu, guest_count)

# API-based implementations
def generate_menu_with_api(event_details: dict) -> dict:
    """Generate menu using GitHub Copilot function calling"""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_menu",
                "description": "Generates a complete menu for an event based on event details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string"},
                        "cuisine": {"type": "string"},
                        "formality": {"type": "string"},
                        "guest_count": {"type": "integer"},
                        "dietary_restrictions": {"type": "string"},
                        "service_type": {"type": "string"}
                    },
                    "required": ["event_type", "cuisine", "formality", "guest_count", "service_type"]
                }
            }
        }
    ]
    
    prompt = f"""
    Create a diverse menu for:
    - Event type: {event_details['event_type']}
    - Cuisine: {event_details['cuisine']}
    - Formality: {event_details['formality']}
    - Guests: {event_details['guest_count']}
    - Dietary restrictions: {event_details['dietary_restrictions']}
    - Preparation: {'catering' if event_details['service_type'] == 'catering' else 'self-prepared'}
    
    Include 3 courses with 2-3 dishes per course. Ensure dishes are culturally authentic.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert chef and event planner."},
            {"role": "user", "content": prompt}
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "generate_menu"}}
    )
    
    # Process the function call
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name == "generate_menu":
            return json.loads(tool_call.function.arguments)
    
    raise Exception("API menu generation failed")

def generate_grocery_list_with_api(menu: dict, guest_count: int) -> dict:
    """Generate grocery list using GitHub Copilot function calling"""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_grocery_list",
                "description": "Generates a grocery list based on a menu and guest count",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "menu": {"type": "object"},
                        "guest_count": {"type": "integer"}
                    },
                    "required": ["menu", "guest_count"]
                }
            }
        }
    ]
    
    prompt = f"""
    Create a detailed grocery list for this menu for {guest_count} guests:
    {json.dumps(menu, indent=2)}
    
    For each ingredient include quantity based on guest count and categorize items.
    Also provide preparation tips.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert chef and event planner."},
            {"role": "user", "content": prompt}
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "generate_grocery_list"}}
    )
    
    # Process the function call
    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name == "generate_grocery_list":
            return json.loads(tool_call.function.arguments)
    
    raise Exception("API grocery generation failed")

# Mock data implementations
def generate_mock_menu(event_details: dict) -> dict:
    """Generate mock menu without API"""
    cuisine = event_details['cuisine'].lower()
    event_type = event_details['event_type']
    guests = event_details['guest_count']
    
    # Mock menu templates
    menus = {
        "italian": {
            "menu_description": f"Authentic Italian menu for your {event_type} ({guests} guests)",
            "courses": [
                {
                    "name": "Appetizers",
                    "dishes": [
                        {"name": "Bruschetta", "description": "Toasted bread with tomatoes, basil, and garlic", "dietary_info": "vegetarian"},
                        {"name": "Prosciutto e Melone", "description": "Cured ham with fresh melon", "dietary_info": "non-vegetarian"}
                    ]
                },
                {
                    "name": "Main Courses",
                    "dishes": [
                        {"name": "Spaghetti Carbonara", "description": "Pasta with eggs, cheese, and pancetta", "dietary_info": "non-vegetarian"},
                        {"name": "Eggplant Parmesan", "description": "Breaded eggplant with tomato sauce and cheese", "dietary_info": "vegetarian"},
                        {"name": "Grilled Sea Bass", "description": "Fresh fish with lemon and herbs", "dietary_info": "pescatarian"}
                    ]
                },
                {
                    "name": "Desserts",
                    "dishes": [
                        {"name": "Tiramisu", "description": "Coffee-flavored Italian dessert", "dietary_info": "vegetarian"},
                        {"name": "Panna Cotta", "description": "Creamy vanilla custard with berry coulis", "dietary_info": "vegetarian"}
                    ]
                }
            ]
        },
        "indian": {
            "menu_description": f"Traditional Indian feast for your {event_type} ({guests} guests)",
            "courses": [
                {
                    "name": "Appetizers",
                    "dishes": [
                        {"name": "Samosa", "description": "Spiced potato stuffed pastry", "dietary_info": "vegetarian"},
                        {"name": "Chicken Tikka", "description": "Grilled chicken marinated in spices", "dietary_info": "non-vegetarian"}
                    ]
                },
                {
                    "name": "Main Courses",
                    "dishes": [
                        {"name": "Butter Chicken", "description": "Creamy tomato-based chicken curry", "dietary_info": "non-vegetarian"},
                        {"name": "Palak Paneer", "description": "Spinach and cottage cheese curry", "dietary_info": "vegetarian"},
                        {"name": "Vegetable Biryani", "description": "Fragrant rice with mixed vegetables", "dietary_info": "vegan"}
                    ]
                },
                {
                    "name": "Desserts",
                    "dishes": [
                        {"name": "Gulab Jamun", "description": "Sweet milk balls in syrup", "dietary_info": "vegetarian"},
                        {"name": "Kheer", "description": "Rice pudding with nuts", "dietary_info": "vegetarian"}
                    ]
                }
            ]
        },
        "mexican": {
            "menu_description": f"Vibrant Mexican fiesta for your {event_type} ({guests} guests)",
            "courses": [
                {
                    "name": "Appetizers",
                    "dishes": [
                        {"name": "Guacamole & Chips", "description": "Fresh avocado dip with tortilla chips", "dietary_info": "vegetarian"},
                        {"name": "Beef Quesadillas", "description": "Grilled tortillas with seasoned beef", "dietary_info": "non-vegetarian"}
                    ]
                },
                {
                    "name": "Main Courses",
                    "dishes": [
                        {"name": "Chicken Enchiladas", "description": "Corn tortillas with chicken in chili sauce", "dietary_info": "non-vegetarian"},
                        {"name": "Vegetable Fajitas", "description": "Sizzling peppers and onions with tortillas", "dietary_info": "vegetarian"},
                        {"name": "Fish Tacos", "description": "Grilled fish in soft tortillas with slaw", "dietary_info": "pescatarian"}
                    ]
                },
                {
                    "name": "Desserts",
                    "dishes": [
                        {"name": "Churros", "description": "Fried dough pastries with chocolate", "dietary_info": "vegetarian"},
                        {"name": "Flan", "description": "Caramel custard dessert", "dietary_info": "vegetarian"}
                    ]
                }
            ]
        },
        "japanese": {
            "menu_description": f"Elegant Japanese menu for your {event_type} ({guests} guests)",
            "courses": [
                {
                    "name": "Appetizers",
                    "dishes": [
                        {"name": "Edamame", "description": "Steamed soybeans with sea salt", "dietary_info": "vegan"},
                        {"name": "Gyoza", "description": "Pan-fried dumplings with pork filling", "dietary_info": "non-vegetarian"}
                    ]
                },
                {
                    "name": "Main Courses",
                    "dishes": [
                        {"name": "Teriyaki Chicken", "description": "Grilled chicken with sweet soy glaze", "dietary_info": "non-vegetarian"},
                        {"name": "Vegetable Tempura", "description": "Lightly battered seasonal vegetables", "dietary_info": "vegetarian"},
                        {"name": "Sushi Platter", "description": "Assorted nigiri and maki rolls", "dietary_info": "pescatarian"}
                    ]
                },
                {
                    "name": "Desserts",
                    "dishes": [
                        {"name": "Mochi Ice Cream", "description": "Rice cake with ice cream filling", "dietary_info": "vegetarian"},
                        {"name": "Matcha Tiramisu", "description": "Green tea-flavored Italian dessert", "dietary_info": "vegetarian"}
                    ]
                }
            ]
        }
    }
    
    # Return a random cuisine if specific not found
    return menus.get(cuisine, random.choice(list(menus.values())))

def generate_mock_grocery_list(menu: dict, guest_count: int) -> dict:
    """Generate mock grocery list without API"""
    # Calculate quantities based on guest count
    meat_qty = guest_count * 150  # 150g per person
    veg_qty = guest_count * 200   # 200g per person
    rice_qty = guest_count * 100  # 100g per person
    
    # Mock grocery list
    return {
        "ingredients": [
            {"name": "Chicken/Meat", "quantity": f"{meat_qty}g", "category": "meat"},
            {"name": "Fresh Vegetables", "quantity": f"{veg_qty}g", "category": "produce"},
            {"name": "Rice/Grains", "quantity": f"{rice_qty}g", "category": "pantry"},
            {"name": "Spices & Herbs", "quantity": "Assorted", "category": "pantry"},
            {"name": "Dairy Products", "quantity": "As needed", "category": "dairy"},
            {"name": "Cooking Oil", "quantity": "1 bottle", "category": "pantry"}
        ],
        "prep_tips": [
            "Marinate proteins at least 2 hours before cooking",
            "Chop vegetables in advance to save time",
            "Prepare sauces ahead of time",
            "Set up cooking stations for efficient preparation",
            "Taste and adjust seasoning before serving"
        ]
    }

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)