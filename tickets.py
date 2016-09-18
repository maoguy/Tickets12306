# coding=utf-8
'''Usage: tickets.py [-gdktz] <fromplace> <toplace> <date>

Arguments:
    <fromplace> place from where you begin this journey
    <toplace> place that you wanna go to

Options:
    -h,--help 帮助
    -g        高铁
    -d        动车
    -k        快速
    -t        特快
    -z        直达
'''

import os
import re
import requests
import json
from docopt import docopt
from prettytable import PrettyTable


def downloadConvertFile():
    if os.path.exists('convertData.txt'):
        return
    dataURL = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8955'
    responseData = requests.get(dataURL, verify = False)
    fileData = responseData.content[20:]
    toWrite = open('convertData.txt', 'w')

    try:
        toWrite.write(fileData)
    except:
        toWrite.close()
        os.remove('convertData.txt')

    toWrite.close()

def getCODEC(place):
    toRead = open('convertData.txt','r')
    text = ''
    try:
        text = toRead.read()
    except:
        print u'缓存文件读取出错!'
        return {}
    toRead.close()

    reResult = dict(re.findall('([A-Z]+)\|([a-z]+)',text))
    resultDict = dict(zip(reResult.values(), reResult.keys()))
    retDict = {}
    for key in resultDict.keys():
        if(key == place):
            retDict[key] = resultDict[key]

    #print retDict.values()
    return retDict.values()

def getQueryJson(FROMCODE, TOCODE, DATE):
    url = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}'.format(DATE, FROMCODE, TOCODE)
    #print url
    result = requests.get(url, verify = False)
    return result.json()

def colorText(color, text):
    if color == 'red':
        return ''.join(['\033[91m', text, '\033[0m'])
    elif color == 'green':
        return ''.join(['\033[92m', text, '\033[0m'])
    elif color == 'yellow':
        return ''.join(['\033[93m', text, '\033[0m'])
    elif color == 'blue':
        return ''.join(['\033[94m', text, '\033[0m'])
    elif color == 'white':
        return text

class TrainClass:
    trainNumber = ''
    startStop = ''
    endStop = ''
    startTime = ''
    endTime = ''
    totalTime = ''
    day = ''
    canBuy = ''

    businessSeatNum = ''
    specialSeatNum = ''
    firstSeatNum = ''
    secondSeatNum = ''

    advancedSoftBedNum = ''
    softBedNum = ''
    hardBedNum = ''
    softSeatNum = ''
    hardSeatNum = ''
    noneSeatNum = ''
    PS = ''
    note = ''

    def generateLine(self):
        totalTime = self.totalTime.replace(':', u'时')
        if(self.day == '1'):
            totalTime = u'次日' + totalTime + u'分'
        elif(self.day == '2'):
            totalTime = u'第三日' + totalTime + u'分'
        info = [
            self.trainNumber,
            '\n'.join([colorText('red', self.startStop), colorText('green', self.endStop)]) if self.canBuy == 'Y'
                else '\n'.join([self.startStop, self.endStop]),
            '\n'.join([colorText('red', self.startTime), colorText('green', self.endTime)]) if self.canBuy == 'Y'
                else '\n'.join([self.startTime, self.endTime]),
            self.totalTime,
            colorText('red' if self.canBuy == 'N' else 'white', self.canBuy),
            self.businessSeatNum,
            self.specialSeatNum,
            self.firstSeatNum,
            self.secondSeatNum,
            self.advancedSoftBedNum,
            self.softBedNum,
            self.hardBedNum,
            self.softSeatNum,
            self.hardSeatNum,
            self.noneSeatNum,
            self.PS if self.note == '' else self.note.replace('<br/>', '  ')
        ]
        return info

def main():

    arg = docopt(__doc__)
    #print arg
    fPlace = arg['<fromplace>']
    tPlace = arg['<toplace>']
    date = arg['<date>']

    downloadConvertFile()
    fromDict = getCODEC(fPlace)
    toDict = getCODEC(tPlace)

    totalInfo = []

    for fromplace in fromDict:
        for toplace in toDict:
            jsonData = getQueryJson(fromplace, toplace, date)
            #print json.dumps(jsonData, ensure_ascii = False, encoding = 'utf-8')
            if json != None:
                jsonData = jsonData['data']
            else:
                print u'您的网络出了问题!请检测!'
                return
            if 'message' in jsonData.keys():
                continue
            if 'datas' in jsonData:
                jsonData = jsonData['datas']
            for queryTrain in jsonData:
                newTrain = TrainClass()
                newTrain.trainNumber = queryTrain['station_train_code']
                newTrain.startStop = queryTrain['from_station_name']
                newTrain.endStop = queryTrain['to_station_name']
                newTrain.startTime = queryTrain['start_time']
                newTrain.endTime = queryTrain['arrive_time']
                newTrain.totalTime = queryTrain['lishi']
                newTrain.day = queryTrain['day_difference']
                newTrain.canBuy = queryTrain['canWebBuy']

                newTrain.businessSeatNum = queryTrain['swz_num']
                newTrain.firstSeatNum = queryTrain['zy_num']
                newTrain.secondSeatNum = queryTrain['ze_num']
                newTrain.specialSeatNum = queryTrain['tz_num']

                newTrain.advancedSoftBedNum = queryTrain['gr_num']
                newTrain.hardSeatNum = queryTrain['yz_num']
                newTrain.softSeatNum = queryTrain['rz_num']
                newTrain.softBedNum = queryTrain['rw_num']
                newTrain.noneSeatNum = queryTrain['wz_num']
                newTrain.hardBedNum = queryTrain['yw_num']

                newTrain.PS = queryTrain['controlled_train_message']
                newTrain.note = queryTrain['note']
                canAdd = False
                if arg['-g'] == arg['-d'] == arg['-t'] == arg['-z'] == arg['-k'] == False:
                    canAdd = True
                elif arg['-g'] == True and newTrain.trainNumber[0] == 'G':
                    canAdd = True
                elif arg['-d'] == True and newTrain.trainNumber[0] == 'D':
                    canAdd = True
                elif arg['-t'] == True and newTrain.trainNumber[0] == 'T':
                    canAdd = True
                elif arg['-z'] == True and newTrain.trainNumber[0] == 'Z':
                    canAdd = True
                elif arg['-k'] == True and newTrain.trainNumber[0] == 'K':
                    canAdd = True
                if canAdd == True:
                    totalInfo.append(newTrain)

    header = '车次 出发、到达站 出发、到达时间 历时 可否网购 商务座 特等座 一等座 二等座 高级软卧 软卧 硬卧 软座 硬座 无座 备注'.split(' ')
    table = PrettyTable()
    table._set_field_names(header)
    for train in totalInfo:
        table.add_row(train.generateLine())
    print table


if __name__ == '__main__':
    main()
