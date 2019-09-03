import os
import re
import pandas as pd
from glob import glob
import logging

##########################################################################
##########################################################################
##                                                                      ##
##   Author:      Martin Holecek                                        ##
##                                                                      ##
##   Description: This code transpile all combinations of the product   ##
##                options from MD files into the CSV file               ##
##                                                                      ##
##########################################################################
##########################################################################


logging.basicConfig(filename='app.log', filemode='w',
                    format='%(message)s')


def getTemplateOption(optionName, sku):
    ''' Read template option from the md file and return it as a string '''
    filename = "templateOptions\\" + optionName + ".md"
    try:
        with open(filename, "r") as target:
            templateOptionContent = target.read()
            content = re.search(
                '---(.+?)---', templateOptionContent, re.DOTALL).group(1)
            return content
    except OSError as identifier:
        error = sku + " " + filename
        logging.warning(error)
        print(identifier)
        return ""


def printCombination(options):
    ''' Create all posible combinations of the product options '''
    totalNumberOfCombinations = 0
    allCombinations = []

    # number of arrays
    n = len(options)

    # to keep track of next element
    # in each of the n arrays
    indices = [0 for i in range(n)]

    while (1):

        totalNumberOfCombinations = totalNumberOfCombinations + 1

        # store current combination into the dictionary (key -> optionName, value -> name of single option)
        combination = {}
        for i in range(n):
            # print("## " + arr[i][indices[i]][0] + " ##", end=" ")
            # print("\n## " + arr[i][indices[i]][1] + " ##", end=" ")
            combination[options[i][indices[i]][0]] = options[i][indices[i]][1]

        allCombinations.append(combination)
        # print()

        # find the rightmost array that has more
        # elements left after the current element
        # in that array
        next = n - 1
        while (next >= 0 and
               (indices[next] + 1 >= len(options[next]))):
            next -= 1

        # no such array is found so no more
        # combinations left
        if (next < 0):
            print("Total: ", totalNumberOfCombinations)
            return allCombinations

        # if found move to next element in that
        # array
        indices[next] += 1

        # for all arrays to the right of this
        # array current index again points to
        # first element
        for i in range(next + 1, n):
            indices[i] = 0


def processSingleFile(filename, df_in):
    ''' 
        Get relevant content from the MD file (sku, options and generic options) 
        and create a Pandas Dataframe from this content
    '''
    with open(filename, "r") as f:
        fileContent = f.read()

        #### Get only variables within dashed content ####
        content = re.search(r'---(.+?)---', fileContent, re.DOTALL).group(1)

        #### Get Sku ####
        sku = re.findall(r"sku:\s+\"(.*)\"", content)[0]
        print(sku)

        #### Generic Options ####
        genericOptionsArray = re.findall(
            r"genericOptions: \[(.*?)\]", content, re.DOTALL)
        if genericOptionsArray:
            genericOptions = re.findall(
                r"\"(.*?)\"", genericOptionsArray[0])

            ### Append generic options to md file content ###
            for option in genericOptions:
                temp = getTemplateOption(option, sku)
                content += temp

        #### Options ####
        productOptions = re.findall(
            r"productOptions:\s*\[\s*{(.*?)]\s*}\s*]", content, re.DOTALL)
        allOptions = []
        for option in productOptions:
            optionName = re.findall(r"optionName\s*:\s*\"(.*?)\"", option)[0]
            names = re.findall(r"name:\s*\"(.*?)\"", option)
            # print(optionName)
            # print(names)

            if optionName == "Add Ground Anchor Bolts?" or optionName == "Add Heavy Duty Padlock?" or optionName == "Add Post Mix?":
                continue
            ### Create dictionary for each option where key is optionName and value is single option ###
            combinedNames = []
            for name in names:
                if name == "Powder Coated" or name == "RAL 3020" or name == "RAL 5010" or name == "RAL 6005" or name == "RAL 7037" or name == "RAL 8017" or name == "RAL 9005":
                    continue
                else:
                    combinedNames.append([optionName, name])
            if len(combinedNames) > 0:
                allOptions.append(combinedNames)

        #### Get all combinations and create Pandas Dataframe ####
        combinations = printCombination(allOptions)
        df = pd.DataFrame(combinations)
        df['sku'] = sku
        df_con = pd.concat([df_in, df], sort=True)
        return df_con


##### Get filenames of all products, extract options and store all combinations into the CSV file #####
md_files = glob('./products/**/index.md', recursive=True)
df = pd.DataFrame()
for md in md_files:
    df = processSingleFile(md, df)
df.to_csv('test2.csv', index=False)

# df = processSingleFile("/test-products/test/index.md", df) # Testing of single product
