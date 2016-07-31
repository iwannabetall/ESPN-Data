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

##scrapes 2015-16 regular season - 2015-11-13 2016-04-04
#2014-15 regular season 2014-11-13 to 2015-03-08
# CONSTANTS
#http://espn.go.com/mens-college-basketball/scoreboard/_/date/20160224
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
    
    soup = make_soup(ESPN_URL + "/mens-college-basketball/scoreboard/_/group/3/date/" + gamedate)
#first game last game 2015-11-13 2016-04-04
#2013-14 2013-11-08 2014-04-07
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
    #print script
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
    
    return games
#shot chart <div data-module="shotChart" id="gamepackage-shot-chart">

def get_play_by_play(gameid, current_date):
    "Returns the play-by-play data for a given game id."
    #game 400841592 has OT
    pbplink = "/mens-college-basketball/playbyplay?gameId="
    print (ESPN_URL + pbplink + gameid)
    soup = make_soup(ESPN_URL + pbplink + gameid)  #make_soup opens the url and returns the source code
#<<<<<<< HEAD
    #print soup
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
    #get link for image of team logo to tell what team data is for
    awayteaminfo = []  #array of logo image link and team name
    hometeaminfo = []
    teamclasses = ["team home", "team away"]
    teamlogolinks = {}
    game_data = []
    for j in range(len(teamclasses)):
        teaminfo = soup.find_all("div", teamclasses[j])  #get team info - gets too much home/away info
        logolink = []
        for i in range(len(teaminfo)):
            teamname = teaminfo[i].find("span","long-name").text
            if teaminfo[i].find("div", "logo").contents == []:  #not all teams have logo
                logolink = "null"
                teamlogolinks.update({"null":teamname})  #dictionary of logo img links and corresponding team
            else:    
                teamlogo = teaminfo[i].find_all("img", "team-logo")
                logolink = teamlogo[i]["src"]
                teamlogolinks.update({teamlogo[i]["src"]:teamname})  #dictionary of logo img links and corresponding team
            mascot = teaminfo[i].find("span","short-name").text
            teamrecord = teaminfo[i].find("div","record").text  #has inner record
            #teamrecord2 = teaminfo[i].find("span","inner-record").text
            teamrank = "NR"
            #check if team is ranked
            if teaminfo[i].find("span","rank") != None:
                teamrank = teaminfo[i].find("span","rank").text 
            if len(logolink) > 0:  #if got link for logo
                if teamclasses[j] == "team away":
                    AwayTeam = teamname
                    awayteaminfo.extend([AwayTeam, mascot, teamrank, teamrecord]) 
                    awayteaminfo = [str(x) for x in awayteaminfo]
                elif teamclasses[j] == "team home":
                    HomeTeam = teamname
                    hometeaminfo.extend([HomeTeam, mascot, teamrank, teamrecord]) 
                    hometeaminfo = [str(x) for x in hometeaminfo]
                break
    game_data.extend([current_date, gameid]) 
    game_data = game_data + hometeaminfo + awayteaminfo

    #get scores, pbp description, and time stamp 

    pbprow = []
    scores = soup.find_all('td', attrs = {'class' : 'combined-score'})
    description = soup.find_all('td', attrs = {'class' : 'game-details'})
    timestamp = soup.find_all('td', attrs = {'class' : 'time-stamp'})
    logospbplinks = soup.find_all('td', attrs = {'class' : 'logo'})
    logos = []
    pbpteam = []  #team for which the pbp data is for
    pbpdata = []
    for i in range(len(logospbplinks)):
        logos.append(logospbplinks[i].find("img", attrs = {'class' : 'team-logo'})["src"])
#find match btwn link of logo from pbp data (logos) and link of logo from data table.  if match 1st, use that, if not use hte other        
        if logos[i] == teamlogolinks.keys()[0]:  
            pbpteam.append(teamlogolinks.values()[0])
        else:
            pbpteam.append(teamlogolinks.values()[1])

#concatenate pbp info row by row 
    for i in range(len(scores)):
        pbprow.extend([timestamp[i].text,description[i].text,scores[i].text, pbpteam[i]])
        pbpdata.append(pbprow)
        pbprow = []
    
    #print game_data
    return pbpdata, game_data

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
            #game_id = game.lower().split("gameid=")[1]
            game_id = str(game)

            # I didn't feel like dealing with unicode characters
            try:
                print "Writing data for game: {0}".format(game_id)
                #save the data 
                #cbb-play-data/ is a directory/folder and will write separate file for each game
                pbp, game_data = get_play_by_play(game, d.strftime("%Y-%m-%d"))

                game_details.append(game_data)
               ##comment out from here  
                if pbp:
                    #filename = "cbb-pbp-data-14-15/{0}/".format(d.strftime("%Y-%m-%d")) + game_id + ".csv"
                    filename = "cbb-pbp-data-13-14/{0}/".format(d.strftime("%Y-%m-%d")) + game_id + ".csv"
                    if not os.path.exists(os.path.dirname(filename)):
                        os.makedirs(os.path.dirname(filename))
                    with open(filename, "w") as f:
                        writer = csv.writer(f, delimiter="\t")
                        #header of the data 
                        writer.writerow(["time", "description", "score", "team"])
                        writer.writerows(pbp)
                ##to here if don't want to print '''
            except UnicodeEncodeError:
                print "Unable to write data for game: {0}".format(game_id)
                print "Moving on ..."
                continue
            except urllib.HTTPError, detail:
                if detail.errno == 500:
                    print "wtf"
                    time.sleep(1)
                    continue
        d += delta
        sleep(2) # be nice
    #print game_details
    with open("cbb-pbp-data-13-14/A10GameDetails.csv", "w") as f:
        writer = csv.writer(f, delimiter=",")
        #header of the data 
        writer.writerow(["Date", "Game_id", "HomeTeam", "HomeMascot", "HomeRank", "HomeRecord", "AwayTeam", "AwayMascot","AwayRank", "AwayRecord"])
        writer.writerows(game_details)
    print "Done!" 

    os.system('say "DunDunDun Donnne"')