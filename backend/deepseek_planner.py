import requests
import json
import os
from typing import Dict, List

class DeepSeekPlanner:
    def call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek's free API"""
        headers = {"Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY', '')}"}
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            return "DeepSeek API error"
        except Exception as e:
            return f"DeepSeek service error: {str(e)}"

    def generate_menu(self, event_details: Dict) -> Dict:
        prompt = f"""
        Suggest a complete menu for a {event_details['event_type']} event with:
        - Cuisine: {event_details['cuisine']}
        - Formality: {event_details['formality']}
        - Guests: {event_details['guest_count']}
        - Dietary needs: {event_details['dietary_restrictions']}
        - Preparation: {'catering' if event_details['service_type'] == 'catering' else 'self-prepared'}
        
        Provide response as JSON with:
        {{
            "menu_description": "brief overview",
            "courses": [
                {{
                    "name": "course name",
                    "dishes": [
                        {{
                            "name": "dish name",
                            "description": "brief description"
                        }}
                    ]
                }}
            ]
        }}
        Only respond with valid JSON, no additional text.
        """
        
        response = self.call_deepseek(prompt)
        
        # Try to extract JSON from response
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            return json.loads(response[start:end])
        except:
            # Fallback menu
            return {
                "menu_description": "AI-generated menu",
                "courses": [{
                    "name": "Main Course",
                    "dishes": [{
                        "name": "Pasta Dish", 
                        "description": "Delicious pasta with seasonal vegetables"
                    }]
                }]
            }

    def generate_grocery_list(self, menu: Dict, guest_count: int) -> Dict:
        dishes = [dish['name'] for course in menu['courses'] for dish in course['dishes']]
        dishes_str = ", ".join(dishes)
        
        prompt = f"""
        Create a detailed grocery list for these dishes: {dishes_str}
        for {guest_count} guests. Format as JSON with:
        {{
            "ingredients": [
                {{
                    "name": "ingredient name",
                    "quantity": "quantity needed",
                    "category": "category (produce, dairy, etc.)"
                }}
            ],
            "prep_tips": ["list", "of", "tips"]
        }}
        Only respond with valid JSON, no additional text.
        """
        
        response = self.call_deepseek(prompt)
        
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            return json.loads(response[start:end])
        except:
            # Fallback grocery list
            return {
                "ingredients": [{
                    "name": "Pasta", 
                    "quantity": "1 kg", 
                    "category": "pantry"
                }],
                "prep_tips": ["Start cooking 2 hours before the event"]
            }