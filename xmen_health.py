# coding=utf-8
import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')
import requests, json, urllib,time
import MySQLdb
import os
import mysql.connector
from mysql.connector import Error
from ldap_get import ldap_get
from datetime import datetime

now = datetime.now()
sekarang = now.strftime("%Y-%m-%d %H:%M:%S")
db = MySQLdb.connect(host="localhost",user="root",passwd="mousehunt",db="xmen_healthy_bot")

cur = db.cursor()
#bot xmen healthy
bot = '1291494347:AAGR1dR7LOnPUIwMVhV3oZ_tCO6U8JhRQmE'

r = requests.get('https://api.telegram.org/bot%s/getupdates?timeout=30' %bot)
jsondata = r.content

pesan = ""
data = json.loads(jsondata)

for x in data['result']:
  print "\n"
  try:
    update_id = x['update_id']
  except KeyError:
    print 'No Update'
  else:
    requests.get('https://api.telegram.org/bot%s/getupdates?offset=%s' %(bot,(update_id + 1)), proxies=urllib.getproxies())
  #print(x)
  if 'callback_query' in x:
        chat_id = x['callback_query']['from']['id']
        callback = x['callback_query']['data']
        if callback == 'register':
                pesan = "Input your domain username"
                requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=HTML&reply_markup={"force_reply":true}' %(bot,chat_id,pesan), proxies=urllib.getproxies())
        elif callback == 'report':
                pesan = "Please input your zone status"
                requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=HTML&reply_markup={"inline_keyboard":[[{"text":"Green Zone","callback_data":"green"},{"text":"Yellow Zone","callback_data":"yellow"},{"text":"Red Zone","callback_data":"red"},{"text":"Black Zone","callback_data":"black"}]]}' %(bot,chat_id,pesan), proxies=urllib.getproxies())
        elif (callback == 'green') or (callback == 'yellow') or (callback == 'red') or (callback == 'black'):
                cur.execute("INSERT INTO healthy_log (`chat_id`,`zone`,`datetime`)values ('"+str(chat_id)+"','"+str(callback)+"','"+str(sekarang)+"')")
                db.commit()
                pesan = "Please input your health status"
                requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=HTML&reply_markup={"inline_keyboard":[[{"text":"Healthy","callback_data":"healthy"},{"text":"Minor Sick","callback_data":"minor sick"},{"text":"Sick","callback_data":"sick"}]]}' %(bot,chat_id,pesan), proxies=urllib.getproxies())
        elif (callback == 'healthy') or (callback == 'sick') or (callback == 'minor sick'):
                cur.execute("SELECT indeks from healthy_log WHERE chat_id = '"+str(chat_id)+"' ORDER BY indeks DESC ")
                indeks = cur.fetchone()
                print(indeks)
                cur.execute("UPDATE healthy_log set `health` = '"+str(callback)+"' where indeks = '"+str(indeks[0])+"'")
                db.commit()
                cur.execute("SELECT name,healthy_log.* from healthy_log,user_reg WHERE healthy_log.chat_id = '"+str(chat_id)+"' and `healthy_log`.`chat_id` = `user_reg`.`chat_id` ORDER BY indeks DESC ")
                data = cur.fetchone()
                pesan = "Thank you, your status has been saved" + "\n" + "Name : " +str(data[0])+ "\n" + "Zone : " +str(data[3])+"\n" + "Status : " +str(data[4])
                requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=HTML' %(bot,chat_id,pesan), proxies=urllib.getproxies())
                pesan = "See you next week "+str(data[0])+"\n"+"Stay Safe and Keep Healthy"+ "\n"+ "Just click Report to report your status"
                #requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=HTML&reply_markup={"inline_keyboard":[[{"text":"Report My Status","callback_data":"report"}]]}' %(bot,chat_id,pesan), proxies=urllib.getproxies())


  elif 'message' in x:
        number = x['message']['text']
        chat_id = x['message']['from']['id']
        cur.execute("SELECT name FROM user_reg WHERE `chat_id` = '{0}'".format(chat_id))
        reg = cur.fetchall()

        first_name = x['message']['from']['first_name']
        if number ==  '/start':
                first_name = x['message']['from']['first_name']
                try:
                        pesan = 'Hello <strong>%s</strong>' %reg[0] + "\n" + "Please click Report to report your status"
                        requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=HTML&reply_markup={"inline_keyboard":[[{"text":"Report My Status","callback_data":"report"}]]}' %(bot,chat_id,pesan), proxies=urllib.getproxies())

                except IndexError:
                        pesan = 'Hello <strong>%s</strong>' %first_name + "\n" +"your chat id is not registered yet, please click register below"
                        requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=HTML&reply_markup={"inline_keyboard":[[{"text":"Register","callback_data":"register"}]]}' %(bot,chat_id,pesan), proxies=urllib.getproxies())

        if 'reply_to_message' in x['message']:
                if x['message']['reply_to_message']['text'] == 'Input your domain username':
                        username = x['message']['text']
                        try:
                                ldap = ldap_get(username)
                                dept = ldap.dept
                                nama_ldap = ldap.name
                                cur.execute("INSERT INTO user_reg (`chat_id`,`user_domain`,`datetime`,`name`,`dept`,`status`)values ('"+str(chat_id)+"','"+str(username)+"','"+str(sekarang)+"','"+str(nama_ldap[0])+"','"+str(dept[0])+"','active')")
                                db.commit()
                                pesan = 'Your username '+ username + " is sucessfully registered, please click Report to report your status"
                                requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=HTML&reply_markup={"inline_keyboard":[[{"text":"Report My Status","callback_data":"report"}]]}' %(bot,chat_id,pesan), proxies=urllib.getproxies())

                        except IndexError:
                                pesan = 'Your username '+ username + " is not found, click register to re-input username"
                                requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s&parse_mode=HTML&reply_markup={"inline_keyboard":[[{"text":"Register","callback_data":"register"}]]}' %(bot,chat_id,pesan), proxies=urllib.getproxies())

