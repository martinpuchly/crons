#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import ftplib
from datetime import datetime
import os
import mysql.connector
from sys import exit
from dotenv import load_dotenv, find_dotenv

#ENV DATA
load_dotenv(find_dotenv())
MYSQL_HOST=os.getenv("MYSQL_HOST")
MYSQL_USER=os.getenv("MYSQL_USER")
MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD")
MYSQL_PORT=os.getenv("MYSQL_PORT")
MYSQL_DB=os.getenv("MYSQL_DB")


today =  datetime.today().strftime('%Y-%m-%d')

#ZAPASY DNES
conn = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_USER, host=MYSQL_PASSWORD, database=MYSQL_DB, port=MYSQL_PORT)
cur = conn.cursor()

cur.execute("SELECT id, match_datetime, fn_ID FROM matches WHERE match_datetime LIKE '{0}'".format(today+'%'))
matchs = cur.fetchall()

for match in matchs:
    id_match = match[0]
    match_datetime = match[1]
    fn_ID = match[2]

    r=requests.get('https://www.zsfz.sk/zapas/{0}'.format(fn_ID))
    c = r.content
    page = BeautifulSoup(c, "html.parser")

    scoreDiv = page.find("div", {"class":"col col-xs-4 head-score"})
    score = scoreDiv.find("div", {"class":"big color-default-a"}).getText()
    scoreC=""
    if score:
        for s in score:
            scoreC = scoreC + s.strip()
        cur.execute('UPDATE matches SET result=%s WHERE id=%s AND fn_ID=%s', (scoreC, id_match, fn_ID))
        conn.commit()

conn.close
print ("OK!")
