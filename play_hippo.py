#!/usr/bin/env python3
#-*- cording: utf-8 -*-
import socket
import sys
import pygame
import pygame.mixer
import time
import random
import re
import mutagen.mp3
from queue import Queue
from threading import Thread
from pathlib import Path

PORT = 50000
VOLUME = 0.01

# アルバム一覧
CDlist = [
	"/home/pi/Music/hippo/sonoko/japanese/",
	"/home/pi/Music/hippo/sonoko/english/",
	"/home/pi/Music/hippo/sonoko/english/",
	"/home/pi/Music/hippo/sonoko/english/",
	"/home/pi/Music/hippo/sonoko/english/",
	"/home/pi/Music/hippo/sonoko/english/",
	"/home/pi/Music/hippo/sonoko/english/",
	"/home/pi/Music/hippo/sonoko/chinese/",
	"/home/pi/Music/hippo/sonoko/chinese/",
	"/home/pi/Music/hippo/sonoko/chinese/",
	"/home/pi/Music/hippo/sonoko/chinese/",
	"/home/pi/Music/hippo/sonoko/taiwan/",
	"/home/pi/Music/hippo/sonoko/taiwan/",
	"/home/pi/Music/hippo/sonoko/taiwan/",
	"/home/pi/Music/hippo/sonoko/russia/",
	"/home/pi/Music/hippo/sonoko/russia/",
	"/home/pi/Music/hippo/ichiro/chinese/",
	"/home/pi/Music/hippo/ichiro/chinese/",
	"/home/pi/Music/hippo/ichiro/chinese/",
	"/home/pi/Music/hippo/ichiro/chinese/",
	"/home/pi/Music/hippo/ichiro/english/",
	"/home/pi/Music/hippo/ichiro/english/",
	"/home/pi/Music/hippo/ichiro/english/",
	"/home/pi/Music/hippo/ichiro/english/",
	"/home/pi/Music/hippo/ichiro/english/",
	"/home/pi/Music/hippo/ichiro/english/",
	"/home/pi/Music/hippo/ichiro/japanese/",
	"/home/pi/Music/hippo/ichiro/russia/",
	"/home/pi/Music/hippo/ichiro/russia/",
	"/home/pi/Music/hippo/ichiro/russia/"
]

track_list = []

def play_next(CD_no, track_no):
	global track_list
	# 次の曲
	track_no+=1

	# CDの上限チェック
	if CD_no >= len(CDlist):
		# CDのシャッフル
		random.shuffle(CDlist)
		CD_no = 0
		track_no = 0

		# フォルダ検索。trackを昇順に並び替え
		with Path(CDlist[CD_no]) as p:
			track_list = sorted(p.glob("*.mp3"))

	# 次に再生するトラック番号
	if track_no >= len(track_list):
		track_no = 0
		CD_no +=1

		# CDの終わり。再度シャッフル
		if CD_no >= len(CDlist):
			random.shuffle(CDlist)
			CD_no = 0

		# フォルダ検索。trackを昇順に並び替え
		with Path(CDlist[CD_no]) as p:
			track_list = sorted(p.glob("*.mp3"))

	filename = str(track_list[track_no])
	print(filename)

	pygame.mixer.init()
	pygame.mixer.music.set_volume(VOLUME)

	# 音楽ファイルの読み込み
	pygame.mixer.music.load(filename)

	# 音楽再生、および再生回数の設定(-1:ループ再生、0:リピートなし)
	pygame.mixer.music.play(0)

	return CD_no, track_no

def player(qu):
	CD_no, track_no = play_next(len(CDlist), 0)

	while True:
		if qu.empty():
			cmd = "NONE"
		else:
			cmd = qu.get_nowait()
			print(cmd)

		if cmd == "STOP":
			pygame.mixer.music.pause()
		elif cmd == "PLAY":
			pygame.mixer.music.unpause()
		elif cmd == "NEXT":
			pygame.mixer.music.stop()
		elif not pygame.mixer.music.get_busy():
			pygame.mixer.quit()
			CD_no, track_no = play_next(CD_no, track_no)
		else:
			pass

		time.sleep(0.5)


def main():
	# mixerモジュールの初期化
	pygame.init()

	qu = Queue()
	thread = Thread(target=player, args=(qu,))
	thread.setDaemon(True)
	thread.start()

	# コントローラからの受付
	# クライアント設定
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	client.bind(("", PORT))

	while True:
		# コマンド待ち
		cmd, addr = client.recvfrom(128)
		qu.put_nowait(cmd.decode('utf-8'))

	client.close()

#引数チェックを入れたいね
if __name__ == '__main__':
	args = sys.argv
	cmd_num = len(args)

	if cmd_num == 2:
		if args[1].replace(".", "").isdigit():
			VOLUME = float(args[1])

	main()
