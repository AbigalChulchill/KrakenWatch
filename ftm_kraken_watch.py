#!/usr/bin/env python3

import asyncio
import json
import telegram
import time
import tweepy
from credentials import *
from datetime import datetime
from ftmscan import ftmScan
from config import *

async def main():
  ftm_block = open('/home/pi/kraken_watch/ftm_start_block.txt', 'r')
  ftm_start_block = ftm_block.read()

  print("Getting Kraken data from FTMScan...")
  with ftmScan(FTM_API_KEY,False) as ftm_client:
    ftm_txns = ftm_client.get_normal_txs_by_address('0x3BB730E6f651007F2963B627C0D992CFC120a352',startblock=(int(ftm_start_block) + 1),endblock=999999999,sort="asc")
#    print(ftm_txns)

  print("Connecting to Telegram Bot...")
  try:
    bot = telegram.Bot(token='5196129266:AAE4O7naJ5rj6ewu_FnSByipQWswbAPmvxA')
    print("Success!")
  except telegram.Error as e:
    print(f"Error connecting to Telegram: {e}")

  print("Connecting to Twitter...")
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth)
  print("Success!")

  current_time = datetime.utcnow()
  print('Current Time:        ',current_time)

  for item in ftm_txns:
    if item['from'] == '0x3bb730e6f651007f2963b627c0d992cfc120a352':
      ftm_kraken_found = 1
    else:
      ftm_kraken_found = 0
    if ftm_kraken_found == 1:
#      ftm_value = int(item['value'])/1000000000000000000
      ftm_internal_txn = ftm_client.get_internal_txs_by_txhash(item['hash'])
#      print(ftm_internal_txn)
      ftm_value = int(ftm_internal_txn[1]['value'])/1000000000000000000

      ftm_kaboom_datetime = datetime.utcfromtimestamp(int(item['timeStamp']))
      print('Date/Time of Kaboom: ',ftm_kaboom_datetime)
      print('Block Number:        ',item['blockNumber'])
      print('FTM Value:          ',ftm_value)
      ftm_start_block = item['blockNumber']
      file = open("/home/pi/kraken_watch/ftm_start_block.txt", "w")
      file.write(ftm_start_block)
      file.close()
      ftm_message = "*FTM Kraken Sighting:*\n*Date/Time of Kaboom:* " + str(ftm_kaboom_datetime) + "\n*Block Number:*               " + str(item['blockNumber']) + "\n*FTM Value:*                       " + str(ftm_value)
      bot.send_message(chat_id=CHAT_ID, text=ftm_message, parse_mode=telegram.ParseMode.MARKDOWN)

      ftm_message = "#EverRise $RISE\n\nFTM Kraken Sighting:\n\nDate/Time of Kaboom: " + str(ftm_kaboom_datetime) + "\nFTM Block Number:           " + str(item['blockNumber']) + "\nFTM Value:                     " + str(ftm_value)
      api.update_status(status=ftm_message)

if __name__ == "__main__":
  asyncio.run(main())
