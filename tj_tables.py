#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import ftplib
from datetime import datetime
import os
import sys
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


FTP_HOST=os.getenv("FTP_HOST")
FTP_USER=os.getenv("FTP_USER")
FTP_PASSWORD=os.getenv("FTP_PASSWORD")


dir_path = os.getcwd()

teamsID = {
  "atim": 34597,
  "dorast": 37435,
  "ziaci": 34598
}

def createTable(team, teamID):
    r=requests.get("https://tj-druzstevnik-spacince.futbalnet.sk/tim/{}/".format(teamID))
    c=r.content

    page = BeautifulSoup(c, "html.parser")

    table = page.find("table", {"class":"table"})
    clubs = table.find_all("a")
    points = table.find_all("td")

    clubs_b=[]
    clubs_n=[]
    num = 0
    for club in clubs:
        clubs_n.append(club.get_text())
        num+=1

    bn = 1
    for b in points:
        if bn==9 or (bn-9)%12==0:
            clubs_b.append(b.get_text())
            #bn+=3
        bn+=1

    tableHTML = "<div class='row font-weight-bold' style='border-bottom: 0.1em solid black'>"
    tableHTML += "<div class='col-1'>P.</div>"
    tableHTML += "<div class='col-9'>Klub</div>"
    tableHTML += "<div class='col-1'>B</div>"
    tableHTML += "</div>"

    for i in range(num):
        style=""
        if "Špačince" in clubs_n[i]:
            style="font-weight:bold"
        elif "odstúpené" in clubs_n[i]:
            style="color:grey;text-decoration: line-through;"
        else:
            style=""

        tableHTML += "<div class='row' style='"+style+"'>"
        tableHTML += "<div class='col-1'>"+ str(i+1) +".</div>"
        tableHTML += "<div class='col-9'>"+ clubs_n[i] +"</div>"
        tableHTML += "<div class='col-1 text-align-center'>"+ clubs_b[i] +"</div>"
        tableHTML += "</div>"

    f = open("{}/tj_table_{}.html".format(dir_path, team), "w+")
    f.truncate()
    f.write(tableHTML)
    f.close()

    ftp = ftplib.FTP(FTP_HOST,FTP_USER,FTP_PASSWORD)
    ftp.cwd('/web/uploads/')
    file = open('{}/tj_table_{}.html'.format(dir_path, team),'rb')                  # file to send
    ftp.storbinary('STOR table_{}.html'.format(team), file)     # send the file
    file.close()                                    # close file and FTP
    ftp.quit()
    os.remove("{}/tj_table_{}.html".format(dir_path, team))        #remove file with table (I don't know why I am creating it :-D)


for team in teamsID:
    teamID = teamsID.get(team)
    try:
        createTable(str(team), str(teamID))
        print ("{} table -> uploaded".format(team))
        f = open("{}/tj_crons_logs.txt".format(dir_path), "a+")
        f.read()
        f.write(str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")) +"-> {} table -> uploaded\n".format(team))
        f.close()
    except:
        print ("{} table -> upload ERROR".format(team))
        f = open("{}/tj_crons_logs.txt".format(dir_path), "a+")
        f.read()
        f.write(str(datetime.now().strftime("%d-%m-%Y %H:%M:%S")) +"-> {} table -> upload ERROR\n".format(team))
        f.close()
