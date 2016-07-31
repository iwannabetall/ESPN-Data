from bs4 import BeautifulSoup
import urllib2
from urllib2 import urlopen
import csv
import pandas as pd 
import math 
import numpy as np
import re
import os
from datetime import datetime
import cookielib
from cookielib import CookieJar
from time import sleep   #tells your program to run and then pause (for updated data)


'''this file gets the shot chart data.  uses game id from game details and goes to pbp page
make 3 changes for file references for diff seasons 
'''
ESPN_URL = "http://espn.go.com"  ##global var

#print ("hello")
def make_soup(url):
    cj = CookieJar() # Not absolutely necessary but recommended
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0')] # To be able to crawl on websites that blocks Robots
    soup = BeautifulSoup(opener.open(url).read(), "html.parser")
    soup.prettify()
    #print soup
    return soup

##get game details 
def Readme(conf):
    #game_details = pd.read_csv("cbb-pbp-data-13-14/" + conf + "GameDetails.csv",sep = ',')
    #game_details = pd.read_csv("cbb-pbp-data-15-16/" + conf + "GameDetails.csv",sep = ',')
    ###14-15 season
    game_details = pd.read_csv("cbb-play-data/" + conf + "Team_GameIDs.csv",sep = ',')
    game_ids = game_details["Game_id"]
    dates = game_details["Date"]
    Home_Team = game_details["HomeTeam"]
    Away_Team = game_details["AwayTeam"]
    return dates, game_ids, Home_Team, Away_Team

def get_Rosters(gameid):
    pbplink = "/mens-college-basketball/playbyplay?gameId="
    #print (ESPN_URL + pbplink + gameid)
    soup = make_soup(ESPN_URL + pbplink + gameid)  #make_soup opens the url and returns the source code
    #get team rosters and convert player ID to name, add team name to player
    hometeamids = []
    awayteamids = []
    rosters = soup.find_all("ul", "dropdown-menu sm playerfilter")
    roster = {}   #dictionary of player id 
    for j in range(len(rosters)):
        playerlist = rosters[j].find_all("li")
        for i in range(len(playerlist)):
            homeaway = playerlist[i]["data-homeaway"].encode()
            playerid = playerlist[i]["data-playerid"].encode()
            playername = playerlist[i].findAll(text=True)[0].encode('utf-8')
            roster.update({playerid: playername})
            if homeaway == "home":
                hometeamids.append(playerid)
            else:
                awayteamids.append(playerid)
    return roster, hometeamids, awayteamids

"Returns the shot chart data for a given game id."
    #game 400841592 has OT
    #400839211 doesn't have shot chart data 
def get_shots(gameid, hometeam, awayteam):
    pbplink = "/mens-college-basketball/playbyplay?gameId="
    print (ESPN_URL + pbplink + gameid)
    soup = make_soup(ESPN_URL + pbplink + gameid)  #make_soup opens the url and returns the source code
    shooting_team = ["shots away-team", "shots home-team"]
    attributes = ["data-period", "data-homeaway", "style", "data-text", "data-shooter", "id", "class"]
    SC_data = []
    roster, hometeamids, awayteamids = get_Rosters(gameid)
    #soup = make_soup(ESPN_URL + pbplink + id1)
    #soup.find_all("div", {"id":"gamepackage-shot-chart"})
    #soup.find_all("div", {"data-module":"shotChart"})
    for i in range(len(shooting_team)):
         #why cant i do length of shotchart[0]? always off by 2
        shotchart = soup.find_all("ul", shooting_team[i])  #get data for home/away team
        if shotchart: #not all teams have shot chart data
            num_shots = len(shotchart[0].find_all("li")) 
            for j in range(num_shots):
                leftside = 0  #1 if on left side, 0 if not
                FGA3 = 0 #becomes a 1 if 3 pt FGA (later)
                made = 0
                assisted = 0
                jumper = 0
                layup = 0
                dunk = 0
                row_data = []
                team = hometeam
                pd = shotchart[0].find_all("li")[j].attrs["data-period"].encode('ascii','ignore')
                homeaway = shotchart[0].find_all("li")[j].attrs["data-homeaway"].encode('ascii','ignore')
                xy_loc = shotchart[0].find_all("li")[j].attrs["style"].encode('ascii','ignore')
                description = shotchart[0].find_all("li")[j].attrs["data-text"].encode('ascii','ignore')
                playerid = shotchart[0].find_all("li")[j].attrs["data-shooter"].encode('ascii','ignore')
                shotnum = shotchart[0].find_all("li")[j].attrs["id"].encode('ascii','ignore')
                made_miss = shotchart[0].find_all("li")[j].attrs["class"][0].encode('ascii','ignore')
                player = roster.get(playerid)
                if playerid in awayteamids:
                    team = awayteam
                if made_miss == "made":
                    made = 1
                xys = xy_loc.split(";")
                for m in range(len(xys)):
                    if "left:" in xys[m]:
                        left = xys[m].split(":")
                        left = int(left[1].split("%")[0])
                    if "top:" in xys[m]:
                        top = xys[m].split(":")
                        top = int(top[1].split("%")[0])
                rim_top = 47
                if left > 50: ##other side of the court 
                    rim_left = 95
                    #(66,50) = almost dead straight ahead, from coaches mark
                    ##distance in feet from rim -- conversions: 11.28 inches/px for left, 6.38 inches/px for
                    distance = math.sqrt(((left - rim_left)*11.28) ** 2 + ((top - rim_top)*6.38)**2)/12
                    if top < 47:  #left/right side
                        leftside = 1
                else:   #left <= 50
                    rim_left = 5
                    distance = math.sqrt(((left - rim_left)*11.28) ** 2 + ((top - rim_top)*6.38)**2)/12
                    if top > 47:
                        leftside = 1
                #get angle - relative to facing basket (free throw is 0 degrees)
                opp_length = math.fabs(top - rim_top)*6.38
                adj_length = math.fabs(left - rim_left)*11.28
                angle = 0
                if adj_length > 0: #if not a dunk, ie divide by 0
                    angle = math.degrees(math.atan(opp_length/adj_length))
                #3 point fga indicator 
                if "Three Point" in description:
                    FGA3 = 1
                if "Assisted" in description:
                    assisted = 1
                if "Jumper" in description:
                    jumper = 1
                if "Layup" in description:
                    layup = 1
                if "Dunk" in description:
                    dunk = 1
                    #adjust 3 point FGA distance -- marked 4-5 feet behind the line 
                    ft_behind_line = distance - 20.75
                    if ft_behind_line > 0: 
                        distance = distance - float(ft_behind_line)*0.75
                row_data.extend([gameid, player, pd, homeaway, team,distance, angle, leftside ,left, top, description, playerid,shotnum,made, FGA3, assisted, jumper, layup, dunk])
                SC_data.append(row_data)
    return SC_data

def main():
    conferences = ["ACC", "Big10", "SEC","A10", "PAC12","Big12","BigEast"]
    conf = str(raw_input("Pick a conference: ACC, Big10, SEC, A10, PAC12, Big12, BigEast. "))
    dates, gameids, Home_Team, Away_Team = Readme(conf)
    # I didn't feel like dealing with unicode characters
    #save the data 
    #cbb-play-data/ is a directory/folder and will write separate file for each game
    counter = 0
    got_shots = []
    listmissing_games = []
    for k in range(len(gameids)):
        missing_games = []
        shots = get_shots(str(gameids[k]), Home_Team[k], Away_Team[k])
         ##comment out from here  
        missing_data = k - counter
        if shots:
            print "Writing data for game: {0}".format(gameids[k])
            got_shots.append(gameids[k])
            d = dates[k]
            d = datetime.strptime(d,"%Y-%m-%d")
            #filename = "cbb-pbp-data-15-16/{0}/".format(d.strftime("%Y-%m-%d")) +"SC_" + str(gameids[k]) + ".csv"
            #14-15 season
            filename = "cbb-play-data/{0}/".format(d.strftime("%Y-%m-%d")) +"SC_" + str(gameids[k]) + ".csv"
            #filename = "cbb-pbp-data-13-14/{0}/".format(d.strftime("%Y-%m-%d")) +"SC_" + str(gameids[k]) + ".csv"
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
                #filename = "sc.csv"
            with open(filename, "w") as f:
                counter = counter + 1
                writer = csv.writer(f, delimiter="\t")
                #header of the data         
                writer.writerow(["Game_id","player","pd", "homeaway", "team","distance","angle", "leftside", "left","top", "description", "playerid","shotnum","made", "FGA3", "assisted","jumper", "layup", "dunk"])
                writer.writerows(shots)
            print "Got game " + str(counter) + " of " + str(k) + "/" + str(len(gameids)) +". " + dates[k] + ", " + Home_Team[k] + "-" + Away_Team[k] + "."     
        if not shots:
            missing_games.extend([gameids[k],dates[k], Home_Team[k], Away_Team[k]])
            listmissing_games.append(missing_games)
            print "Missing: " + str(missing_data) + ": " + dates[k] + ", " + Home_Team[k] + "-" + Away_Team[k] + "."
            ##to here if don't want to print '''
        sleep(2) # be nice
    #filename = "cbb-pbp-data-15-16/" + "MissingShotsfor" + conf + ".csv"
    #filename = "cbb-pbp-data-13-14/" + "MissingShotsfor" + conf + ".csv"  #13-14 season
    filename = "cbb-play-data/" + "MissingShotsfor" + conf + ".csv"  #14-15 season
    titles = ["Game_id","Date", "Home_Team", "Away_Team"]
    with open(filename, "wb") as g:
        writer = csv.writer(g, delimiter = ",")
        writer.writerow(titles)
        writer.writerows(listmissing_games)
    os.system('say "DunDunDun Donnne"')
    os.system('afplay /System/Library/Sounds/Sosumi.aiff')


if __name__ == '__main__':
    main()
#pd.read_csv("cbb-play-data/Big10Team_GameIDs.csv", sep = ",")
#datetime.strptime(d,"%Y-%m-%d")
#  dates[i] = datetime.datetime.strptime(dates[i],"%m/%d/%y").strftime("%Y-%m-%d") 
#SC_data.to_csv("testSC.csv", sep = '\t')
'''except UnicodeEncodeError:
    print "Unable to write data for game: {0}".format(game_id)
    print "Moving on ..."
    continue
except urllib.HTTPError, detail:
    if detail.errno == 500:
        print "wtf"
        time.sleep(1)
        continue
                    '''