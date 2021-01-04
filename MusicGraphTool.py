import urllib
import os
import json
import threading
import matplotlib.pyplot as plt
from urllib.request import urlopen
from urllib.request import HTTPError
from datetime import datetime

class Chart:
    API_KEY = os.environ.get('LFM_Key')
    lastPage = None
    count = 0
    page = 1
    artist = ''
    username= ''
    dates = []
    monthTotal = []
    startMonth = None
    startYear = None
    endMonth = None
    endYear = None

    def __init__(self, x):
        self.username = x
        
    def dateRange(self, startMonth, startYear, endMonth, endYear):
        self.startMonth = startMonth
        self.startYear = startYear
        self.endMonth = endMonth
        self.endYear = endYear
        
    def setArtist(self, artist):
        print("Getting Data -- Please Wait")
        self.artist = artist
        self.makeLink()
        self.countMonths()
        
    def getCount(self):
        return self.count
        
    def getDates(self):
        return self.dates
        
    def getMonthTotal(self):
        return self.monthTotal
     

    #Creates the links needed to get the user's information
    def makeLink(self):
        q1 = []
        q2 = []
        q3 = []
        q4 = []
        q5 = []
        q6 = []
        q7 = []
        q8 = []
        
        link = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + self.username + '&api_key=' + self.API_KEY + '&limit=200&format=json&page=' + str(self.page)
        try:
            response = urllib.request.urlopen(link)
        except HTTPError as e:
            content = e.read()
        try:
            data = json.loads(response.read())
        except ValueError:
            makeLink()
            
        if ((self.endMonth is None) or (self.endYear is None)):
            self.endMonth = datetime.fromtimestamp(int(data['recenttracks']['track'][0]['date']['uts']))
            self.endYear = self.endMonth.strftime('%y')
            self.endMonth = self.endMonth.strftime('%m')
        
        #Gets the total number of pages to create links to
        self.lastPage = int(data['recenttracks']['@attr']['totalPages'])
        link = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + self.username + '&api_key=' + self.API_KEY + '&limit=200&format=json&page=' + str(self.lastPage)
        try:
            response = urllib.request.urlopen(link)
        except HTTPError as e:
            content = e.read()
        try:
            data = json.loads(response.read())
        except ValueError:
            makeLink()
        
        if ((self.startMonth is None) or (self.startYear is None) or (self.endMonth is None) or (self.endYear is None)):
            self.startMonth = datetime.fromtimestamp(int(data['recenttracks']['track'][len(data['recenttracks']['track']) - 1]['date']['uts']))
            self.startYear = self.startMonth.strftime('%y')
            self.startMonth = self.startMonth.strftime('%m')
        
        #Creaes a link and assigns them into a list
        while self.page <= self.lastPage:
            link = 'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + self.username + '&api_key=' + self.API_KEY + '&limit=200&format=json&page=' + str(self.page)
            if self.page <= (.125 * self.lastPage):
                q1.append(link)
            elif self.page <= (.25 * self.lastPage):
                q2.append(link)
            elif self.page <= (.375 * self.lastPage):
                q3.append(link)
            elif self.page <= (.5 * self.lastPage):
                q4.append(link)
            elif self.page <= (.625 * self.lastPage):
                q5.append(link)
            elif self.page <= (.75 * self.lastPage):
                q6.append(link)
            elif self.page <= (.875 * self.lastPage):
                q7.append(link)
            else:
                q8.append(link)
            self.page += 1
        
        #Creates threads to run the getArtists function in parallel     
        t1 = threading.Thread(target=self.getArtists, args=(q1,)) 
        t2 = threading.Thread(target=self.getArtists, args=(q2,))
        t3 = threading.Thread(target=self.getArtists, args=(q3,)) 
        t4 = threading.Thread(target=self.getArtists, args=(q4,))
        t5 = threading.Thread(target=self.getArtists, args=(q5,)) 
        t6 = threading.Thread(target=self.getArtists, args=(q6,))
        t7 = threading.Thread(target=self.getArtists, args=(q7,)) 
        t8 = threading.Thread(target=self.getArtists, args=(q8,))

        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t6.start()
        t7.start()
        t8.start()
        
        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()
        t6.join()
        t7.join()
        t8.join()
        

    #Parses the JSON and adds entries matching the desired artists to a list
    def getArtists(self, q):
        while len(q) > 0:
            link = q.pop()
            try:
                response = urllib.request.urlopen(link)
                data = json.loads(response.read())
            
                for scrobble in data['recenttracks']['track']:
                    if self.artist.lower() == scrobble['artist']['#text'].lower():
                        if 'date' in scrobble:
                            timestamp = datetime.fromtimestamp(int(scrobble['date']['uts']))
                            self.dates.append(timestamp)
            except HTTPError as e:
                q.append(link)
      
    #Gets the monthly total for the artist
    def countMonths(self):
        month = int(self.startMonth)
        year = int(self.startYear)
        period = 1
        while (year <= int(self.endYear)):
            while month <= 12:
                if ((month > int(self.endMonth)) and (year == int(self.endYear))):
                    break
                monthCount = 0
                dateCopy = []
                while len(self.dates) > 0:
                    temp = self.dates.pop()
                    if (month == int(temp.strftime('%m')) and (year == int(temp.strftime('%y')))):
                        monthCount += 1
                        self.count += 1
                    else:
                        dateCopy.append(temp)
                self.monthTotal.append(monthCount)
                self.dates = dateCopy.copy()
                period += 1
                month += 1
            month = 1
            year += 1
            
print("Last.fm Monthly Play Graphing Tool")
print("----------------------------------\n")        
inputUser = Chart(input("Enter a Last.fm username: "))
customDates = input("Would you like a custom date range? Enter y for yes or press enter for no: ").lower()
if (customDates == 'y' or customDates == 'yes'):
    dateInput = ""
    while (("-" not in dateInput) or (len(dateInput) != 5)):
        dateInput = input("Enter the start date in the format MM-YY: ")
    stMonth = dateInput.split("-")[0]
    stYear = dateInput.split("-")[1]
    dateInput = ""
    while (("-" not in dateInput) or (len(dateInput) != 5)):
        dateInput = input("Enter the end date in the format MM-YY: ")
    eMonth = dateInput.split("-")[0]
    eYear = dateInput.split("-")[1]
    inputUser.dateRange(stMonth, stYear, eMonth, eYear)  
          
inputUser.setArtist(input("Enter the desired artist: "))
graphColor = input("Enter a color for the graph (ex: red, black, #00ff00): ")
print("Total Plays: " + str(inputUser.count))
monthTotal = inputUser.getMonthTotal()
months = []
i = int(inputUser.startMonth)
yr = int(inputUser.startYear)
graphStr = None
for m in monthTotal:
    if (i == 13):
        i = 1
    if (i % 12 == 1):
        graphStr = "Jan-"
    elif (i % 12 == 2):
        graphStr = "Feb-"
    elif (i % 12 == 3):
        graphStr = "Mar-"
    elif (i % 12 == 4):
        graphStr = "Apr-"
    elif (i % 12 == 5):
        graphStr = "May-"
    elif (i % 12 == 6):
        graphStr = "Jun-"
    elif (i % 12 == 7):
        graphStr = "Jul-"
    elif (i % 12 == 8):
        graphStr = "Aug-"
    elif (i % 12 == 9):
        graphStr = "Sep-"
    elif (i % 12 == 10):
        graphStr = "Oct-"
    elif (i % 12 == 11):
        graphStr = "Nov-"
    elif (i % 12 == 0):
        graphStr = "Dec-"
        graphStr = graphStr + str(yr)
        yr = yr + 1
    if (i % 12 != 0):
        graphStr = graphStr + str(yr)
    i = i + 1
    months.append(graphStr)
    
plt.grid(zorder=0)
plt.bar(months, monthTotal, align='center', color=graphColor, zorder=3)
plt.xticks(rotation='vertical', fontsize=8)
plt.title(inputUser.username + "'s " + inputUser.artist + " Chart")
#plt.ylim([0,900])
plt.savefig('artist.jpeg')
plt.show()
