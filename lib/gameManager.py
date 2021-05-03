import sys
import copy

from stockChart import StockChart
from stockDB import StockDB

class ConditionOutOfIndexException(Exception):
    pass

class Result:
    def __init__(self):
        self.data = []
        self.sum = 0
        self.mul = 1.0
        self.money = 1.0
        self.count = 0

    def __add__(self, other):
        newData = Result()
        newData.data = self.data + other.data
        newData.sum = self.sum + other.sum
        newData.mul = self.mul * other.mul
        newData.money = self.money * other.money
        newData.count = self.count + other.count

        return newData

class GameManager:
    def __init__(self, parameters):
        self.stockChart = StockChart(StockDB())
        self.codeList = parameters
        self.results = {}
        self.resultCnt = 0
        self.minCharts = {}
        self.fromDate = 0
        self.toDate = 0
        self.isModified = False

    def 일봉(self, x):
        if x >= len(self.chart) or x < 0:
            raise ConditionOutOfIndexException()
        return self.chart[x]

    def 분봉(self, x):
        if x in self.minCharts:
            return self.minCharts[x]
        else:
            minChart = self.stockChart.getMinChart(self.code, self.chart[x]['date'], self.chart[x]['date'], 1)
            self.minCharts[x] = minChart
            return minChart

    def 상한가(self, x):
        current = self.preChart[x]
        if current['high'] / current['prev'] > 1.28 and current['volume'] > 100000:
            curHoga = current['prev'];
            while True:
                curHoga2 = self.GetNextHoga(curHoga, 1, self.group);
                if curHoga2 / current['prev'] > 1.3000001:
                    break
                curHoga = curHoga2

            if (curHoga == current['close']):
                return True
        return False

    def GetNextHoga(self, price, n, group):
        for i in range(n):
            if price < 1000:
                price += 1;
            elif price < 5000:
                price += 5
            elif price < 10000:
                price += 10
            elif price < 50000:
                price += 50
            else:
                if group == "d" or price < 100000:
                    price += 100;
                elif price < 500000:
                    price += 500
                else:
                    price += 1000
        return price

    def GetPrevHoga(self, price, n):
        for i in range(n):
            if price < 1000:
                price -= 1;
            elif price < 5000:
                price -= 5
            elif price < 10000:
                price -= 10
            elif price < 50000:
                price -= 50
            elif price < 100000:
                price -= 100
            elif price < 500000:
                price -= 500
            else:
                price -= 1000
        return price

    def Run(self):
        for code in self.codeList:
            print(code[0])
            sys.stdout.flush()

            self.code = code[0]
            self.group = code[1]

            self.preChart = self.stockChart.getDayChart(self.code, self.fromDate, self.toDate)
            self.chart = self.preChart
            if self.isModified:
                self.chart = self.getModifiedChart(self.chart)

            for i in range(len(self.chart)):
                if (self.일봉(i)['volume'] == 0):
                    continue
                try:
                    self.Strategy(i);
                except ConditionOutOfIndexException:
                    pass

        return (self.resultCnt, self.results)

    def setResult(self, key):
        self.results[key] = Result()

    def addResult(self, key, 일봉, value):
        date = 일봉['date']
        if key not in self.results:
            self.setResult(key);

        self.results[key].sum += value
        self.results[key].mul *= value
        self.results[key].count += 1
        self.results[key].money *= (value)

        self.results[key].data.append(self.code + ' ' + str(date))

    def addCase(self):
        self.resultCnt += 1

    def IsStay(self, data, price ):
        if  (data['open'] == price and 
            data['high'] == price and
            data['low'] == price and
            data['close'] == price):
                return True
        else:
            return False

    def getAveLine(self, datas, n):

        closeList = []
        for data in datas:
            closeList.append(data['close'])

        aveList = []
        for i in range(len(closeList) - n + 1):
            data = closeList[i:i+n]

            ave = sum(data) / float(len(data))
            aveList.append(ave)

        return aveList

    def maximum(self, datas, key):
        max = 0
        for data in datas:
            if data[key] > max:
                max = data[key]

        return max

    def minimum(self, datas, key):
        max = 9999999
        for data in datas:
            if data[key] < max:
                max = data[key]

        return max

    def getModifiedChart(self, chart):
        chart = copy.deepcopy(chart);
        length = len(chart)

        if length <= 0:
            return chart

        last = chart[-1]

        for i in range(length - 1, 0, -1):
            current = chart[i]['prev']
            prev = chart[i - 1]['close']

            if current != prev:

                ratio = current / float(prev)
                
                chart[i - 1]['open'] *= ratio
                chart[i - 1]['close'] *= ratio
                chart[i - 1]['high'] *= ratio
                chart[i - 1]['low'] *= ratio
                chart[i - 1]['prev'] *= ratio
                chart[i - 1]['volume'] /= ratio
                chart[i - 1]['buy'] /= ratio
                chart[i - 1]['sell'] /= ratio

        return chart

if __name__ == "__main__":
    ConditionManager().Run()