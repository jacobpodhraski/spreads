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

    data = pd.read_csv('datasets/nfl odds 2020-21.csv', header=None)
    print (data)
    numRows = data.shape[0]
    print('Num Rows: ' + str(numRows))
    idsCol = createListOfGameIds(numRows)
    print('len ids: ' + str(len(idsCol)))

    data['Game ID'] = idsCol

    print(data)

    data.to_csv('datasets/nfl odds 2020-21 idx.csv', header=None, index=False)




