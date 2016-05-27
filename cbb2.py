from bs4 import BeautifulSoup
import urllib2
from urllib2 import urlopen
import cookielib
from cookielib import CookieJar
from datetime import datetime, timedelta
import json
import re
#from urllib2.request import urlopen
#import html5lib
#from . import _htmlparser
#import requests
#import lxml
#from lxml.html import *
from time import sleep   #tells your program to run and then pause (for updated data)
import sys
import csv
import mechanize
import os

#2014-15 regular season 2014-11-13 to 2015-03-08
# CONSTANTS
http://espn.go.com/mens-college-basketball/scoreboard/_/date/20160224
ESPN_URL = "http://espn.go.com"  ##global var
cj = CookieJar() # Not absolutely necessary but recommended
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0')] # To be able to crawl on websites that blocks Robots

#print ("hello")
def make_soup(url):
    soup = BeautifulSoup(opener.open(url).read(), "html.parser")
    soup.prettify()
    #print soup
    return soup


def get_games(gamedate):
    """
    Gets all the play-by-play URLs for a given date (YYYYMMDD).
    Fair warning: ESPN doesn't have play-by-play data for all games.
    """
    
    soup = make_soup(ESPN_URL + "/mens-college-basketball/scoreboard/_/group/21/date/" + gamedate)

        #"/ncb/scoreboard?date={0}&confId=3".format(date))   #all ACC games
    #http://scores.espn.go.com/mens-college-basketball/scoreboard/_/group/21/date/20151122
##conf IDs: ACC: 2; Big 10: 7; Big 12:8; SEC: 23; Pac 12:21; Big East: 4; A10: 3; Mountain West: 44; Am East: 1 
    #have data for ACC, Big10,Big12,SEC,Pac12,Big East, A10 games 
    #"get's all conferences?  /ncb/scoreboard?date=""
    #array of span tags that start with, start with id and end with "-gamelinks-expand", 
    #eg <span id="400589301-gameLinks-expand"><a href="/ncb/boxscore?gameId=400589301">Box&nbsp;Score</a>&nbsp;&#187;&nbsp;  <a href="/ncb/playbyplay?gameId=400589301">Play&#8209;By&#8209;Play</a>&nbsp;&#187;&nbsp;  <a href="/ncb/video?gameId=400589301">Videos</a>&nbsp;&#187;&nbsp;  <a href="/ncb/photos?gameId=400589301">Photos</a>&nbsp;&#187;&nbsp;  <a href="/ncb/conversation?gameId=400589301">Conversation</a>&nbsp;&#187;&nbsp;  </span>
    #x.lower changes everything to all lower case 
    #games = soup.findAll('a', text = 'Recap', attrs = {'class' : 'gameTracker'})  #gets all recap links 
    
    #games = soup.find_all("span", {"id": lambda x: x and x.lower().endswith("-gamelinks-expand")})   #gets game ID "from gameLinks-expand
    #pattern = re.compile(r"window\.espn\.scoreboardData = (.*);", re.MULTILINE)
    script = soup.find("script", text=lambda x: x and "window.espn.scoreboardData" in x).text  #get dictionary
    print script
    #create acceptable JSON format
    script = script.split("window.espn.scoreboardData \t= ",1)[1] #keep everything after window.espn.scoreboardData \t= 
    script = script.partition(";window.espn.scoreboardSettings")[0]  #delete everything after
    #pattern = "recap?gameId"
    #re.search(pattern, script)
    data = json.loads(script)
    #data = json.loads(re.search(pattern, script).group(1))

    ##get pbp "text":"Play-by-Play" 
    #view-source:http://scores.espn.go.com/mens-college-basketball/scoreboard/_/group/21/date/20151113
    "playbyplay?gameId"
    "recap?gameId"
    #this gets all href game ID urls pieces, eg <a href="/ncb/playbyplay?gameId=400589301">            
    #link_sets = [game.find_all("a") for game in games]  #looking for everything inside games array with "a" tag 
    
    #get play by play links
    links = []  
    games = []
    for i in range(len(data["events"])):
        for j in range(len(data["events"][i]["links"])):
            if "playbyplay" in data["events"][i]["links"][j]["href"]:
                links.append(data["events"][i]["links"][j]["href"])  #pbp links
                games.append(data["events"][i]["links"][j]["href"].split("=")[-1])  #game IDs
        #links = data["events"][i]["links"][j]["href"].split("=")  #first index numbers have all games--need to loop thru all, 2nd number = various links for a game--only want pbp link
    
    return play_by_plays
#shot chart <div data-module="shotChart" id="gamepackage-shot-chart">

def get_play_by_play(gameid, current_date):
    "Returns the play-by-play data for a given game id."
    #game 400841592 has OT
    pbp = "/mens-college-basketball/playbyplay?gameId="
    print (ESPN_URL + pbp + gameid)
    soup = make_soup(ESPN_URL + pbp + gameid)  #make_soup opens the url and returns the source code
#<<<<<<< HEAD
    pds = soup.select('li [data-period]')  #use CSS selector to find length of game, ie # of OTs
    maxpd = []
    for i in range(len(pds)):
        maxpd.append(int(pds[i]["data-period"]))
    if max(maxpd) > 2:   #number of OTs if more than 2 pds played
        OTs = max(maxpd) - 2
    #create id tag to get pbp data by period 
    Q = "gp-quarter-" 
    for i in range(max(maxpd)):
        idtag = Q + str(maxpd[i] + 1)
        pbp = soup.find_all('div', attrs = {'id' : idtag }) 
    
    #h1table = soup.find_all("div", "accordion-content collapse in")  #first half pbp table 
    #h2table = soup.find_all("div", "accordion-content collapse")  #2nd half pbp table 
    ##table has table row and table data (tr, td), but table var is a string**
    print "------------------------------"
    #print soup
    #print "------------------------------"
    '''table = soup.find_all("div", "story-container")   #find the only table tag and returns string (find_all returns array)
    '''##table has table row and table data (tr, td), but table var is a string**
#>>>>>>> 8c94b1874697e0be2b50ddaf102d215faf710eb4
    #table rows has class for odd or even (probly why the table on espn is switched colors)
    #rows is an matrix of tr tags with even or odd 
    #eg <tr class="even"><td valign=top width=50>19:53</td><td valign=top>&nbsp;</td><td valign=top style="text-align:center;" NOWRAP>0-0</td><td valign=top>Karl-Anthony Towns missed Three Point Jumper.</td></tr>
    #each row in rows is an array of td's
    #print table
    #find_all splits table string into array by tr 
     <div class="team away"> #use to get image src link 
      <div class="team home">
      awayteam = soup.find_all("div", "team away")  #get team info
      awayteam = soup.find_all("div", "team home")  #get team info
      teams = soup.find_all("div", "team-container")  #get team info
    
    for t in teams:
        t.find_all("img","src", attrs = {'class' : 'team-logo'}) #get team info
    #find all table tags of class combined-score for each table row 
    #scores = [row.find_all("td",attrs = {'class' : 'combined-score'}) for row in soup.find_all("tr")]
    #description = [row.find_all("td",attrs = {'class' : 'game-details'}) for row in soup.find_all("tr")]
    #timestamp = [row.find_all("td",attrs = {'class' : 'time-stamp'}) for row in soup.find_all("tr")]
    logos = [x['src'] for x in soup.findAll('img', {'class': 'team-logo'})]
**find logos in tr tag 
    [row.find_all("img", "src", attrs = {'class' : 'team-logo'}) for row in soup.find_all("tr")]
    logos[32][0]["src"] #???WHY DOES THIS WORK??!
    
    #get scores, pbp description, and time stamp 
    scores = []
    description = []
    timestamp = []
    logos = []
    for tdtag in soup.find_all('td', attrs = {'class' : 'combined-score'}):
        scores.append(tdtag.text) 
    for tdtag in soup.find_all('td', attrs = {'class' : 'game-details'}):
        description.append(tdtag.text)
    for tdtag in soup.find_all('td', attrs = {'class' : 'time-stamp'}):
        timestamp.append(tdtag.text)
    for tdtag in soup.find_all('tr', attrs = {'class' : 'team-logo'}):
        logos.append(tdtag.text)
    
    data = []
    for row in rows:
        values = []
        for value in row:
            #if td is empty, append nothing/empty string; u might be unicode?
            #each string must be converted to unicode so you can process it
            ##some emoji's show up as boxes vs a emoji --> convert to unicode
            if value.string is None:    
                values.append(u"")
            else:
            #unicode has u"\xa0" as whitespace?, get rid of it and replace w/blank space
                values.append(value.string.replace(u"\xa0", u" "))   #u"\xa0" is unicode stuff -- read this 
        # handle timeouts being colspan=3
        # repeat the timeout or note in the other columns
        #</tr><tr class="odd"><td valign=top width=50>17:28</td><td colspan=3 style="text-align:center;"><b>Kentucky  Timeout</b></td></tr>
        #kentucky timeout spanned 3 colms


        if len(values) != 4:
            #print values
            values = [values[0], values[1], values[1], values[1]]  #timeout replaced multiple times 

        data.append(values)

    '''Find Home and Away Team infos for the game'''
    game_data = []
    team_data = []
    game_data = [gameid, current_date]
    for team in ["team home", "team away"]:
        matchup = soup.find("div", "matchup")
        the_team = soup.find("div", team)
        team_Name = the_team.find("a").text  #away team name 
        team_Rank = ""   #away team rank 
        rank = the_team.find("span", "rank")
        if rank:
            team_Rank = rank.text
        else:
            team_Rank = "NR"
        team_Record = the_team.find("p").text   #away team record 
        
        team_data.extend([team_Name, team_Rank, team_Record])
        team_data = [x.replace(u"\xa0", u" ") for x in team_data]
        #print "Name: %s, Rank %s, Record %s\n"%(team_Name, team_Rank, team_Record)
    #print game_data + team_data
    game_data = game_data + team_data

    #print game_data
    return data, game_data

if __name__ == '__main__':
    try:
        START_DATE = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        END_DATE = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    except IndexError:
        print "I need a start and end date ('YYYY-MM-DD')."
        sys.exit()

    d = START_DATE
    delta = timedelta(days=1)

    game_details = []

    while d <= END_DATE:
        print "Getting data for: {0}".format(d.strftime("%Y-%m-%d"))
        
        #games is array with /ncb/playbyplay?gameId=400589301
        games = get_games(d.strftime("%Y%m%d"))  #string format for date time 
        for game in games:
            game_id = game.lower().split("gameid=")[1]

            # I didn't feel like dealing with unicode characters
            try:
                print "Writing data for game: {0}".format(game_id)
                #save the data 
                #cbb-play-data/ is a directory/folder and will write separate file for each game
                pbp, game_data = get_play_by_play(game, d.strftime("%Y-%m-%d"))

                game_details.append(game_data)
               ##comment out from here  
                if pbp:
                    filename = "cbb-play-data/{0}/".format(d.strftime("%Y-%m-%d")) + game_id + ".csv"
                    if not os.path.exists(os.path.dirname(filename)):
                        os.makedirs(os.path.dirname(filename))
                    with open(filename, "w") as f:
                        writer = csv.writer(f, delimiter="\t")
                        #header of the data 
                        writer.writerow(["time", "away", "score", "home"])
                        writer.writerows(pbp)
                ##to here if don't want to print 
            except UnicodeEncodeError:
                print "Unable to write data for game: {0}".format(game_id)
                print "Moving on ..."
                continue
        d += delta
        sleep(2) # be nice
    #print game_details
    '''with open("cbb-play-data/game_details.csv", "w") as f:
                        writer = csv.writer(f, delimiter="\t")
                        #header of the data 
                        writer.writerow(["Game_id","Date", "HomeTeam", "HomeRank", "HomeRecord", "AwayTeam", "AwayRank", "AwayRecord"])
                        writer.writerows(game_details)
    print "Done!" 
    '''