from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/spreadhistory'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

nfl2020 = db.Table('nfl2020', db.metadata, autoload = True, autoload_with=db.engine)

@app.route('/')
def showQueryResults():

    results = db.session.query(nfl2020).all()
    for r in results:
        team = r.team


   # return render_template('show_all.html', students = students.query.all() )
    return render_template('show_all.html', nfl2020 = db.session.query(nfl2020).all())


@app.route('/new', methods = ['GET', 'POST'])
def query():
    if request.method == 'POST':
        team = request.form['team']
        isFav = request.form['isFav']
        isGreater = request.form['isGreater']
        points = request.form['points']

        print (team + isFav + isGreater + points)

        r = db.engine.execute('select ' + 'team' + ', final from nfl2020')

        for entry in r:
            print (entry.team + ' - ' + str(entry.final))

    return render_template('new.html', team = team)

if __name__ == '__main__':
    app.run(debug = True)
