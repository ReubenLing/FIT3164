from sklearn.naive_bayes import GaussianNB
import csv
def naiveBayes(lstToPredict):
    """
    :param lstToPredict: A list of booleans of length 20
    :return: list containing
    """
    def extractY(lst):
        """
        :param lst: data as list of lists, with Y values in first column
        :return: All of the Y values as a list
        """
        return [item[0] for item in lst]

    def extractX(lst):
        """
        :param lst: data as list of lists, with Y values in first column
        :return: list of lists containing X values as boolean, excluding water loss values
        """
        return [list(map(bool,[int(i) for i in item[1:20]])) for item in lst]

    # read training csv
    with open('Irrigation_table - binary nb.csv', newline='', encoding='utf-8') as csvfile:
        irrData = list(csv.reader(csvfile))

    # read test csv
    with open('nb_test.csv', newline='', encoding='utf-8') as csvfile:
        irrTest = list(csv.reader(csvfile))

    # extract X and Y values of training and testing data
    irrDataY = extractY(irrData)
    irrDataX = extractX(irrData)
    # print(irrDataX, irrDataY)
    irrTestY = extractY(irrTest)
    irrTestX = extractX(irrTest)

    # fit naive bayes
    gnb = GaussianNB()
    y_pred = gnb.fit(irrDataX, irrDataY).predict([lstToPredict])     # the prediction value
    return y_pred
    """
    # testing
    y_pred = gnb.fit(irrDataX, irrDataY).predict(irrTestX)

    print("Number of mislabeled points out of a total %d points : %d"
        % (len(irrTestX), (irrTestY != y_pred).sum()))
    """
