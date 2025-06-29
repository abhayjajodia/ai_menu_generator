# import requests
# import json
# import os
# from typing import Dict, List

# class DeepSeekPlanner:
#     def call_deepseek(self, prompt: str) -> str:
#         """Call DeepSeek's API with proper error handling"""
#         api_key = os.getenv('DEEPSEEK_API_KEY')
#         if not api_key:
#             return "DeepSeek API key not configured in environment variables"
        
#         headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json"
#         }
        
#         payload = {
#             "model": "deepseek-chat",
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0.7,
#             "max_tokens": 2000,
#             "top_p": 0.9
#         }
        
#         try:
#             response = requests.post(
#                 "https://api.deepseek.com/chat/completions",
#                 headers=headers,
#                 json=payload,
#                 timeout=60
#             )
            
#             if response.status_code != 200:
#                 return f"DeepSeek API error: {response.status_code} - {response.text}"
            
#             result = response.json()
#             return result['choices'][0]['message']['content']
#         except Exception as e:
#             return f"DeepSeek service error: {str(e)}"

#     def generate_menu(self, event_details: Dict) -> Dict:
        
#         prompt = f"""
#         [IMPORTANT: Respond only with valid JSON, no additional text]
#         As an expert chef and event planner, create a diverse menu for a {event_details['event_type']} event with:
#         - Cuisine: {event_details['cuisine']}
#         - Formality: {event_details['formality']}
#         - Guests: {event_details['guest_count']}
#         - Dietary restrictions: {event_details['dietary_restrictions']}
#         - Preparation style: {'catering' if event_details['service_type'] == 'catering' else 'home-cooked'}
        
#         Include 3-5 courses with 2-3 dishes per course. Ensure dishes are:
#         - Culturally authentic to the cuisine
#         - Appropriate for the formality level
#         - Accommodate dietary restrictions
#         - Include both vegetarian and non-vegetarian options
        
#         Response format (JSON only):
#         {{
#             "menu_description": "brief overview",
#             "courses": [
#                 {{
#                     "name": "course name",
#                     "dishes": [
#                         {{
#                             "name": "unique dish name",
#                             "description": "brief description",
#                             "type": "vegetarian/non-vegetarian/vegan"
#                         }}
#                     ]
#                 }}
#             ]
#         }}
#         """
        
#         response = self.call_deepseek(prompt)

#     def generate_grocery_list(self, menu: Dict, guest_count: int) -> Dict:
#         dishes = [dish['name'] for course in menu['courses'] for dish in course['dishes']]
#         dishes_str = ", ".join(dishes)
        
#         prompt = f"""
#         Create a detailed grocery list for these dishes: {dishes_str}
#         for {guest_count} guests. Format as JSON with:
#         {{
#             "ingredients": [
#                 {{
#                     "name": "ingredient name",
#                     "quantity": "quantity needed",
#                     "category": "category (produce, dairy, etc.)"
#                 }}
#             ],
#             "prep_tips": ["list", "of", "tips"]
#         }}
#         Only respond with valid JSON, no additional text.
#         """
        
#         response = self.call_deepseek(prompt)
        
#         try:
#             start = response.find('{')
#             end = response.rfind('}') + 1
#             return json.loads(response[start:end])
#         except:
#             # Fallback grocery list
#             return {
#                 "ingredients": [{
#                     "name": "Pasta", 
#                     "quantity": "1 kg", 
#                     "category": "pantry"
#                 }],
#                 "prep_tips": ["Start cooking 2 hours before the event"]
#             }