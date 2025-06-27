echo "Starting DeepSeek Event Planner..."
echo "Please make sure you have a DeepSeek API key in backend/.env"

# Start backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run --port=5000 &

# Open in browser (Linux/Mac)
sleep 2
open "http://localhost:5000"

echo "Application running at http://localhost:5000"