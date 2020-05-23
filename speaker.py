#!/usr/bin/env python3
#-*- cording: utf-8 -*-
import socket
import sys
import time
import math

from threading import Thread
from aiy.leds import (Leds, Pattern, PrivacyLed, RgbLeds, Color)
from aiy.board import Board, Led

PORT = 50000

TargetList = [
	["192.168.68.127", PORT], #vk2 Voice Kit 2
	["192.168.68.128", PORT],
	["192.168.68.129", PORT], #zero3 ASUS (gray)
	["192.168.68.130", PORT], #zero2 MINI raspberry pi
	["192.168.68.131", PORT], #old raspberry pi
	["192.168.68.132", PORT]  #zero1 HUAWEI (white)
]

STOP_CMD = ["停止", "停止して", "とめて", "止めて", "うるさい", "とまれ", "止まれ"]
PLAY_CMD = ["再生", "再生して", "再開", "再開して", "プレイ"]
NEXT_CMD = ["次の曲", "次", "次へ"]

def button():
	with Leds() as leds:
		with Board() as board:
			st_play = True;
			while True:
				leds.pattern = Pattern.breathe(3000)
				if st_play :
					leds.update(Leds.rgb_pattern(Color.GREEN))
				else:
					leds.update(Leds.rgb_pattern(Color.BLUE))

				board.button.wait_for_press()
				if st_play :
					send_cmd("STOP")
					print("> STOP")
				else:
					send_cmd("PLAY")
					print("> PLAY")

				board.led.state = Led.ON
				board.button.wait_for_release()
				board.led.state = Led.OFF
				st_play = not st_play


def send_cmd(cmd):
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	for target in TargetList:
		client.sendto(cmd.encode(), (target[0], target[1]))

	client.close()


def main():
	thread = Thread(target=button)
	thread.setDaemon(True)
	thread.start()

	while True:
		cmd = input('> ')

		if cmd == "stop":
			send_cmd("STOP")
		elif cmd == "play":
			send_cmd("PLAY")
		elif cmd == "next":
			send_cmd("NEXT")
		else:
			pass


if __name__ == '__main__':
	args = sys.argv
	cmd_num = len(args)

	if cmd_num == 1:
		main()
	elif cmd_num == 2:
		send_cmd(args[1])
	else:
		pass
