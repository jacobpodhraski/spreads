from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/spreadhistory'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

nfl2020 = db.Table('nfl2020', db.metadata, autoload = True, autoload_with=db.engine)

@app.route('/', methods = ['GET', 'POST'])
def query():

    if request.method == 'POST':

        team      = request.form['team']
        isFav     = request.form['isFav']
        isGreater = request.form['isGreater']
        points    = request.form['points']
        if points == "":
            points = str(0)
        beginYear = request.form['beginYear']
        endYear   = request.form['endYear']



        # Check if the years are valid
        if int(endYear) - int(beginYear) < 0:
            return render_template('new.html', errorMessage = "Years are invalid")


        yearByYear = OrderedDict()
        for year in range(int(beginYear), int(endYear) + 1):
            print("Queing year " + str(year))
            if team != 'any':
                yearByYear[year] = prepareQueryStatementForTeam(str(year), team, isFav, isGreater, points)
        return render_template('new.html', dictOfYears = yearByYear)

    else:

        return render_template('new.html', dictOfYears = OrderedDict())

def prepareQueryStatementForTeam(year, team, isFav, isGreater, points):

    statement = "select * from nfl" + year + " where team like '"+ team + "' and "

    if isFav == "Favourite":
        if isGreater == "more":
            # Set the spread requirement to under 30 (lowest o.u in history)
            statement = statement + 'close < 30 and close > ' + points + ';'
        else:
            statement = statement + 'close > 0 and close < ' + points + ';'

        print(statement)
        favGameIds = findAllGameIds(db.engine.execute(statement))
        favGames = getTableOfAllRelevantUnderdogGames(favGameIds, str(year), team)
        return favGames

    else:
        statement = statement + 'close >= 30'
        obtainAllUnderdogs = db.engine.execute(statement)
        underdogGameIds = findAllGameIds(obtainAllUnderdogs)
        print("ready to operate on " )
        print(underdogGameIds)
        relevantUnderdogGames = getTableOfAllRelevantUnderdogGames(underdogGameIds, str(year), team)
        if isGreater == "more":
            filteredUnderdogGameIds = filterUnderdogGameIds(relevantUnderdogGames, True, points)
        else:
            filteredUnderdogGameIds = filterUnderdogGameIds(relevantUnderdogGames, False, points)

        filteredUnderdogGames = getTableOfAllRelevantUnderdogGames(filteredUnderdogGameIds, str(year), team)
        return filteredUnderdogGames

def findAllGameIds(teamEntries):

    listOfGameIds = []
    for entry in teamEntries:
        listOfGameIds.append(entry.gameid)

    return listOfGameIds

def getTableOfAllRelevantUnderdogGames(gameIds, year, team):

    queryStatement = "select * from nfl" + year + " where "
    print(gameIds)
    if len(gameIds) == 0:
        return db.engine.execute("select * from nfl" + year + " where gameid = 0;")

    for i in range(0, len(gameIds)):
        if i == 0:
            queryStatement = queryStatement + "gameid = " + str(gameIds[i]) + " "
        else:
            queryStatement = queryStatement + "or gameid = " + str(gameIds[i]) + " "
    queryStatement = queryStatement + ";"
    return db.engine.execute(queryStatement)

def filterUnderdogGameIds(underdogGames, isGreater, points):

    listOfIds = []
    for game in underdogGames:
        if game.close > 30:
            continue
        else:
            if isGreater:
                if game.close > int(points):
                    listOfIds.append(game.gameid)
            else:
                if game.close < int(points):
                    listOfIds.append(game.gameid)
    return listOfIds



if __name__ == '__main__':
    app.run(debug = True)
