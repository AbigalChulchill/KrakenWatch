#!/usr/bin/env python3

import asyncio
import json
import telegram
import time
import tweepy
from credentials import *
from statistics import mean, stdev
from datetime import datetime
from bscscan import BscScan
from config import *

async def main():
  bsc_path = PATH + "bsc_averages_start.txt"
  bsc_block = open(bsc_path, "r")
  bsc_start_block = bsc_block.read()

  async with BscScan(BSC_API_KEY) as bsc_client:
    print("Getting Kraken data from BSCScan...")
    try:
      bsc_internal_txns = await bsc_client.get_internal_txs_by_address(CONTRACT_ADDRESS,startblock=(int(bsc_start_block) + 1),endblock=999999999,sort="asc")
      print("Success!")
    except:
      print("Error!")

    current_time = datetime.now()
    time_stamp = int(round(current_time.timestamp()))
#    print(time_stamp)
    print("Getting Kraken data from BSCScan...")
    bsc_block_number = await bsc_client.get_block_number_by_timestamp(time_stamp,"before")
#    print(bsc_block_number)
    if bsc_block_number == "Error! No closest block found":
      bsc_error = 1
    else:
      bsc_error = 0
    if bsc_error == 0:
      print("Success!")

    print("Current Time:     ",current_time)
    print("Time Stamp:       ",time_stamp)
    print("BSC Block Number: ",bsc_block_number)



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

      file = open(bsc_path, "w")
      file.write(bsc_start_block)
      file.close()


      file = open("/home/pi/kraken_watch/bsc_averages_blocks.txt", "a")
      file.write(item['blockNumber'])
      file.write("\n")
      file.close()


      file = open("/home/pi/kraken_watch/bsc_averages_timestamps.txt", "a")
      file.write(str(bsc_kaboom_datetime.timestamp()))
      file.write("\n")
      file.close()


  bsc_block = open('/home/pi/kraken_watch/bsc_averages_blocks.txt', 'r')
  bsc_kaboom_blocks = bsc_block.read().splitlines()
  bsc_kaboom_block_difference = [int(bsc_kaboom_blocks[i+1])-int(bsc_kaboom_blocks[i]) for i in range(len(bsc_kaboom_blocks)-1)]
  bsc_block_average = int(mean(bsc_kaboom_block_difference))
  bsc_block_standard_deviation = stdev(bsc_kaboom_block_difference)
  bsc_block_minimum = bsc_block_average - bsc_block_standard_deviation
  bsc_block_maximum = bsc_block_average + bsc_block_standard_deviation

  bsc_timestamp = open('/home/pi/kraken_watch/bsc_averages_timestamps.txt', 'r')
  bsc_kaboom_timestamps = bsc_timestamp.read().splitlines()
  bsc_kaboom_timestamp_difference = [float(bsc_kaboom_timestamps[i+1])-float(bsc_kaboom_timestamps[i]) for i in range(len(bsc_kaboom_timestamps)-1)]
  bsc_timestamp_average = int(mean(bsc_kaboom_timestamp_difference)/60)
  print("Average Minutes Between Kabooms:   ",round(bsc_timestamp_average,2))
  print("BSC Block Average Between Kabooms: ",round(bsc_block_average,1))
  print("BSC Block Standard Deviation:      ",round(bsc_block_standard_deviation,1))

  bsc_block_hourly = open("/home/pi/kraken_watch/bsc_block_hourly.txt", "r")
  bsc_block_hourly_previous = bsc_block_hourly.readline()
  print("Previous BSC Block:                ",bsc_block_hourly_previous)

  bsc_block_delta = (int(bsc_block_number) - int(bsc_block_hourly_previous))
  print("BSC Block Delta:                   ",bsc_block_delta)

  bsc_timestamp_hourly = open('/home/pi/kraken_watch/bsc_timestamp_hourly.txt', 'r')
  bsc_timestamp_hourly_previous = bsc_timestamp_hourly.readline()
  print("Previous BSC Timestamp:            ",bsc_timestamp_hourly_previous)

  bsc_timestamp_delta = (int(time_stamp) - int(bsc_timestamp_hourly_previous))/60
  print("BSC Timestamp Delta:               ", bsc_timestamp_delta)

  bsc_block_rate = int((bsc_block_delta/bsc_timestamp_delta)*60)
  print("BSC Block Rate:                    ",bsc_block_rate)

  bsc_time_standard_deviation = int(bsc_block_standard_deviation) / int(bsc_block_rate)

  file = open('/home/pi/kraken_watch/bsc_block_hourly.txt', 'w')
  file.write(bsc_block_number)
  file.close()

  file = open('/home/pi/kraken_watch/bsc_timestamp_hourly.txt', 'w')
  file.write(str(time_stamp))
  file.close()

  bsc_blocks_elapsed = int(bsc_block_number) - int(bsc_start_block)
  bsc_blocks_left = int(bsc_block_average) - int(bsc_blocks_elapsed)
  hours_until_kaboom , blocks_until_kaboom = divmod(int(bsc_blocks_left),int(bsc_block_rate))
  minutes_until_kaboom = round(int(blocks_until_kaboom)/int(bsc_block_rate)*60)
  time_until_kaboom = str(hours_until_kaboom) + ":" + str(minutes_until_kaboom).zfill(2)

  print("Time Until Next Kaboom:            ",time_until_kaboom)

  bsc_message = "\n*Average BSC Blocks Per Kaboom:*     " + str(round(bsc_block_average,1)) + "\n*BSC Blocks Since Last Kaboom:*        " + str(bsc_blocks_elapsed) + "\n*BSC Blocks Left:*                                    " + str(bsc_blocks_left) + "\n*BSC Blocks Per Hour:*                           " + str(bsc_block_rate) + "\n*Hours Until Next Kaboom:*                  " + str(time_until_kaboom)
#  bsc_message = "*Previous Kraken Block Number:* " + str(bsc_start_block) + "\n*Current BSC Block Number:*        " + str(bsc_block_number) + "\n*BSC Blocks Elapsed:*                             " + str(bsc_blocks_elapsed) + "\n*Average BSC Blocks Per Kaboom:*       " + str(round(bsc_block_average,1)) + "\n*BSC Blocks Per Hour:*                               " + str(bsc_block_rate) + "\n*Average Minutes Between Kabooms:*    " + str(bsc_timestamp_average)
  bot.send_message(chat_id=CHAT_ID, text=bsc_message, parse_mode=telegram.ParseMode.MARKDOWN)

  bsc_message = "#EverRise $RISE\n\nAverage BSC Blocks Per Kaboom:     " + str(round(bsc_block_average,1)) + "\nBSC Blocks Since Last Kaboom:        " + str(bsc_blocks_elapsed) + "\nBSC Blocks Left:                                   " + str(bsc_blocks_left) + "\nBSC Blocks Per Hour:                           " + str(bsc_block_rate) + "\nHours Until Next Kaboom:                   " + str(time_until_kaboom)
#  bsc_message = "#EverRise $RISE\n\nPrevious Kraken Block Number: " + str(bsc_start_block) + "\nCurrent BSC Block Number:        " + str(bsc_block_number) + "\nBSC Blocks Elapsed:                          " + str(bsc_blocks_elapsed) + "\nAverage BSC Blocks Per Kaboom:      " + str(round(bsc_block_average,1)) + "\nBSC Blocks Per Hour:                           " + str(bsc_block_rate) +  "\nAverage Minutes Between Kabooms:   " + str(bsc_timestamp_average)
  api.update_status(status=bsc_message)




if __name__ == "__main__":
  asyncio.run(main())
