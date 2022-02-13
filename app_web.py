import time

from flask import Flask, render_template, request, flash, redirect, url_for

from middle_control import middle

app = Flask(__name__)
# from main import app as application

var = Flask(__name__)
# from main import var as application

my_flask = Flask(__name__)
# from main import my_flask as application


@app.route('/', methods=('GET', 'POST'))
def start():
    return render_template('index.html')


@app.route('/getRecommendations')
def getRecommendations():
    title: str = request.args.get('title')
    artist: str = request.args.get('artist')
    limit: int = request.args.get('limit')

    startTime = time.time()
    recommendations = middle(str(artist), str(title), int(limit))
    endTime = time.time()

    return render_template('recommendations.html', rec=recommendations, time=(endTime - startTime))


@app.route('/search', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        title = request.form['titleMusic']
        artist = request.form['artistMusic']
        limit = request.form['limit_select']

        if not title:
            flash('Music name\'s required')
        else:
            return redirect(url_for('getRecommendations', title=title, artist=artist, limit=limit))
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
