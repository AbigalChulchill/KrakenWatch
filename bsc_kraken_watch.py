#!/usr/bin/env python3

import asyncio
import json
import telegram
import time
import tweepy
from credentials import *
from datetime import datetime
from bscscan import BscScan
from config import *

async def main():
  bsc_block = open('/home/pi/kraken_watch/bsc_start_block.txt', 'r')
  bsc_start_block = bsc_block.read()

  async with BscScan(BSC_API_KEY) as bsc_client:
    print("Getting Kraken data from BSCScan...")
    bsc_internal_txns = await bsc_client.get_internal_txs_by_address('0xC17c30e98541188614dF99239cABD40280810cA3',startblock=(int(bsc_start_block) + 1),endblock=999999999,sort="asc")
    print("Success!")

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

  for item in bsc_internal_txns:
    if item['from'] == '0xc17c30e98541188614df99239cabd40280810ca3':
      if item['to'] == '0x10ed43c718714eb63d5aa57b78b54704e256024e':
        bsc_kraken_found = 1
      else:
        bsc_kraken_found = 0
    else:
      bsc_kraken_found = 0
    if bsc_kraken_found == 1:
      bnb_value = int(item['value'])/1000000000000000000
      bsc_kaboom_datetime = datetime.utcfromtimestamp(int(item['timeStamp']))
      print('Date/Time of Kaboom: ',bsc_kaboom_datetime)
      print('Block Number:        ',item['blockNumber'])
      print('BNB Value:           ',bnb_value)
      bsc_start_block = item['blockNumber']

      file = open("/home/pi/kraken_watch/bsc_start_block.txt", "w")
      file.write(bsc_start_block)
      file.close()

      file = open("/home/pi/kraken_watch/bsc_block_numbers.txt", "a")
      file.write(item['blockNumber'])
      file.close()

      bsc_message = "#EverRise $RISE Kraken Sighting:\n\nDate/Time of Kaboom: " + str(bsc_kaboom_datetime) + "\nBlock Number:               " + str(item['blockNumber']) + "\nBNB Value:                     " + str(bnb_value)
      bot.send_message(chat_id=CHAT_ID, text=bsc_message)

      api.update_status(status=bsc_message)

#      time.sleep(5)

if __name__ == "__main__":
  asyncio.run(main())
