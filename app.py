import requests
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = request.form['query']
        response = requests.get(f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key=8Y5cEUURtEY4GtGvO99qAf0F1mRLLGvWoO8MXX8S&query={query}")
        data = response.json()
        results = data.get('foods', [])
    return render_template('search.html', results=results)

@app.route('/planner')
def planner():
    planner = session.get('planner', {})

    totals = {}
    for day, items in planner.items():
        total_calories = round(sum(item['calories'] for item in items))
        total_sugars = round(sum(item['sugars'] for item in items))
        totals[day] = {
            'calories': total_calories,
            'sugars': total_sugars
        }

    return render_template('planner.html', planner=planner, totals=totals)

@app.route('/add_to_planner', methods=['POST'])
def add_to_planner():
    food_name = request.form['food_name']
    calories = float(request.form['calories'])
    sugars = float(request.form['sugars'])
    day = request.form['day']  

    if 'planner' not in session:
        session['planner'] = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}

    if day not in session['planner']:
        session['planner'][day] = []

    session['planner'][day].append({'name': food_name, 'calories': calories, 'sugars': sugars})
    session.modified = True

    return redirect('/planner')

@app.route('/delete_item', methods=['POST'])
def delete_item():
    day = request.form['day']
    item_name = request.form['item_name']

    if 'planner' in session and day in session['planner']:
        session['planner'][day] = [item for item in session['planner'][day] if item['name'] != item_name]

        session.modified = True

    return redirect('/planner')

@app.route('/reset_planner')
def reset_planner():
    session['planner'] = {day: [] for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}
    session.modified = True
    return redirect('/planner')

@app.route('/reset_session')
def reset_session():
    session.clear()
    return "Session has been cleared. You can now visit the planner page."

if __name__ == '__main__':
    app.run(debug=True)