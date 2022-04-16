#!/usr/bin/env python3

import asyncio
import json
import telegram
import time
import tweepy
from credentials import *
from datetime import datetime
from etherscan import Etherscan
from config import *

async def main():
  eth_path = PATH + "eth_start_block.txt"
  eth_block = open(eth_path, "r")
  eth_start_block = eth_block.read()

  print("Getting Kraken data from EtherScan...")
  eth_client = Etherscan(ETH_API_KEY)
  eth_internal_txns = eth_client.get_internal_txs_by_address(CONTRACT_ADDRESS,startblock=(int(eth_start_block) + 1),endblock=999999999,sort="asc")
  print("Success!")

  print("Connecting to Telegram Bot...")
  try:
    bot = telegram.Bot(token=TELEGRAM_API_KEY)
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

  for item in eth_internal_txns:
    if item['from'] == '0xc17c30e98541188614df99239cabd40280810ca3':
      if item['to'] == '0x7a250d5630b4cf539739df2c5dacb4c659f2488d':
        eth_kraken_found = 1
      else:
        eth_kraken_found = 0
    else:
      eth_kraken_found = 0
    if eth_kraken_found == 1:
      eth_value = int(item['value'])/1000000000000000000
      eth_kaboom_datetime = datetime.utcfromtimestamp(int(item['timeStamp']))
      print("Date/Time of Kaboom: ",eth_kaboom_datetime)
      print("Block Number:        ",item['blockNumber'])
      print("ETH Value:           ",eth_value)
      eth_start_block = item['blockNumber']

      file = open(eth_path, "w")
      file.write(eth_start_block)
      file.close()

      eth_message = "*ETH Kraken Sighting:*\n*Date/Time of Kaboom:* " + str(eth_kaboom_datetime) + "\n*Block Number:*               " + str(item['blockNumber']) + "\n*ETH Value:*                      " + str(eth_value)
      bot.send_message(chat_id=CHAT_ID, text=eth_message, parse_mode=telegram.ParseMode.MARKDOWN)

      eth_message = "#EverRise $RISE\n\nETH Kraken Sighting:\n\nDate/Time of Kaboom: " + str(eth_kaboom_datetime) + "\nETH Block Number:        " + str(item['blockNumber']) + "\nETH Value:                      " + str(eth_value)
      api.update_status(status=eth_message)


if __name__ == "__main__":
  asyncio.run(main())
