from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/spreadhistory'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

nfl2020 = db.Table('nfl2020a', db.metadata, autoload = True, autoload_with=db.engine)

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

        teamEntries = findAllGamesForTeam(team, isFav, isGreater, points)

        gameIds = findAllGameIds(teamEntries)
        print(gameIds)

        currentGamesTable = getTableOfAllRelevantGames(gameIds)

        return render_template('new.html', games = currentGamesTable )


def findAllGamesForTeam(team, isFav, isGreater, points):

    queryStatement = 'select * from nfl2020a'
    if team != 'any':
        queryStatement = queryStatement + " where team like '" + team + "';"
    else:
        queryStatement = queryStatement + ';'

    print(queryStatement)

    return db.engine.execute(queryStatement)

def findAllGameIds(teamEntries):

    listOfGameIds = []
    for entry in teamEntries:
        listOfGameIds.append(entry.gameid)

    return listOfGameIds

def getTableOfAllRelevantGames(gameIds):

    queryStatement = "select * from nfl2020a where "

    for i in range(0, len(gameIds)):

        if i == 0:
            queryStatement = queryStatement + 'gameid = ' + str(gameIds[i])
        else:
            queryStatement = queryStatement + ' or gameid = ' + str(gameIds[i])


    return db.engine.execute(queryStatement)


if __name__ == '__main__':
    app.run(debug = True)
