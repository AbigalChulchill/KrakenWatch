#!/usr/bin/env python3

import asyncio
import json
import telegram
import time
import requests
import tweepy
from credentials import *
from datetime import datetime
from config import *

cross_chain_buyback_address = "0x3BB730E6f651007F2963B627C0D992CFC120a352"
async def main():
  avax_block = open('/home/pi/kraken_watch/avax_start_block.txt', 'r')
  avax_start_block = int(avax_block.read()) + 1

  print("Getting Kraken data from SnowTrace...")

  txns_request_url = "https://api.snowtrace.io/api?module=account&action=txlist&address=" + cross_chain_buyback_address + "&startblock=" + str(avax_start_block) + "&endblock=999999999&sort=asc&apikey=" + avax_api_key
  avax_txns = requests.get(txns_request_url)
  avax_txns_json = avax_txns.json()

  avax_txns_result = avax_txns_json["result"]

  print("Connecting to Telegram Bot...")
  try:
    bot = telegram.Bot(token='')
    print("Success!")
  except telegram.Error as e:
    print(f"Error connecting to Telegram: {e}")

  print("Connecting to Twitter...")
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth)
  print("Success!")

  current_time = datetime.utcnow()
  print("Current Time:        ",current_time)

  for item in avax_txns_result:
    if item['from'] == '0x3bb730e6f651007f2963b627c0d992cfc120a352':
      avax_kraken_found = 1
    else:
      avax_kraken_found = 0
    if avax_kraken_found == 1:
      txn_hash = item['hash']
      print("\nKraken Found!\nTransaction Hash=",txn_hash)
      internal_txns_url = "https://api.snowtrace.io/api?module=account&action=txlistinternal&txhash=" + txn_hash + "&apikey=" + avax_api_key
      avax_internal_txns = requests.get(internal_txns_url)
      avax_internal_txns_json = avax_internal_txns.json()
#      print(avax_internal_txns_json)
      avax_internal_txns_result = avax_internal_txns_json["result"]
      print(avax_internal_txns_result)
      avax_value = int(avax_internal_txns_result[0]['value'])/1000000000000000000
      avax_kaboom_datetime = datetime.utcfromtimestamp(int(item['timeStamp']))
      print('\nDate/Time of Kaboom: ',avax_kaboom_datetime)
      print('Block Number:        ',item['blockNumber'])
      print('AVAX Value:          ',avax_value)
      avax_start_block = item['blockNumber']
      file = open("/home/pi/kraken_watch/avax_start_block.txt", "w")
      file.write(avax_start_block)
      file.close()

      avax_message = "*AVAX Kraken Sighting:*\n*Date/Time of Kaboom:* " + str(avax_kaboom_datetime) + "\n*Block Number:*               " + str(item['blockNumber'])+ "\n*AVAX Value:*                   " + str(avax_value)
      bot.send_message(chat_id=CHAT_ID, text=avax_message, parse_mode=telegram.ParseMode.MARKDOWN)

      avax_message = "#EverRise $RISE\n\nAVAX Kraken Sighting:\n\nDate/Time of Kaboom: " + str(avax_kaboom_datetime) + "\nAVAX Block Number:          " + str(item['blockNumber']) + "\nAVAX Value:                     " + str(avax_value)
      api.update_status(status=avax_message)

if __name__ == "__main__":
  asyncio.run(main())
