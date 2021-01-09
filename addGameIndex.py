import pandas as pd

def createListOfGameIds(numRows):

    row = 1
    gameId = 1
    listOfGameIds = [];
    while (row <= numRows):
        listOfGameIds.append(gameId)
        listOfGameIds.append(gameId)
        row += 2
        gameId += 1

    return listOfGameIds


if __name__ == '__main__':

    years = ["2020-21"]

    for i in range(0,len(years)):

        data = pd.read_csv('datasets/nfl odds ' + years[i] + '.csv')
        print (data)
        numRows = data.shape[0]
        print('Num Rows: ' + str(numRows))
        idsCol = createListOfGameIds(numRows)
        print('len ids: ' + str(len(idsCol)))

        data['Game ID'] = idsCol

        print(data)

        data.to_csv('datasets/nfl odds ' + years[i] + 'idxUpdated.csv', header=None, index=False)




