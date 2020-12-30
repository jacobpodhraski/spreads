from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict

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

    print("Test")
    if request.method == 'POST':
        team = request.form['team']
        isFav = request.form['isFav']
        isGreater = request.form['isGreater']
        points = request.form['points']

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

def getTableOfAllRelevantGames(gameIds, team, isFav, isGreater, points):

    queryStatement = "select * from nfl2020a where "



    for i in range(0, len(gameIds)):

        currentGame =  db.engine.execute("select * from nfl2020a where gameid = " + str(gameIds[i]))

        gameDictForComparsion = OrderedDict()

        for row in currentGame:
            continue


    return db.engine.execute(queryStatement)

def prepareGameLinesDict(currentGames):

    currentGameId = 0
    previousGameId = 0
    gameScores = OrderedDict()

    for row in currentGames:

        currentGameId = row.gameid

        if previousGameId == currentGameId:
            homeScore = row.final
            previousGameId = currentGameId

            openHome = row.open
            closeHome = row.close
            gameScores[row.gameid] = [vistorScore, homeScore, openVis, openHome, closeVis, closeHome]

        else:
            vistorScore = row.final
            openVis = row.open
            closeVis = row.close
            previousGameId = currentGameId

    print(gameScores)
    return gameScores

def obtainRecords(scoresDict):

    return [1, 2]
if __name__ == '__main__':
    app.run(debug = True)
