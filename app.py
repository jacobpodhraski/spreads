from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict

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

        team      = request.form['team']
        isFav     = request.form['isFav']
        isGreater = request.form['isGreater']
        points    = request.form['points']
        beginYear = request.form['beginYear']
        endYear   = request.form['endYear']

        # Check if the years are valid
        if int(endYear) - int(beginYear) < 0:
            return render_template('new.html', errorMessage = "Years are invalid")


        yearByYear = OrderedDict()
        for year in range(int(beginYear), int(endYear) + 1):
            if team != 'any':
                queryStatement = prepareQueryStatementForTeam(str(year), team, isFav, isGreater, points)



        teamEntries = findAllGamesForTeam(team, isFav, isGreater, points)

        gameIds = findAllGameIds(teamEntries)
        print(gameIds)

        #currentGamesTable = getTableOfAllRelevantGames(gameIds)

        #dictOfGameScores = prepareGameLinesDict(currentGamesTable)

       # [suRecord, atsRecord] = obtainRecords(dictOfGameScores)

        return render_template('new.html')

       # return render_template('new.html', games = getTableOfAllRelevantGames(gameIds))


    else:

        return render_template('new.html')

def prepareQueryStatementForTeam(year, team, isFav, isGreater, points):

    statement = "select * from nfl" + year + " where team like '"+ team + "' and "

    if isFav:
        if isGreater:
            # Set the spread requirement to under 30 (lowest o.u in history)
            statement.append('close < 30 and close > ' + points + ';'
        else:
            statement.append('close > 0 and close < ' + points + ';'

        favGameIds = findAllGameIds(db.engine.execute(statement))

    else:
        statement.append('close >= 30')
        obtainAllUnderdogs = db.execute(statement)
        underdogGameIds = findAllGameIds(obtainAllUnderdogs)
        relevantUnderdogGames =


        if isGreater:

        else:


def findAllGamesForTeam(team, isFav, isGreater, points):

    queryStatement = 'select * from nfl2020'
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

def getTableOfAllRelevantGames(gameIds, year, team):

    queryStatement = "select * from nfl" + year + " where "
    for i in range(0, len(gameIds)):
        if i == 0:
            queryStatement.append("gameid = " + str(gameIds[i] + " ")
        else:
            queryStatement.append("or gameid = " + str(gameIds[i]) + " ")
    queryStatement.append(";")
    return db.engine.execute(queryStatement)

if __name__ == '__main__':
    app.run(debug = True)
