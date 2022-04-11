#!/usr/bin/env python3

import asyncio
import json
import telegram
import time
import tweepy
from credentials import *
from statistics import mean
from datetime import datetime
from bscscan import BscScan
from config import *

async def main():
  bsc_block = open('/home/pi/kraken_watch/bsc_kaboom_blocks_start.txt', 'r')
  bsc_start_block = bsc_block.read()

  async with BscScan(BSC_API_KEY) as bsc_client:
    print("Getting Kraken data from BSCScan...")
    bsc_internal_txns = await bsc_client.get_internal_txs_by_address('0xC17c30e98541188614dF99239cABD40280810cA3',startblock=(int(bsc_start_block) + 1),endblock=999999999,sort="asc")
    print("Success!")

  print("Connecting to Telegram Bot...")
  try:
    bot = telegram.Bot(token='TELEGRAM API TOKEN')
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
      bsc_start_block = item['blockNumber']

      bsc_kaboom_datetime = datetime.utcfromtimestamp(int(item['timeStamp']))

      file = open("/home/pi/kraken_watch/bsc_kaboom_blocks_start.txt", "w")
      file.write(bsc_start_block)
      file.close()

      file = open("/home/pi/kraken_watch/bsc_kaboom_blocks.txt", "a")
      file.write(item['blockNumber'])
      file.write("\n")
      file.close()

  bsc_block = open('/home/pi/kraken_watch/bsc_kaboom_blocks.txt', 'r')
  bsc_kaboom_blocks = bsc_block.read().splitlines()

  bsc_kaboom_block_difference = [int(bsc_kaboom_blocks[i+1])-int(bsc_kaboom_blocks[i]) for i in range(len(bsc_kaboom_blocks)-1)]

  bsc_block_average = mean(bsc_kaboom_block_difference)
  print("BSC Block Average Between Kabooms: ",round(bsc_block_average,2))


  bsc_message = "Average BSC Blocks Per Kaboom: " + str(round(bsc_block_average,1))

  bot.send_message(chat_id=CHAT_ID, text=bsc_message)

  bsc_message = "#EverRise $RISE\n\nAverage BSC Blocks Per Kaboom: " + str(round(bsc_block_average,1))

  api.update_status(status=bsc_message)


if __name__ == "__main__":
  asyncio.run(main())
