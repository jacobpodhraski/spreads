from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fjcopgiwtupahu:ed271e50c35f2a9e80fd2db4c893256c37cf98926a0934dec1539db84aeee91a@ec2-18-232-232-96.compute-1.amazonaws.com:5432/d1nct8hqm1v5vc'

#app.config['SECRET_KEY'] = "random string"

#app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
        beginMonth = request.form['beginMonth']
        endMonth = request.form['endMonth']
        homeOrAway = request.form['vh']

        passBackFormHomeOrAway = homeOrAway
        if passBackFormHomeOrAway == "H":
            passBackFormHomeOrAway = "home"
            homeOrVisValue = "H"
        elif passBackFormHomeOrAway == "V":
            passBackFormHomeOrAway = "visitor"
            homeOrVisValue = "H"
        else:
            passBackFormHomeOrAway = "any"
            homeOrVisValue = "any"

        if isGreater == "more":
            passBackIsGreaterText = "By More than"
        else:
            passBackIsGreaterText = "By Less than"

        formInput = [team, beginYear, endYear, beginMonth, endMonth, passBackFormHomeOrAway, isFav, isGreater, int(points)]

        # Check if the years are valid
        if int(endYear) - int(beginYear) < 0:
            return render_template('new.html', dictOfYears = OrderedDict(), records = [], totalRecord = [], errorMessage = "Years are invalid")

        # Check if the months are valid
        if isMonthsValid(beginMonth, endMonth) == False:
            return render_template('new.html', dictOfYears = OrderedDict(), records = [], totalRecord = [], errorMessage = "Months are invalid")

        yearByYear = OrderedDict()
        records = []
        totalWinsAts = 0
        totalLossesAts = 0
        totalTiesAts = 0
        totalWins = 0
        totalLosses = 0
        totalTies = 0

        for year in range(int(beginYear), int(endYear) + 1):
            ##print("Queing year " + str(year))
            if team != 'any':
                yearByYear[year], record = prepareQueryStatementForTeam(str(year), beginMonth, endMonth, team, isFav, isGreater, points, homeOrAway)

                totalWinsAts = totalWinsAts + record[0]
                totalLossesAts = totalLossesAts + record[1]
                totalTiesAts = totalTiesAts + record[2]
                totalWins = totalWins + record[3]
                totalLosses = totalLosses + record[4]
                totalTies = totalTies + record[5]
                records.append(record)
                ##print(records)

        totalRecord = [totalWinsAts, totalLossesAts, totalTiesAts, totalWins, totalLosses, totalTies]
        return render_template('new.html', dictOfYears = yearByYear, records = records, totalRecord = totalRecord, beginYear = beginYear, endYear = endYear, formInput = formInput, homeOrVisValue = homeOrVisValue, passBackIsGreaterText = passBackIsGreaterText)

    else:

        return render_template('new.html', dictOfYears = OrderedDict(), records = [], totalRecord = [], formInput = [])

def prepareQueryStatementForTeam(year, beginMonth, endMonth, team, isFav, isGreater, points, homeOrAway):
    if team == "LAChargers":
        statement = "select * from nfl" + year + " where team like '"+ team + "' or team like 'SanDiego'"
        if int(year) < 2017:
            team = "SanDiego"
    elif team == "LARams":
        statement = "select * from nfl" + year + " where team like '"+ team + "' or team like 'St.Louis' or team like 'LosAngeles'"
        if int(year) < 2016:
            team = "St.Louis"
        elif int(year) == 2016:
            team = "LosAngeles"
    elif team == "LasVegas":
        statement = "select * from nfl" + year + " where team like '"+ team + "' or team like 'Oakland'"
        if int(year) < 2020:
            team = "Oakland"
    else:
        statement = "select * from nfl" + year + " where team like '"+ team + "'"


    #print("The TEAM IS " + str(team))
    #print("THE FAV IS: " + str(isFav))
    #print("THE YEAR IS: " + str(year))

    if isFav == "Favourite":
        if isGreater == "more":
            # Set the spread requirement to under 30 (lowest o.u in history)
            statement = statement + ' and close < 30 and close > ' + points + ';'
        else:
            statement = statement + ' and close > 0 and close < ' + points + ';'

        ##print(statement)
        favGameIds = findAllGameIds(db.engine.execute(statement), beginMonth, endMonth, homeOrAway)
        records = obtainRecords(favGameIds, team, year)
        favGames = getTableOfAllRelevantUnderdogGames(favGameIds, str(year), team)
        return favGames, records

    elif isFav == "Underdog":
        statement = statement + ' and close >= 30'
        obtainAllUnderdogs = db.engine.execute(statement)
        underdogGameIds = findAllGameIds(obtainAllUnderdogs, beginMonth, endMonth, homeOrAway)
        ##print("ready to operate on " )
        ##print(underdogGameIds)
        relevantUnderdogGames = getTableOfAllRelevantUnderdogGames(underdogGameIds, str(year), team)
        if isGreater == "more":
            filteredUnderdogGameIds = filterUnderdogGameIds(relevantUnderdogGames, True, points)
        else:
            filteredUnderdogGameIds = filterUnderdogGameIds(relevantUnderdogGames, False, points)

        records = obtainRecords(filteredUnderdogGameIds, team, year)
        filteredUnderdogGames = getTableOfAllRelevantUnderdogGames(filteredUnderdogGameIds, str(year), team)
        return filteredUnderdogGames, records

    else:
        #print("Made it here")
        statement = statement + ";"
        #print(statement)
        anyGameIds = findAllGameIds(db.engine.execute(statement), beginMonth, endMonth, homeOrAway)
        #print(anyGameIds)
        records = obtainRecords(anyGameIds, team, year)
        #print(anyGameIds)
        #print(records)
        #print(year)
        #print(team)
        anyGamesTable = getTableOfAllRelevantUnderdogGames(anyGameIds, str(year), team)
        return anyGamesTable, records

def findAllGameIds(teamEntries, beginMonth, endMonth, homeOrAway):
    listOfGameIds = []
    if beginMonth == "any":
        for entry in teamEntries:
            if homeOrAway == "any" or entry.vh == homeOrAway:
                #print("ENTERED")
                listOfGameIds.append(entry.gameid)
        return listOfGameIds
    else:
        monthKeys = whatAreTheRelevantMonths(beginMonth, endMonth)
        #print("Month Keys: ")
        #print(monthKeys)
        checkMonthId = []
        for entry in teamEntries:
            monthDayFromTable = str(entry.date)
            #print(monthDayFromTable)
            if len(monthDayFromTable) == 3:
                checkMonthId = int(monthDayFromTable[0])
            else:
                checkMonthId = int(monthDayFromTable[0] + monthDayFromTable[1])
            if checkMonthId in monthKeys:
                if homeOrAway == "any" or entry.vh == homeOrAway:
                    listOfGameIds.append(entry.gameid)

    #print(checkMonthId)
    #print("Made it here")

    #print(listOfGameIds)
    return listOfGameIds

def getTableOfAllRelevantUnderdogGames(gameIds, year, team):

    queryStatement = "select * from nfl" + year + " where "
    ##print(gameIds)
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

    ##print("Game ids for record")
    ##print(gameIds)
    for i in range(0, len(gameIds)):
        ##print(gameIds[i])
        statement = "select * from nfl" + year + " where gameid = " + str(gameIds[i]) + ";"
        ##print(statement)
        currGame = db.engine.execute(statement)
        for game in currGame:
            ##print(game.team)
            ##print(game.close)
            ##print(game.final)
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

def isMonthsValid(begin, end):

    if begin == "any":
        return True

    if end == "any":
        return False

    september = 1
    october   = 2
    november  = 3
    december  = 4
    january   = 5
    february  = 6

    if begin == "September":
        beginCheck = september
    elif begin == "October":
        beginCheck = october
    elif begin == "November":
        beginCheck = november
    elif begin == "December":
        beginCheck = december
    elif begin == "January":
        beginCheck = january
    elif begin == "February":
        beginCheck = february
    else:
        return False

    if end == "September":
        endCheck = september
    elif end == "October":
        endCheck = october
    elif end == "November":
        endCheck = november
    elif end == "December":
        endCheck = december
    elif end == "January":
        endCheck = january
    elif end == "February":
        endCheck = february
    else:
        return False


    if endCheck - beginCheck >= 0:
        return True
    else:
        return False


def whatAreTheRelevantMonths(begin, end):

    ##print("Begin Month: ")
    ##print(begin)
    ##print("End Month: ")
    ##print(end)

    monthsDict = OrderedDict()
    monthsDict["September"] = 9
    monthsDict["October"]   = 10
    monthsDict["November"]  = 11
    monthsDict["December"]  = 12
    monthsDict["January"]   = 1
    monthsDict["February"]  = 2

    relevantMonths = []
    hasBegun = False

    if begin == end:
        ##print("Made it here")
        ##print(monthsDict[begin])
        relevantMonths.append(monthsDict[begin])
        return relevantMonths

    for key in monthsDict:
        if key == begin:
            relevantMonths.append(monthsDict[key])
            hasBegun = True
        elif key == end:
            relevantMonths.append(monthsDict[key])
            return relevantMonths
        elif hasBegun:
            relevantMonths.append(monthsDict[key])




if __name__ == '__main__':
    app.run(debug = True)
