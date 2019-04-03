# -*- coding: utf-8 -*-
import re


# remove all characters that are not a letter, number, or space character
def remove_char(text):
    patt = re.compile('[^A-Za-z0-9 ]')
    return patt.sub('', text)


# distinguish title -> all upper cases
# re: [A-Z(other )]+
def findTitle(text_list):
    if text_list == '1. HOW THEY WENT TO THE MOUNTAINS TO EAT NUTS' or text_list == '2. HOW CHANTICLEER AND PARTLET WENT TO VISIT MR KORBES' or text_list == '3. HOW PARTLET DIED AND WAS BURIED, AND HOW CHANTICLEER DIED OF GRIEF':
        return False
    for text in text_list:
        if text.islower():
            return False
    return True


# outer dict{word:inner dict{}}
# inner dict{title: list[line_number]}
# use setdefault(key,default)
def bodyText(w2s, title, line, linenumber):
    for word in line:
        innerDict = w2s.get(word, {})
        innerList = innerDict.get(title, [])
        innerList.append(linenumber)
        innerDict[title] = innerList
        w2s[word] = innerDict


def buildIndex():
    stopwords_list = []
    tales_list = []  # i=linenumber-125
    w2s = {}
    titles = []

    grimms_file = open('grimms.txt', 'r', encoding='utf-8')
    stopwords_file = open('stopwords.txt', 'r')

    # build the list containing stopwords
    for line in stopwords_file:
        word = line.strip()
        stopwords_list.append(word)

    linenumber = 124
    for line in grimms_file.readlines()[124:9182]:
        tales_list.append(line.strip())
        linenumber += 1
        if(len(line) != 1):  # space line: len==1
            aline = line.strip()
            if findTitle(aline):
                titles.append(aline)
            if aline not in titles:
                aline = remove_char(aline)
                words_list = aline.split()
    # use set() to store unique values
                filtered_words = set([word.lower() for word in words_list if not word.lower() in stopwords_list])
                bodyText(w2s, titles[-1], filtered_words, linenumber)

    grimms_file.close()
    stopwords_file.close()
    return (stopwords_list, tales_list, w2s, titles)


# !isOr: find if the queries are all in the query list is in the w2s dictionary
# isOr: find if any of the query is not in the query list is in the w2s dictionary
def inW2S(w2s, queryList, isOr):
    if isOr:
        for oneQuery in queryList:
            if oneQuery in w2s:
                return True
        return False
    else:
        for oneQuery in queryList:
            if oneQuery not in w2s:
                return False
        return True


# print the smallest block:
#  542 an **OWL** ...
def printItem(tales_list, query, num, qLen):
    resString = tales_list[num - 125]
    newSub = '**' + query.upper() + '**'
    resString = resString.replace(query, newSub)
    resString = resString.replace(query.capitalize(), newSub)
    if qLen == 1:
        print('\t  ', num, resString)
    else:
        print('\t\t', num, resString)


# return frequency of certain word in each story
def countFrequency(tales_list, word, dict):
    freDict = {}
    for key in dict.keys():
        count = 0
        for num in dict[key]:
            resString = tales_list[num - 125].strip().lower()
            resString = remove_char(resString).split()
            for i in range(len(resString)):
                if resString[i] == word:
                    count = count + 1
        freDict[key] = count
    return freDict

def classifyOutput(isOr, isMore, isNear, w2s, talesCount, tales_list, queryList, frequency, numSet, numSet2):
    talesPrint = []
    freDict = dict()
    freDict2 = dict()
    if isOr:
        talesPrint = [tale for tale in talesCount]
    elif isMore:
        onlyQuery = queryList[0]
        if onlyQuery in w2s:
            freDict = countFrequency(tales_list, onlyQuery, w2s[onlyQuery])
            if frequency.isdigit():
                talesPrint = [tale for tale in freDict if freDict[tale] > int(frequency)]
            else:
                if frequency not in w2s:
                    talesPrint = [tale for tale in freDict if freDict[tale] > 0]
                else:
                    freDict2 = countFrequency(tales_list, frequency, w2s[frequency])
                    talesPrint = [tale for tale in freDict if (tale in freDict2 and freDict[tale] > freDict2[tale]) or tale not in freDict2]
    elif isNear:
        talesPre = [tale for tale in talesCount if talesCount[tale] == len(queryList)]
        for tale in talesPre:
            for num0 in w2s[queryList[0]][tale]:
                if (num0 + 1) in w2s[queryList[1]][tale]:
                    numSet.add(num0)
                    numSet2.add(num0+1)
                    talesPrint.append(tale)
                if (num0 - 1) in w2s[queryList[1]][tale]:
                    numSet.add(num0)
                    numSet2.add(num0-1)
                    talesPrint.append(tale)
                if (num0) in w2s[queryList[1]][tale]:
                    numSet.add(num0)
                    numSet2.add(num0)
                    talesPrint.append(tale)
    else:
        talesPrint = [tale for tale in talesCount if talesCount[tale] == len(queryList)]
    return (set(talesPrint), freDict, freDict2)


# print the main body of output
def printCore(talesPrint, w2s, tales_list, queryList, isOr, isNear, numSet, numSet2, isMore, freDict, freDict2, frequency):
    lastQuery = queryList[-1]
    for tale in talesPrint:
        print("\t", tale)
        if isMore:
            if frequency.isdigit():
                print("\t ",queryList[0],'appears',freDict[tale],'time(s) in this tale,','which is more than',frequency)
            else:
                
                if frequency in freDict2:
                    print("\t ",queryList[0],'appears',freDict[tale],'time(s) in this tale','WHILE',frequency,'appears',freDict2[tale],'time(s) in this tale')
                else:
                    print("\t ",queryList[0],'appears',freDict[tale],'time(s) in this tale','WHILE',frequency,'appears 0 time in this tale')
        if isNear:
            queryList = queryList[0:1]
        for oneQuery in queryList:
            if isOr:
                print("\t  ", oneQuery)
                if oneQuery not in w2s.keys():
                    print('\t\t--')
                else:
                    if tale not in w2s[oneQuery]:
                        print('\t\t--')
                    else:
                        for num in w2s[oneQuery][tale]:
                            printItem(tales_list, oneQuery, num, len(queryList))
            elif isNear:
                print('\t ','Lines containing',oneQuery,':')
                for num in numSet:
                    if num in w2s[oneQuery][tale]:
                        printItem(tales_list, oneQuery, num, 1)
                print('\t ','Nearby lines containing',lastQuery,':')
                for num in numSet2:
                    if num in w2s[oneQuery][tale]:
                        printItem(tales_list, lastQuery, num, 1)
            else:
                if len(queryList) != 1:
                    print("\t  ", oneQuery)
                for num in w2s[oneQuery][tale]:
                    printItem(tales_list, oneQuery, num, len(queryList))


def searchWords(w2s, tales_list, query):
    print("query = ", query)
    query = query.lower()
    queryList = []
    isOr = ' or ' in query
    isAnd = ' and ' in query
    isMore = ' morethan ' in query
    isNear = ' near ' in query
    talesPrint = []
    numSet = set()  # for near
    numSet2 = set()
    frequency = 0
    if isMore:
        queryList = query.split(' morethan ')[0:1]
        frequency = query.split(' morethan ')[1]
    elif isAnd:
        queryList = query.split(' and ')
    elif isOr:
        queryList = query.split(' or ')
    elif isNear:
        queryList = query.split(' near ')
    else:
        queryList = query.split()
    talesCount = {}
    if not inW2S(w2s, queryList, isOr):
        print('\t--')
    else:
        for oneQuery in queryList:
            if oneQuery in w2s.keys():
                for key in w2s[oneQuery].keys():
                    count = talesCount.get(key, 0) + 1
                    talesCount[key] = count
        (talesPrint, freDict, freDict2) = classifyOutput(isOr, isMore, isNear, w2s, talesCount, tales_list, queryList, frequency, numSet, numSet2)

        if len(talesPrint) == 0:
            print('\t--')
        else:
            printCore(talesPrint, w2s, tales_list, queryList, isOr, isNear, numSet, numSet2, isMore, freDict, freDict2, frequency) 


def main():
    (stopwords_list, tales_list, w2s, titles) = buildIndex()
    print('Loading stopwords...')
    print(stopwords_list)
    print('')
    print('Building index...')
    for i in range(len(titles)):
        print(i + 1, titles[i])
    print('')
    print("Welcome to the Grimms' Fairy Tales search systems!")
    print('')
    query = input("Please enter your query: ")
    while query != 'qquit':
        if query == 'qquit':
            exit(0)
        searchWords(w2s, tales_list, query)
        query = input("Please enter your query:")


if __name__ == "__main__":
    main()

# Feb 12
