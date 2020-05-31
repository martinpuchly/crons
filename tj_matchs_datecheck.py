#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import ftplib
from datetime import datetime
import os
import mysql.connector
from sys import exit
from dotenv import load_dotenv, find_dotenv

today =  datetime.today().strftime('%Y-%m-%d')

#ENV DATA
load_dotenv(find_dotenv())
MYSQL_HOST=os.getenv("MYSQL_HOST")
MYSQL_USER=os.getenv("MYSQL_USER")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD")
MYSQL_PORT=os.getenv("MYSQL_PORT")
MYSQL_DB=os.getenv("MYSQL_DB")


def mesiac(mesStr):
    return {
        'január': '01',
        'február': '02',
        'marec': '03',
        'apríl': '04',
        'máj': '05',
        'jún': '06',
        'júl': '07',
        'august': '08',
        'september': '09',
        'október': '10',
        'november': '11',
        'december': '12',
    }.get(mesStr.lower(), '01')

#ZAPASY OD DNES
conn = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST, database=MYSQL_DB, port=MYSQL_PORT)
cur = conn.cursor()

cur.execute("SELECT id, match_datetime, fn_ID FROM matches WHERE match_datetime>%s AND result=%s", (today, ""))
matchs = cur.fetchall()

for match in matchs:
    id_match = match[0]
    match_datetime = match[1]
    fn_ID = match[2]

    r=requests.get('https://www.zsfz.sk/zapas/{0}'.format(fn_ID))
    c = r.content
    page = BeautifulSoup(c, "html.parser")

    wherMatchData = dateDiv = page.find("div", {"class":"team-title"}).getText().lower()
    wherMatch = 1
    if "špačince" in wherMatchData:
         wherMatch = 0

    dateDiv = page.find("div", {"class":"topline clearfix"})
    date = dateDiv.find("div", {"class":"col col-md-3 col-xs-8 uppercase m-date"}).getText()

    if date:
        dateDateTimeArr = date.split(", ")
        timeArr = dateDateTimeArr[1].split(":")
        dateArr = dateDateTimeArr[0].split(".")
        dateArr[1]=mesiac(dateArr[1])
        dateUpd = datetime(int(dateArr[2]), int(dateArr[1]), int(dateArr[0]), int(timeArr[0]), int(timeArr[1]))

        cur.execute('UPDATE matches SET match_datetime=%s, home_away=%s WHERE id=%s AND fn_ID=%s', (dateUpd, wherMatch, id_match, fn_ID))
        conn.commit()

conn.close
print ("OK!")
