# app.py

from flask import Flask, request, render_template
from recommender import get_recommendations_by_keyword

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    keyword = ""
    if request.method == 'POST':
        keyword = request.form['keyword']
        recommendations = get_recommendations_by_keyword(keyword)

    return render_template('index.html', keyword=keyword, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
