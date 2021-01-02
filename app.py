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
        records = []
        totalWinsAts = 0
        totalLossesAts = 0
        totalTiesAts = 0
        totalWins = 0
        totalLosses = 0
        totalTies = 0

        for year in range(int(beginYear), int(endYear) + 1):
            print("Queing year " + str(year))
            if team != 'any':
                yearByYear[year], record = prepareQueryStatementForTeam(str(year), team, isFav, isGreater, points)

                totalWinsAts = totalWinsAts + record[0]
                totalLossesAts = totalLossesAts + record[1]
                totalTiesAts = totalTiesAts + record[2]
                totalWins = totalWins + record[3]
                totalLosses = totalLosses + record[4]
                totalTies = totalTies + record[5]
                records.append(record)
                print(records)

        totalRecord = [totalWinsAts, totalLossesAts, totalTiesAts, totalWins, totalLosses, totalTies]
        return render_template('new.html', dictOfYears = yearByYear, records = records, totalRecord = totalRecord, beginYear = beginYear, endYear = endYear)

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
        records = obtainRecords(favGameIds, team, year)
        favGames = getTableOfAllRelevantUnderdogGames(favGameIds, str(year), team)
        return favGames, records

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

        records = obtainRecords(filteredUnderdogGameIds, team, year)
        filteredUnderdogGames = getTableOfAllRelevantUnderdogGames(filteredUnderdogGameIds, str(year), team)
        return filteredUnderdogGames, records

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

def obtainRecords(gameIds, team, year):

    losses = 0
    wins = 0
    ties = 0

    lossesAts = 0
    winsAts = 0
    tiesAts = 0

    print("Game ids for record")
    print(gameIds)
    for i in range(0, len(gameIds)):
        print(gameIds[i])
        statement = "select * from nfl" + year + " where gameid = " + str(gameIds[i]) + ";"
        print(statement)
        currGame = db.engine.execute(statement)
        for game in currGame:
            print(game.team)
            print(game.close)
            print(game.final)
            if game.team == team:
                teamScore = game.final
                if game.close < 30:
                    isFav = True
                    spread = game.close
            else:
                otherScore = game.final
                if game.close < 30:
                    isFav = False
                    spread = game.close

        if teamScore - otherScore > 0:
            wins = wins + 1
        elif teamScore - otherScore == 0:
            ties = ties + 1
        else:
            losses = losses + 1

        if isFav:
            if teamScore - otherScore > spread:
                winsAts = winsAts + 1
            elif teamScore - otherScore == 0:
                tiesAts = tiesAts + 1
            else:
                lossesAts = lossesAts + 1

        else:
            if (teamScore + spread) - otherScore > 0:
                winsAts = winsAts + 1
            elif (teamScore + spread) - otherScore == 0:
                tiesAts = tiesAts + 1
            else:
                lossesAts = lossesAts + 1

    records = [winsAts, lossesAts, tiesAts, wins, losses, ties]
    return records


if __name__ == '__main__':
    app.run(debug = True)
