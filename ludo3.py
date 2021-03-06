try:
	import tkinter as tk
except:
	import Tkinter as tk
import time
import random
import cv2
import os
from PIL import Image, ImageTk
import numpy as np


canvas = None

class Params:
	def __init__(self):
		self.base_dir = os.getcwd()
		self.current = None
		self.canvas_width = 800
		self.canvas_height = 600
		self.cell_size = 35
		self.cells_for_player = 6
		self.marginX = 25
		self.marginY = 25
		self.images = {"small":[None, None, None, None], "middle":[None, None, None, None], "big":[None, None, None, None]}
		self.image_names = ["redPieceAlpha.png", "greenPieceAlpha.png", "bluePieceAlpha.png", "yellowPieceAlpha.png"]
		self.player_expand = np.zeros((4, 4, 2), dtype = np.float32)
		self.player_compress = np.zeros((4, 4, 2), dtype = np.float32)
		self.pieces = np.zeros((4, 4), dtype = np.uint16)
		self.player_pos = np.zeros((4, 2), dtype = np.uint16)
		self.win = np.zeros((4, 4), dtype = np.uint16)
		self.piece_size = np.zeros((4, 4), dtype = np.uint16) #0]big size    #1]middle size    #2]small size
		self.piece_multiples = np.zeros((4, 4), dtype = np.uint16) #0]Single    #1]Multipes
		self.piece_pos_in_path = np.zeros((4, 4), dtype = np.uint16)
		image = Image.open(os.path.join(self.base_dir, "images", self.image_names[0]))
		self.ratio = image.size[1]/image.size[0]
		self.path = np.zeros((self.cells_for_player * 8 + 4, 2), dtype = np.uint16)
		self.win = np.zeros((4, self.cells_for_player - 1, 2), dtype = np.uint16)
		self.set_path()
		self.change = None
		self.testing = False
		self.path_out = np.asarray([
			1,
			2 + self.cells_for_player * 2,
			3 + self.cells_for_player * 4,
			4 + self.cells_for_player * 6
		], dtype = np.uint16)
		self.path_safe = np.asarray([
			1 + self.cells_for_player,
			2 + self.cells_for_player * 3,
			3 + self.cells_for_player * 5,
			4 + self.cells_for_player * 7
		], dtype = np.uint16)
		self.set_position()
		self.debug = False#True
		if self.debug:
			self.dice_roll = 1
		else:
			self.dice_roll = -1
		self.debug_roll = [int(int(random.random()*1000) % 6) for i in range(50)]
		if 6 not in self.debug_roll:
			self.debug_roll = [int(random.random()*1000 % 6) for i in range(50)]
		self.roll_id = 0
		self.dice_pos = 0
		self.active = None
		self.double = False
		self.auto = False
		self.record_file = None
	
	def set_path(self):
		j = 0
		for i in range(self.cells_for_player):
			self.path[j][0] = self.marginX + i * self.cell_size
			self.path[j][1] = self.marginY + self.cells_for_player * self.cell_size
			j += 1
		#print(self.path[0 : self.cells_for_player])
		for i in range(self.cells_for_player - 1, -1, -1):
			self.path[j][0] = self.marginX + self.cells_for_player * self.cell_size
			self.path[j][1] = self.marginY + i * self.cell_size
			j += 1
		#print(self.path[self.cells_for_player : self.cells_for_player * 2])
		self.path[j][0] = self.marginX + (self.cells_for_player + 1) * self.cell_size
		self.path[j][1] = self.marginY
		j += 1
		#print(self.path[self.cells_for_player * 2: self.cells_for_player * 2 + 1])
		
		for i in range(self.cells_for_player):
			self.path[j][0] = self.marginX + (self.cells_for_player + 2) * self.cell_size
			self.path[j][1] = self.marginY + i * self.cell_size
			j += 1
		#print(self.path[self.cells_for_player * 2 + 1: self.cells_for_player * 3 + 1])
		for i in range(self.cells_for_player + 3, self.cells_for_player * 2 + 3):
			self.path[j][0] = self.marginX + i * self.cell_size
			self.path[j][1] = self.marginY + self.cells_for_player * self.cell_size
			j += 1
		#print(self.path[self.cells_for_player * 3 + 1: self.cells_for_player * 4 + 1])
		self.path[j][0] = self.marginX + (self.cells_for_player * 2 + 2) * self.cell_size
		self.path[j][1] = self.marginY + (self.cells_for_player + 1) * self.cell_size
		j += 1
		#print(self.path[self.cells_for_player * 4 + 1: self.cells_for_player * 4 + 2])
		
		for i in range(self.cells_for_player * 2 + 2, self.cells_for_player + 2, -1):
			self.path[j][0] = self.marginX + i * self.cell_size
			self.path[j][1] = self.marginY + (self.cells_for_player + 2) * self.cell_size
			j += 1
		#print(self.path[self.cells_for_player * 4 + 2: self.cells_for_player * 5 + 2])
		for i in range(self.cells_for_player + 3, self.cells_for_player * 2 + 3):
			self.path[j][0] = self.marginX + (self.cells_for_player + 2) * self.cell_size
			self.path[j][1] = self.marginY + i * self.cell_size
			j += 1
		#print(self.path[self.cells_for_player * 5 + 2: self.cells_for_player * 6 + 2])
		self.path[j][0] = self.marginX + (self.cells_for_player + 1) * self.cell_size
		self.path[j][1] = self.marginY + (self.cells_for_player * 2 + 2) * self.cell_size
		j += 1
		#print(self.path[self.cells_for_player * 6 + 2: self.cells_for_player * 6 + 3])
		
		for i in range(self.cells_for_player * 2 + 2, self.cells_for_player + 2, -1):
			self.path[j][0] = self.marginX + self.cells_for_player * self.cell_size
			self.path[j][1] = self.marginY + i * self.cell_size
			j += 1
		#print(self.path[self.cells_for_player * 6 + 3: self.cells_for_player * 7 + 3])
		for i in range(self.cells_for_player -1, -1, -1):
			self.path[j][0] = self.marginX + i * self.cell_size
			self.path[j][1] = self.marginY + (self.cells_for_player + 2) * self.cell_size
			j += 1
		#print(self.path[self.cells_for_player * 7 + 3: self.cells_for_player * 8 + 3])
		self.path[j][0] = self.marginX
		self.path[j][1] = self.marginY + (self.cells_for_player + 1) * self.cell_size
		j += 1
		#print(self.path[self.cells_for_player * 8 + 3: self.cells_for_player * 8 + 4])
		
		for i in range(self.cells_for_player - 1):
			self.win[0][i][0] = self.marginX + (i + 1) * self.cell_size
			self.win[0][i][1] = self.marginY + (self.cells_for_player +1) * self.cell_size
		for i in range(self.cells_for_player - 1):
			self.win[1][i][0] = self.marginX + (self.cells_for_player + 1) * self.cell_size
			self.win[1][i][1] = self.marginY + (i + 1) * self.cell_size
		for i in range(self.cells_for_player - 1):
			self.win[2][i][0] = self.marginX + (i + self.cells_for_player + 3) * self.cell_size
			self.win[2][i][1] = self.marginY + (self.cells_for_player + 1) * self.cell_size
		for i in range(self.cells_for_player - 1):
			self.win[3][i][0] = self.marginX + (self.cells_for_player + 1) * self.cell_size
			self.win[3][i][1] = self.marginY + (i + self.cells_for_player + 3)	 * self.cell_size
	
	def set_position(self):
		  #position of piece in cell w.r.t to left top coerner pos of cell
		self.piece_pos = [
			np.asarray([
				[self.cell_size * 0.5, self.cell_size * (0.5  - self.ratio * 0.15)]
			]),
			
			np.asarray([
				[self.cell_size * 0.30, self.cell_size * (0.50  - self.ratio * 0.20)],
				[self.cell_size * 0.65, self.cell_size * (0.50  - self.ratio * 0.05)]
			]),
		
			np.asarray([
				[self.cell_size * 0.30, self.cell_size * (0.50  - self.ratio * 0.20)],
				[self.cell_size * 0.70, self.cell_size * (0.50  - self.ratio * 0.20)],
				[self.cell_size * 0.50, self.cell_size * (0.50  - self.ratio * 0.01)]
			]),
		
			np.asarray([
				[self.cell_size * 0.25, self.cell_size * (0.50  - self.ratio * 0.20)],
				[self.cell_size * 0.60, self.cell_size * (0.50  - self.ratio * 0.20)],
				[self.cell_size * 0.40, self.cell_size * (0.50  - self.ratio * 0.01)],
				[self.cell_size * 0.75, self.cell_size * (0.50  - self.ratio * 0.01)]
			]),
		
			np.asarray([
				[self.cell_size * 0.35, self.cell_size * (0.50  - self.ratio * 0.25)],
				[self.cell_size * 0.70, self.cell_size * (0.50  - self.ratio * 0.25)],
				[self.cell_size * 0.20, self.cell_size * (0.50  - self.ratio * 0.01)],
				[self.cell_size * 0.80, self.cell_size * (0.50  - self.ratio * 0.01)],
				[self.cell_size * 0.50, self.cell_size * (0.80  - self.ratio * 0.10)]
			]),
		
			np.asarray([
				[self.cell_size * 0.30, self.cell_size * (0.50  - self.ratio * 0.25)],
				[self.cell_size * 0.75, self.cell_size * (0.50  - self.ratio * 0.25)],
				[self.cell_size * 0.50, self.cell_size * (0.50  - self.ratio * 0.12)],
				[self.cell_size * 0.20, self.cell_size * (0.50  - self.ratio * 0.01)],
				[self.cell_size * 0.80, self.cell_size * (0.50  - self.ratio * 0.01)],
				[self.cell_size * 0.50, self.cell_size * (0.80  - self.ratio * 0.10)]
			])
		]
		self.id = 0
	
	def setImages(self, canvas):
		#print(canvas)
		canvas.images = {"small":[None, None, None, None], "middle":[None, None, None, None], "big":[None, None, None, None]}
		for i in range(len(self.image_names)):
			image = Image.open(os.path.join(self.base_dir, "images", self.image_names[i]))
			#print(image.size[1] / image.size[0])
			#self.ratio[i] = image.size[1] / image.size[0]
			
			sx = self.cell_size * 0.4
			sy = sx * image.size[1] / image.size[0]
			img = image.resize((int(sx), int(sy)), Image.ANTIALIAS)
			im = ImageTk.PhotoImage(img)
			self.images["small"][i] = im
			canvas.images["small"][i] = im
			
			mx = self.cell_size * 0.8
			my = mx * image.size[1] / image.size[0]
			img = image.resize((int(mx), int(my)), Image.ANTIALIAS)
			im = ImageTk.PhotoImage(img)
			self.images["middle"][i] = im
			canvas.images["middle"][i] = im
			
			hx = self.cell_size * 1.1
			hy = hx * image.size[1] / image.size[0]
			img = image.resize((int(hx), int(hy)), Image.ANTIALIAS)
			im = ImageTk.PhotoImage(img)
			self.images["big"][i] = im
			canvas.images["big"][i] = im
	
	def print_debug_entry_path(self, *info):
		if self.debug:
			print(" >>> ", end="")
			print(*info)
	
	def change(self):
		self.change()

			
class Board:
	def __init__(self, dx, dy):
		params.print_debug_entry_path("Board in __init__ !")
		self.dx = dx
		self.dy = dy
		#self.trail()
		self.set_board()
		self.player_pos = [
		[params.marginX, params.marginY],
		[params.marginX + (params.cells_for_player + 3) * params.cell_size, params.marginY],
		[params.marginX + (params.cells_for_player + 3) * params.cell_size, params.marginY + (params.cells_for_player + 3) * params.cell_size],
		[params.marginX, params.marginY + (params.cells_for_player + 3) * params.cell_size]
		]
		self.players = [
			Player(0, self.player_pos[0][0], self.player_pos[0][1], "#ff0000"),
			Player(1, self.player_pos[1][0], self.player_pos[1][1], "#00ff00"),
			Player(2, self.player_pos[2][0], self.player_pos[2][1], "#0000ff"),
			Player(3, self.player_pos[3][0], self.player_pos[3][1], "#ffff00")
		]
		self.dice = Dice(params.marginX, params.marginY)
		canvas.bind("<Return>", self.enterEvent)
		canvas.bind("<Key>", self.keyEvent)
		self.dice_pos = 0
		params.dice_pos = 0
		self.players[self.dice_pos].expand()
		params.change = self.change
		#print(self.change)
		params.print_debug_entry_path("Board out off __init__ !")
	
	def keyEvent(self, event):
		self.checkKey(event.char)
	
	def checkKey(self, key):
		params.print_debug_entry_path("")
		params.print_debug_entry_path("")
		params.print_debug_entry_path("Board in keyEvent !")
		params.print_debug_entry_path("player "+str(self.dice_pos) + " == >> ")
		#print(event.char)
		#print(event.keycode)
		#print(event.char == 'r')
		#print(event.char == 'n')
		if key == "r":
			self.dice.roll_the_dice()
			if params.dice_roll == 5:
				params.double = True
			rt = self.players[self.dice_pos].check_for_active()
			#print(rt)
			if rt[0] == "not ok":
				#print(time.time())
				#time.sleep(1)
				#print(time.time())
				canvas.after(500, params.change)
			elif rt[0] == "ok" and not rt[1] == None:
				#print("Only on out!")
				#print("pid : ", params.dice_pos, " pcid or rt[1] : ", rt[1])
				#print("in the home or rt[2]", rt[2])
				if not (rt[2] > 0 and params.dice_roll == 5):
					canvas.addtag_withtag("myCurrentTag", params.pieces[params.dice_pos][rt[1]])
					#print(canvas.gettags("!"))
					#print("0:0:", canvas.gettags(params.pieces[params.dice_pos][rt[1]]))
					#canvas.dtag(params.pieces[params.dice_pos][rt[1]], "!")
					#print("1:1:", canvas.gettags(params.pieces[params.dice_pos][rt[1]]))
					params.active = rt[1]
					canvas.after(500, self.players[params.dice_pos].makeMove, "myCurrentTag")
			elif rt[0] == "keep" and params.auto:
				#print("dice6 and inHome! :", rt)
				choice = random.choice(rt[3])
				#print(choice)
				canvas.addtag_withtag("myCurrentTag", params.pieces[params.dice_pos][choice])
				params.active  = choice
				canvas.after(500, self.players[params.dice_pos].makeMove, "myCurrentTag")
			elif rt[0] == "change":
				#print("inside the chnage!")
				canvas.addtag_withtag("myCurrentTag", params.pieces[params.dice_pos][rt[1]])
				params.active  = rt[1]
				canvas.after(500, self.players[params.dice_pos].makeMove, "myCurrentTag")
			#print("only one out end !")
			
		elif key == 'n' and params.debug:
			self.change()
		"""
		if event.keycode == 37:
			print("Left key!")
		elif event.keycode == 38:
			print("Up key!")
		elif event.keycode == 39:
			print("Right key!")
		elif event.keycode == 40:
			print("Down key!")
		"""
		params.print_debug_entry_path("Board out off keyEvent !")
	
	def change(self):
		params.print_debug_entry_path("Board in change !")
		if not params.active == None:
			canvas.dtag("myCurrentTag", "myCurrentTag")
			params.active = None
		if params.double:
			self.dice.move(self.player_pos[self.dice_pos][0], self.player_pos[self.dice_pos][1])
			params.double = False
			#print("Got second Chance! LUCKKY!")
			if params.auto:
				self.checkKey("r")
			return
		self.players[self.dice_pos].compress()
		self.dice_pos = int((self.dice_pos + 1) % 4)
		params.dice_pos = int((params.dice_pos + 1) % 4)
		self.dice.move(self.player_pos[self.dice_pos][0], self.player_pos[self.dice_pos][1])
		self.players[self.dice_pos].expand()
		if params.auto:
			canvas.after(40, self.checkKey, "r")
		params.print_debug_entry_path("Board out off change !")
	
	def enterEvent(self, event):
		params.print_debug_entry_path("Board in enterEvent !")
		pass
		params.print_debug_entry_path("Board out off enterEvent !")
	
	def set_board(self):
		params.print_debug_entry_path("Board in set_board !")
		f = params.cell_size * (params.cells_for_player * 2 + 3)
		cs = params.cell_size
		cfp = params.cells_for_player
		cfp2 = cfp * 2
		cfp2_1 = cfp2 + 1
		cfp2_2 = cfp2 + 2
		cfp2_3 = cfp2 + 3
		cfp_1 = cfp + 1
		cfp_2 = cfp + 2
		cfp_3 = cfp + 3
		cfp_4 = cfp + 4
		self.board = [
			canvas.create_rectangle(self.dx, self.dy, self.dx + f, self.dy + f, fill="#00ffff", width = 2),
			canvas.create_rectangle(self.dx, self.dy, self.dx + cs * cfp, self.dy + cs * cfp, fill="#ff0000", width = 2),
			canvas.create_rectangle(self.dx + cfp_3 * cs, self.dy, self.dx + cs * cfp2_3, self.dy + cs * cfp, fill="#00ff00", width = 2),
			canvas.create_rectangle(self.dx + cfp_3 * cs, self.dy + cfp_3 * cs, self.dx + cs * cfp2_3, self.dy + cs * cfp2_3, fill="#0000ff", width = 2),
			canvas.create_rectangle(self.dx, self.dy + cfp_3 * cs, self.dx + cs * cfp, self.dy + cs * cfp2_3, fill="#ffff00", width = 2),
			canvas.create_rectangle(self.dx + cfp * cs, self.dy + cfp * cs, self.dx + cfp_3 * cs, self.dy + cfp_3 * cs, fill="#999999", width = 2)
		]
		
		for i in range(cfp):
			self.board.append(canvas.create_rectangle(self.dx + cs * i, self.dy + cs * cfp, self.dx + cs * (i + 1), self.dy + cs * cfp_1))
		for i in range(cfp - 1, -1, -1):
			self.board.append(canvas.create_rectangle(self.dx + cs * cfp, self.dy + cs * i, self.dx + cs * cfp_1, self.dy + cs * (i + 1)))
		self.board.append(canvas.create_rectangle(self.dx + cs * cfp_1, self.dy, self.dx + cs * cfp_2, self.dy + cs))
		canvas.itemconfig(self.board[7], fill = "#ff0000")
		canvas.itemconfig(self.board[7 + cfp], fill = "#00ff00")
		
		for i in range(cfp):
			self.board.append(canvas.create_rectangle(self.dx + cs * cfp_2, self.dy + cs * i, self.dx + cs * cfp_3, self.dy + cs * (i + 1)))
		for i in range(cfp_3, cfp2_3):
			self.board.append(canvas.create_rectangle(self.dx + cs * i, self.dy + cs * cfp, self.dx + cs * (i + 1), self.dy + cs * cfp_1))
		self.board.append(canvas.create_rectangle(self.dx + cfp2_2 * cs, self.dy + cfp_1 * cs, self.dx + cfp2_3 * cs, self.dy + cfp_2 * cs))
		canvas.itemconfig(self.board[8 + cfp2], fill = "#00ff00")
		canvas.itemconfig(self.board[8 + cfp2 + cfp], fill = "#0000ff")
		
		for i in range(cfp2_2, cfp_2, -1):
			self.board.append(canvas.create_rectangle(self.dx + i * cs, self.dy + cfp_2 * cs, self.dx + (i + 1) * cs, self.dy + cfp_3 * cs))
		for i in range(cfp_3, cfp2_3):
			self.board.append(canvas.create_rectangle(self.dx + cs * cfp_2, self.dy + cs * i, self.dx + cs * cfp_3, self.dy + cs * (i + 1)))
		self.board.append(canvas.create_rectangle(self.dx + cs * cfp_1, self.dy + cs * cfp2_2, self.dx + cs * cfp_2, self.dy + cs * cfp2_3))
		canvas.itemconfig(self.board[9 + cfp2 * 2], fill = "#0000ff")
		canvas.itemconfig(self.board[9 + cfp2 * 2 + cfp], fill = "#ffff00")
		
		for i in range(cfp2_2, cfp_2, -1):
			self.board.append(canvas.create_rectangle(self.dx + cs * cfp, self.dy + cs * i, self.dx + cs * cfp_1, self.dy + cs * (i + 1)))
		for i in range(cfp - 1, -1, -1):
			self.board.append(canvas.create_rectangle(self.dx + cs * i, self.dy + cs * cfp_2, self.dx + cs * (i + 1), self.dy + cs * cfp_3))
		self.board.append(canvas.create_rectangle(self.dx, self.dy + cs * cfp_1, self.dx + cs, self.dy + cs * cfp_2))
		canvas.itemconfig(self.board[10 + cfp2 * 3], fill = "#ffff00")
		canvas.itemconfig(self.board[10 + cfp2 * 3 + cfp], fill = "#ff0000")
		
		"""
		for i in range(1, cfp):
			self.board.append(canvas.create_rectangle(self.dx + i * cs, self.dy + cfp_1 * cs, self.dx + (i + 1) * cs, self.dy + cfp_2 * cs, fill = "#ff0000", width = 2))
		for i in range(1, cfp):
			self.board.append(canvas.create_rectangle(self.dx + cfp_1 * cs, self.dy + i * cs, self.dx + cfp_2 * cs, self.dy + (i + 1) * cs, fill = "#00ff00", width = 2))
		for i in range(cfp2_1, cfp_2, -1):
			self.board.append(canvas.create_rectangle(self.dx + i * cs, self.dy + cfp_1 * cs, self.dx + (i + 1) * cs, self.dy + cfp_2 * cs, fill = "#0000ff", width = 2))
		for i in range(cfp2_1, cfp_2, -1):
			self.board.append(canvas.create_rectangle(self.dx + cfp_1 * cs, self.dy + i * cs, self.dx + cfp_2 * cs, self.dy + (i + 1) * cs, fill = "#ffff00", width = 2))
		"""
		for i in range(cfp - 1):
			self.board.append(canvas.create_rectangle(params.win[0][i][0], params.win[0][i][1], params.win[0][i][0] + cs, params.win[0][i][1] + cs, fill = "#ff0000", width = 2))
		for i in range(cfp - 1):
			self.board.append(canvas.create_rectangle(params.win[1][i][0], params.win[1][i][1], params.win[1][i][0] + cs, params.win[1][i][1] + cs, fill = "#00ff00", width = 2))
		for i in range(cfp - 1,):
			self.board.append(canvas.create_rectangle(params.win[2][i][0], params.win[2][i][1], params.win[2][i][0] + cs, params.win[2][i][1] + cs, fill = "#0000ff", width = 2))
		for i in range(cfp - 1):
			self.board.append(canvas.create_rectangle(params.win[3][i][0], params.win[3][i][1], params.win[3][i][0] + cs, params.win[3][i][1] + cs, fill = "#ffff00", width = 2))
		
		for i in range(1, cfp_1):
			#self.board.append(canvas.create_image(self.dx + (i + 0.17) * cs, self.dy + (cfp_1 + 0.5) * cs, image = params.arrow_images["right"]))
			self.board.append(self.arrow(self.dx + (i + 0.07) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "#000000", "right"))
			self.board.append(self.arrow(self.dx + (i - 0.08) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "#ffffff", "right"))
			self.board.append(self.arrow(self.dx + (i - 0.15) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "#cc0000", "right"))
		for i in range(1, cfp_1):
			self.board.append(self.arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i + 0.07) * cs, 1.5, 1.5, "#000000", "down"))
			self.board.append(self.arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i - 0.08) * cs, 1.5, 1.5, "#ffffff", "down"))
			self.board.append(self.arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i - 0.15) * cs, 1.5, 1.5, "#00cc00", "down"))
		for i in range(cfp2_2, cfp_2, -1):
			self.board.append(self.arrow(self.dx + (i - 0.07) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "#000000", "left"))
			self.board.append(self.arrow(self.dx + (i + 0.08) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "#ffffff", "left"))
			self.board.append(self.arrow(self.dx + (i + 0.15) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "#0000cc", "left"))
		for i in range(cfp2_2, cfp_2, -1):
			self.board.append(self.arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i - 0.07) * cs, 1.5, 1.5, "#000000", "up"))
			self.board.append(self.arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i + 0.08) * cs, 1.5, 1.5, "#ffffff", "up"))
			self.board.append(self.arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i + 0.15) * cs, 1.5, 1.5, "#cccc00", "up"))
		params.print_debug_entry_path("	Board out off set_board !")
	
	def arrow(self, dx, dy, sx, sy, color, dir = "left"):
		#params.print_debug_entry_path("	Board in arrow !", dx, dy, sx, sy, color, dir)
		cs4 = params.cell_size // 4
		if dir == "right":
			return canvas.create_polygon(dx, dy - cs4 * sy, dx, dy + cs4 * sy, dx + cs4 * sx, dy, dx, dy - cs4 * sy, fill=color)
		elif dir == "left":
			return canvas.create_polygon(dx, dy - cs4 * sy, dx, dy + cs4 * sy, dx - cs4 * sx, dy, dx, dy - cs4 * sy, fill=color)
		elif dir == "down":
			return canvas.create_polygon(dx - cs4 * sx, dy, dx + cs4 * sx, dy, dx, dy + cs4 * sx, dx - cs4 * sx, dy, fill=color)
		elif dir == "up":
			return canvas.create_polygon(dx - cs4 * sx, dy, dx + cs4 * sx, dy, dx, dy - cs4 * sy, dx - cs4 * sx, dy, fill=color)
		else:
			#print("Nothing to return!")
			return None
		#params.print_debug_entry_path("	Board out off arrow !")
	
	#just a trail code to represent a single cell and piece in it
	def trail(self):
		params.print_debug_entry_path("	Board in trail !")
		self.r = canvas.create_rectangle(self.dx, self.dy, self.dx + params.cell_size, self.dy + params.cell_size, fill="red")
		image = Image.open(os.path.join(params.base_dir, "images", "yellowPieceAlpha.png"))
		#print(image.size)
		x = params.cell_size * 0.5
		y = x * image.size[1] / image.size[0]
		image = image.resize((int(x), int(y)), Image.ANTIALIAS)
		#print(params.piece_pos[0][0][1])
		self.imgs = []
		arg = 1
		size = "middle"
		for i in range(arg):
			#print(self.dx)
			#print(params.piece_pos[arg - 1][i][0])
			#print(self.dy)
			#print(params.piece_pos[arg - 1][i][1])
			#print(self.dx + params.piece_pos[arg - 1][i][0])
			#print(self.dy + params.piece_pos[arg - 1][i][1])
			self.imgs.append(canvas.create_image(self.dx + params.piece_pos[arg - 1][i][0], self.dy + params.piece_pos[arg - 1][i][1], image = params.images[size][3]))
		params.print_debug_entry_path("Player out off !")
	
	#adjust should be used twice 1)first on old position of piece to shufle pieces there 2)new position of piece to adjust piece
	# only exception is bringOut where only use once
	#do adjustments after move to path from old_path
	def adjust(self, item, old_path):
		params.print_debug_entry_path("Player in adjust !" , items, old_path)
		tags = canvas.gettags(item)
		id = int(tags[0])
		player_id = id // 4
		piece_id = int(id % 4)
		path = int(tags[1])
		
		items = canvas.find_withtag(str(tag[1]))
		l = len(items)
		
		old_items = canvas.find_withtag(str(old_path))
		ol = len(old_items)
		
		if path == -1:
			canvas.itemconfig(params.piece[player_id][piece_id], image = params.images["big"][player_id])
			params.piece_size[player_id][piece_id] = 0
		elif path != -1:
			if l == 1 and params.piece_size[player_id][piece_id] == 2:
				canvas.itemconfig(params.piece[player_id][piece_id], image = params.images["middle"][player_id])
				params.piece_size[player_id][piece_id] = 1
			elif l == 2:
				if params.piece_size[player_id][piece_id] == 1:
					canvas.itemconfig(params.piece[player_id][piece_id], image = params.images["small"][player_id])
					params.piece_size[player_id][piece_id] = 2
				temp = canvas.gettags(items[i])
				tid = int(temp[0])
				tplr_id = tid // 4
				tpc_id = int(tid % 4)
				if params.piece_size[tplr_id][tpc_id] == 1:
					canvas.itemconfig(params.piece[tplr_id][tpc_id], image = params.images["small"][tplr_id])
					params.piece_size[tplr_id][tpc_id] = 2
				self.rePosition(items, path)
			elif l > 2:
				if params.piece_size[player_id][piece_id] == 1:
					canvas.itemconfig(params.piece[player_id][piece_id], image = params.images["small"][player_id])
					params.piece_size[player_id][piece_id] = 2
				self.rePosition(items, path)
			else:
				print("Problem")
			if ol == 1:
				tid = canvas.find_withtag(old_items[0])
				tplr_id = tid // 4
				tpc_id = int(tid % 4)
				if params.piece_size[tplr_id][tpc_id] == 2:
					canvas.itemconfig(params.piece[tplr_id][tpc_id], image = params.images["middle"][tplr_id])
					params.piece_size[tplr_id][tpc_id] = 1
				self.rePosition(old_items, old_path)
			elif ol > 1:
				self.rePosition(old_items, old_path)
				
		params.print_debug_entry_path("Player out off adjust !")
	
	#reposition the items at path according to position and number
	#for particular number of items i define cetrtain position using trail
	def rePosition(self, items, pos):
		params.print_debug_entry_path("Player in rePosition !", items, pos)
		l = len(items)
		tags = canvas.gettags(items[0])
		id = int(tags[0])
		pid = id // 4
		pcid = int(id % 4)
		try:
			pos = int(tags[1].split("@")[1])
		except:
			pos = int(tags[2].split("@")[1])
		for i in range(l):
			if pos < 0:
				canvas.coords(items[i], params.win[pid][(pos * -1) - 2][0] + params.piece_pos[l-1][i][0], params.win[pid][(pos * -1) - 2][1] + params.piece_pos[l-1][i][1])
			else:
				canvas.coords(items[i], params.path[pos][0] + params.piece_pos[l-1][i][0], params.path[pos][1] + params.piece_pos[l-1][i][1])
		params.print_debug_entry_path("Player out off rePosition !")

		
class Player:
	def __init__(self, id, dx, dy, color):
		params.print_debug_entry_path("Player in __init__", id, dx, dy, color)
		self.id = id
		self.color = color
		#dx = 150
		#dy = 200
		self.dx = dx
		self.dy = dy
		params.player_pos[self.id][0] = self.dx
		params.player_pos[self.id][1] = self.dy
		self.state = "normal"
		
		cs = params.cell_size
		cfp = params.cells_for_player
		
		#canvas.create_oval(dx + cs * 1, dy + cs * 2, dx + cs * 4.5, dy + cs * 4.5, fill="#999999", width = 2)
		self.home_site = canvas.create_oval(dx + cs * 1.25, dy + cs * 1.75, dx + cs * 4.75, dy + cs * 4.25, fill="#999999", width = 2)
		
		st = tk.HIDDEN
		self.expaned_pos = np.zeros(4, dtype = np.uint8)
		self.expaned_pos[0] = canvas.create_oval(dx + cs * 0.25, dy + cs * 0.5, dx + cs * 1.75, dy + cs * 1.5, fill="#999999", state = st)
		self.expaned_pos[1] = canvas.create_oval(dx + cs * 4.25, dy + cs * 0.5, dx + cs * 5.75, dy + cs * 1.5, fill="#999999", state = st)
		self.expaned_pos[2] = canvas.create_oval(dx + cs * 4.25, dy + cs * 4.5, dx + cs * 5.75, dy + cs * 5.5, fill="#999999", state = st)
		self.expaned_pos[3] = canvas.create_oval(dx + cs * 0.25, dy + cs * 4.5, dx + cs * 1.75, dy + cs * 5.5, fill="#999999", state = st)
		
		c2 = cfp // 2
		
		#piece positions in expanded state
		params.player_expand[self.id][0][0] = cs
		params.player_expand[self.id][0][1] = cs * 0.5
		params.player_expand[self.id][1][0] = cs * (cfp - 1)
		params.player_expand[self.id][1][1] = cs * 0.5
		params.player_expand[self.id][2][0] = cs * (cfp - 1)
		params.player_expand[self.id][2][1] = cs * (cfp - 1.5)
		params.player_expand[self.id][3][0] = cs
		params.player_expand[self.id][3][1] = cs * (cfp - 1.5)
		
		#piece position in compresed/normal stat+e
		params.player_compress[self.id][0][0] = cs * (c2 - 0.7)
		params.player_compress[self.id][0][1] = cs * (c2 - 0.9)
		params.player_compress[self.id][1][0] = cs * (c2 + 0.4)
		params.player_compress[self.id][1][1] = cs * (c2 - 0.9)
		params.player_compress[self.id][2][0] = cs * (c2 + 0.8)
		params.player_compress[self.id][2][1] = cs * c2
		params.player_compress[self.id][3][0] = cs * (c2 - 0.3)
		params.player_compress[self.id][3][1] = cs * c2
		
		pte = params.player_expand[self.id]
		ptc = params.player_compress[self.id]
		#self.pieces = np.ones(4, dtype = np.int8) * -1
		for i in range(4):
			#print("self.id : ", self.id, "i : ", i)
			#params.pieces[self.id][i] = canvas.create_image(dx + pte[i][0], dy + pte[i][1], image =  params.images["big"][self.id], tags = (str(params.id), "@-1"))
			params.pieces[self.id][i] = canvas.create_image(dx + ptc[i][0], dy + ptc[i][1], image =  params.images["big"][self.id], tags = (str(params.id), "@-1"))
			canvas.tag_bind(params.pieces[self.id][i], "<Button-1>", self.makeMove)
			#print("tkinter item id : ", params.pieces[self.id][i])
			#print("params.id : ", params.id)
			params.id += 1
		params.print_debug_entry_path("Player out off __init__ !")
	
	def refresh(self, pid):
		params.print_debug_entry_path("Player in refresh !", pid)
		for i in range(4):
			tags = canvas.gettags(params.pieces[pid][i])
			#print(" _ :", i, tags)
			if "@-1" in tags:
				canvas.coords(params.pieces[pid][i], params.player_pos[pid][0] + params.player_compress[pid][i][0], params.player_pos[pid][1] + params.player_compress[pid][i][1])
		params.print_debug_entry_path("player out off refresh !")
	
	def expand(self):
		params.print_debug_entry_path("Player in expand !")
		for i in range(4):
			tags = canvas.gettags(params.pieces[self.id][i])
			if "@-1" in tags:
				canvas.itemconfig(self.expaned_pos[i], state = tk.NORMAL)
				canvas.coords(params.pieces[self.id][i], self.dx + params.player_expand[self.id][i][0], self.dy + params.player_expand[self.id][i][1])
		params.print_debug_entry_path("Player ot off expand !")
	
	def compress(self):
		params.print_debug_entry_path("Player in compress !")
		for i in range(4):
			tags = canvas.gettags(params.pieces[self.id][i])
			canvas.itemconfig(self.expaned_pos[i], state = tk.HIDDEN)
			if "@-1" in tags:
				canvas.coords(params.pieces[self.id][i], self.dx + params.player_compress[self.id][i][0], self.dy + params.player_compress[self.id][i][1])				
		params.print_debug_entry_path("Player out off compress !")
	
	def bringOut(self, id):
		params.print_debug_entry_path("Player in bringOut !", id)
		#tags = canvas.gettags(params.pieces[0][0])
		#print("tags : ", tags)
		#id = int(tags[0])
		#id = 0 #if set for event
		pid = id // 4
		pcid = int(id % 4)
		#pos = int(tags[1].split("@")[1])
		pos = -1
		#print("pos : ", pos)
		pt = params.path[params.path_out[pid]]
		#print("coords : ", canvas.coords(params.pieces[pid][pcid]))
		canvas.coords(params.pieces[pid][pcid], pt[0], pt[1])
		#print("coords : ", canvas.coords(params.pieces[pid][pcid]))
		#print("tags : ", canvas.gettags(params.pieces[pid][pcid]))
		canvas.dtag(params.pieces[pid][pcid], "@-1")
		#print("tags : ", canvas.gettags(params.pieces[pid][pcid]))
		canvas.addtag_withtag("@"+str(params.path_out[pid]), params.pieces[pid][pcid])
		#print("tags : ", canvas.gettags(params.pieces[pid][pcid]))
		self.adjust(params.pieces[pid][pcid], params.path_out[pid])
		params.print_debug_entry_path("Player out off bringOut !")
	
	def move(self, id, num):
		params.print_debug_entry_path("Player in move !", id, num)
		pid = id //4
		pcid = int(id % 4)
		item = params.pieces[pid][pcid]
		tags = canvas.gettags(item)
		#print("__:__", item, tags, params.dice_roll)
		try:
			pos = int(tags[2].split("@")[1])
		except:
			pos = int(tags[1].split("@")[1])
		if pos == -1 and params.dice_roll == 5:
			self.bringOut()
			params.change()
			params.print_debug_entry_path("Player out off move with retuen !")
			return
		old_pos = pos
		#print("pos : ", pos)
		#print("pos + 1 : ", pos + 1)
		#print("len(params.path) : ", len(params.path))
		#print("int((pos + num) % len(params.path)) : ", int((pos + num) % len(params.path)))
		self.check_for_active()
		for i in range(num + 1):
			#print("pos in : ", pos)
			if pos >= 0:
				pos = int((pos + 1) % len(params.path))
				#print("new_pos : ", pos)
				if (pos + 1) == params.path_out[pid]:
					pos = (pid * -10) -2
			elif pos < 0:
				pos = pos - 1
				#print("new_pos : ", pos)
				#print("(pid * -10) + (len(params.win[0]) * -1) - 2 : ", (pid * -10) + (len(params.win[0]) * -1) - 2)
				if pos  == (pid * -10) + (len(params.win[0]) * -1) - 2 and i == num :
					canvas.itemconfig( params.pieces[pid][pcid], state = tk.HIDDEN )
					#print(pid, id, "dice wins!")
					params.print_debug_entry_path("Player out off with win and return !")
					return "ok"
				else:
					print("else condition !")
			if pos == -8:
				#print("can't play this move !")
				return "cmm"#"cant make move"
			#print("pos out : ", pos)
		"""
		if pos  == (pid * -10) + (len(params.win[0]) * -1) - 2 and i == num - 1:
			canvas.itemconfig( params.pieces[pid][pcid], state = tk.HIDDEN )
			print(pid, id, "dice wins!")
			params.print_debug_entry_path("Player out off with win and return !")
			return "ok"
		"""
		#print("__:_:__ : ", id, pid, pcid, old_pos, pos)
		if pos < 0:
			pt = params.win[pid][((pos*-1) - 2) - (pid * 10)]
		else:
			pt = params.path[pos]
		#print("__:_:__ : ", id, pid, pcid, old_pos, pos, pt)
		
		#print("coords : ", canvas.coords(params.pieces[pid][pcid]))
		canvas.coords(params.pieces[pid][pcid], pt[0], pt[1])
		#print("coords : ", canvas.coords(params.pieces[pid][pcid]))
		
		#print("tags : ", canvas.gettags(params.pieces[pid][pcid]))
		canvas.dtag(params.pieces[pid][pcid], "@" + str(old_pos))
		#print("tags : ", canvas.gettags(params.pieces[pid][pcid]))
		canvas.addtag_withtag("@"+str(pos), params.pieces[pid][pcid])
		#print("tags : ", canvas.gettags(params.pieces[pid][pcid]))
		
		#print("__::__", pos, id)
		if not (pos in params.path_out or pos in params.path_safe):
			self.catch_n_sendBack_enimies(pos, id)
		self.adjust(params.pieces[pid][pcid], old_pos)
		params.print_debug_entry_path("Player out off move")
		return "ok"
	
	def check_for_active(self):
		params.print_debug_entry_path("Player in check_for_active !")
		id = params.dice_pos
		id4 = id * 4
		active = 0
		in_home = 0
		active_items = [0, 0, 0, 0]
		inside_home = []
		for i in range(4):
			items = canvas.find_withtag(params.pieces[id][i])
			#print("tags : ", id, id4, i, items)
			tags = canvas.gettags(items[0])
			#print("tags : ", tags)
			try:
				pos = int(tags[1].split("@")[1])
			except:
				pos = int(tags[2].split("@")[1])
			num = params.dice_roll
			#print("_:", pos, num)
			if pos == -1:
				in_home += 1
				active_items[i] -= 1
				inside_home.append(i)
				continue
			for j in range(num):
				#print("pos in : ", pos)
				if pos >= 0:
					pos = int((pos + 1) % len(params.path))
					if (pos + 1) == params.path_out[id]:
						pos = (id * -10) -2
				elif pos < 0:
					pos = pos - 1
					#if pos  == (id * -10) + (len(params.win[0]) * -1) - 2 and i == num - 1:
					#	pass#active += 1
					#else:
					#	active -= 1
					#	active_items[i] -= 1
					#	print("one found !")
					#	break
			if pos > -8:
				active += 1
				#print("i : ", i)
				active_items[i] += 1
		#print("Active_items : ", active_items)
		#print("In_home : ", in_home)
		#print("Active : ", active)
		if num == 5 and in_home >0:
			return ["keep", None, None, inside_home]
		if active > 1:
			choices = []
			for i in range(4):
				if active_items[i] == 1:
					choices.append(i)
			choice = random.choice(choices)
			return ["change", choice, None, None]
		elif active == 1:
			for i in range(4):
				if active_items[i] == 1:
					return ["ok", i, in_home, None]#		elif (num == 5 and in_home > 0) or active > 0:#			return ["ok", None, in_home] 
		else:
			return ["not ok", None, in_home, None]
		params.print_debug_entry_path("Player out off check_for_active !")
	
	def catch_n_sendBack_enimies(self, pos, id):
		params.print_debug_entry_path("Player in catch_n_sendBack_enimies !", pos, id)
		items = canvas.find_withtag("@" + str(pos))
		if len(items) == 1:
			params.print_debug_entry_path("Player out off catch_n_sendBack_enimies with return !")
			return
		else:
			print("len(items : )", len(items))
		ids = {0:0, 1:0, 2:0, 3:0}
		del(ids[id // 4])
		for i in range(len(items)):
			temp = canvas.gettags(items[i])
			#print("temp : ", temp)
			if id in temp:
				continue
			tid = int(temp[0])
			tpid = tid // 4
			if not tpid in ids:
				continue
			self.sendBack(tid)
			del(ids[tpid])
		params.print_debug_entry_path("Player out off catch_n_sendBack_enimies !")
	
	def sendBack(self, id):
		params.print_debug_entry_path("Player in sendBack !", id)
		pid = id // 4
		pcid = int(id % 4)
		item = params.pieces[pid][pcid]
		#print("item : ", item)
		tags = canvas.gettags(item)
		#print("tags : ", tags)
		try:
			pos = int(tags[1].split("@")[1])
		except:
			pos = int(tags[2].split("@")[1])
		canvas.dtag(params.pieces[pid][pcid], "@" + str(pos))
		canvas.addtag_withtag("@-1", params.pieces[pid][pcid])
		canvas.coords(params.pieces[pid][pcid], params.player_pos[pid][0] + params.player_compress[pid][pcid][0], params.player_pos[pid][1] + params.player_compress[pid][pcid][1])
		canvas.itemconfig(params.pieces[pid][pcid], image = params.images["big"][pid])
		params.piece_size[pid][pcid] = 0
		self.refresh(pid)
		params.double = True
		params.print_debug_entry_path("Player out off sendBack !")
	
	def makeMove(self, event):
		params.print_debug_entry_path("Player in makeMove !", event)
		#print("Player in makeMove !", event)
		if params.dice_roll == -1:
			params.print_debug_entry_path("Player out off makeMove with return !")
			return 
		if "<class 'tkinter.Event'>" == str(type(event)):
			params.current = tk.CURRENT
		else:
			params.current = "myCurrentTag"
		#	return
		#print("params.current : ", params.current)
		
		#print(canvas.find_withtag(params.current))
		items = canvas.find_withtag(params.current)
		if len(items) > 1:
			print("	Problem !")
		tags = canvas.gettags(params.current)
		#print("tags : ", tags)
		id = int(tags[0])
		pid = id //4
		pcid = int(id % 4)
		try:
			pos = int(tags[2].split("@")[1])
		except:
			pos = int(tags[1].split("@")[1])
		#print("tags : ", tags)
		if pos == -1:
			if params.dice_roll == 5:
				self.bringOut(id)
				params.change()
			else:
				params.print_debug_entry_path("Player out off makeMove with return !")
				return
			#self.bringOut(id)
		else:
			rt = self.move(id, params.dice_roll)
			#print("move returns : ", rt)
			if rt == "ok":
				params.change()
			elif rt == "cmm":
				if params.auto:
					print("cant make move!")
					
		params.print_debug_entry_path("Player out off makeMove !")
	
	#adjust should be used twice 1)first on old position of piece to shufle pieces there 2)new position of piece to adjust piece
	# only exception is bringOut where only use once
	#do adjustments after move to path from old_path
	def adjust(self, item, old_path):
		params.print_debug_entry_path("Player in adjust !" , item, old_path)
		tags = canvas.gettags(item)
		#print("tags : ", tags)
		id = int(tags[0])
		player_id = id // 4
		piece_id = int(id % 4)
		try:
			path = int(tags[2].split("@")[1])
		except:
			path = int(tags[1].split("@")[1])		
		#print(tags[1].split("@")[1])
		#print(str(tags[1].split("@")[1]))
		
		#if tags[1] == params.current:
		#	items = canvas.find_withtag(tags[2])
		#else:
		#	items = canvas.find_withtag(tags[1])
		items = canvas.find_withtag("@" + str(path))
		l = len(items)
		#print("items : ", items)
		#print("old_path : ", old_path )
		old_items = canvas.find_withtag("@" + str(old_path))
		ol = len(old_items)
		#print("old_path : ", old_path )
		
		if path == -1:
			canvas.itemconfig(params.pieces[player_id][piece_id], image = params.images["big"][player_id])
			params.piece_size[player_id][piece_id] = 0
		elif not path == -1:
			if l == 1:
				#print("l = 1")
				if (params.piece_size[player_id][piece_id] == 2 or params.piece_size[player_id][piece_id] == 0):
					canvas.itemconfig(params.pieces[player_id][piece_id], image = params.images["middle"][player_id])
					params.piece_size[player_id][piece_id] = 1
			elif l == 2:
				#print("l = 2")
				if params.piece_size[player_id][piece_id] == 1 or params.piece_size[player_id][piece_id] == 0:
					canvas.itemconfig(params.pieces[player_id][piece_id], image = params.images["small"][player_id])
					params.piece_size[player_id][piece_id] = 2
				temp = canvas.gettags(items[0])
				if params.current in temp:
					temp = canvas.gettags(items[1])
				tid = int(temp[0])
				tplr_id = tid // 4
				tpc_id = int(tid % 4)
				if params.piece_size[tplr_id][tpc_id] == 1:
					canvas.itemconfig(params.pieces[tplr_id][tpc_id], image = params.images["small"][tplr_id])
					params.piece_size[tplr_id][tpc_id] = 2
				#self.rePosition(items, path)
			elif l > 2:
				#print("l = >")
				if params.piece_size[player_id][piece_id] == 1 or params.piece_size[player_id][piece_id] == 0:
					canvas.itemconfig(params.pieces[player_id][piece_id], image = params.images["small"][player_id])
					params.piece_size[player_id][piece_id] = 2
			else:
				print("Problem")
				print("len(items) or l : ", l)
			self.rePosition(items, path)
			#print("old path : ", old_path)
			#print("'@'+str(old_path) : ", "@"+str(old_path))
			#print("old_items : ", canvas.find_withtag("@"+str(old_path)))
			#print("ol : ", ol)
			if ol == 1:
				#print("Only one is remained !")
				#print("temp : ", old_items)
				ttags = canvas.gettags(old_items[0])
				tid = int(ttags[0])
				tplr_id = tid // 4
				tpc_id = int(tid % 4)
				if params.piece_size[tplr_id][tpc_id] == 2:
					canvas.itemconfig(params.pieces[tplr_id][tpc_id], image = params.images["middle"][tplr_id])
					params.piece_size[tplr_id][tpc_id] = 1
			elif ol > 1:
				if old_path == -1:
					params.print_debug_entry_path("Player out off adjust with return!")
					return
			self.rePosition(old_items, old_path)
				
		params.print_debug_entry_path("Player out off adjust !")
	
	def rePosition(self, items, pos):
		params.print_debug_entry_path("Player in rePosition !", items, pos)
		l = len(items)
		if l == 0:
			params.print_debug_entry_path("Player out off rePosition with return !")
			return
		#print("items : ", items)
		#print("l : ", l)
		tags = canvas.gettags(items[0])
		id = int(tags[0])
		pid = id // 4
		pcid = int(id % 4)
		try:
			pos = int(tags[1].split("@")[1])
		except:
			pos = int(tags[2].split("@")[1])
		#print(" __--__ : ", l, tags, id, pid, pcid, pos, ((pos*-1) - 2), (pid * 10), ((pos*-1) - 2) - (pid * 10))
		zid = ((pos*-1) - 2) - (pid * 10)
		#if pos < 0:
		#	print(" __--__ : ", params.win[pid][((pos*-1) - 2) - (pid * 10)][0])
		for i in range(l):
			if pos < 0:
				canvas.coords(items[i], params.win[pid][zid][0] + params.piece_pos[l-1][i][0], params.win[pid][zid][1] + params.piece_pos[l-1][i][1])
				#canvas.coords(items[i], params.win[pid][(pos * -1) - 2][0] + params.piece_pos[l-1][i][0], params.win[pid][(pos * -1) - 2][1] + params.piece_pos[l-1][i][1])
			else:
				canvas.coords(items[i], params.path[int(pos)][0] + params.piece_pos[l-1][i][0], params.path[int(pos)][1] + params.piece_pos[l-1][i][1])
		params.print_debug_entry_path("Player out off rePosition !")


class Dice:
	def __init__(self, dx, dy):
		params.print_debug_entry_path("Dice in __init__ !", dx, dy)
		self.images = [ "white1Small.png", "white2Small.png", "white3Small.png", "white4Small.png", "white5Small.png", "white6Small.png" ]
		self.dx = dx
		self.dy = dy
		cfp2 = params.cells_for_player // 2
		cs = params.cell_size
		self.pos = [cs * cfp2, cs * cfp2]
		canvas.dice_images = [None, None, None, None, None, None]
		self.dice_roll = []
		tk_state = tk.HIDDEN
		for i in range(6):
			self.dice_roll.append( canvas.create_image(self.pos[0], self.pos[1], image = self.get_image(i, 0.75, 0.75), state = tk_state) )
		random.seed(time.time())
		params.print_debug_entry_path("Dice out off __init__ !")
	
	def get_image(self, id, sx, sy):
		params.print_debug_entry_path("Dice in get_image !", id, sx, sy)
		image = Image.open(os.path.join(params.base_dir, "dice", self.images[id]))
		img = image.resize((int(image.size[0] * sx), int(image.size[1] * sy)), Image.ANTIALIAS)
		canvas.dice_images[id] = ImageTk.PhotoImage(img)
		params.print_debug_entry_path("Dice out off get_image by returning : ", canvas.dice_images[id], " !")
		return canvas.dice_images[id]
	
	def roll_the_dice(self):
		params.print_debug_entry_path("Dice in roll_the_dice !")
		#canvas.itemconfig( self.dice_roll[params.dice_roll], state = tk.HIDDEN )
		if not params.dice_roll == -1:
			params.print_debug_entry_path("Dice out off roll_the_dice with return !")
			return
		if params.debug or params.testing:
			params.dice_roll = params.debug_roll[int(params.roll_id%len(params.debug_roll))]
			params.roll_id += 1
		else:
			roll = int(int(random.random() * 1000) % 6)
			params.dice_roll = roll
		params.record_file.write(str(params.dice_roll) + ", ")
		#print("dx_dy : ", self.dx, self.dy)
		#print("__---__ : ", params.dice_roll, self.dice_roll[params.dice_roll])
		canvas.coords(self.dice_roll[params.dice_roll], self.dx + self.pos[0], self.dy + self.pos[1])
		canvas.itemconfig( self.dice_roll[params.dice_roll], state = tk.NORMAL )
		params.print_debug_entry_path("Dice out off roll_the_dice !")
	
	def move(self, dx, dy):
		params.print_debug_entry_path("Dice in move !", dx, dy)
		if not params.dice_roll == -1:
			canvas.itemconfig( self.dice_roll[params.dice_roll], state = tk.HIDDEN )
			params.dice_roll = -1
		self.dx = dx
		self.dy = dy
		#print("dx_dy : ", self.dx, self.dy)
		params.print_debug_entry_path("Dice out off move !")

class GUI:
	def __init__(self):
		pass

def on_closing():
	params.record_file.close()
	root.destroy()

if __name__ == "__main__":
	params = Params()
	root = tk.Tk()
	root.title("my Ludo Game")
	root.protocol("WM_DELETE_WINDOW", on_closing)
	canvas = tk.Canvas(root, width = params.canvas_width, height = params.canvas_height)
	canvas.pack()
	canvas.focus_set()
	params.setImages(canvas)

	board = Board(params.marginX, params.marginY)
	#plr = Player(0, params.marginX, params.marginY, "#ff0000")
	#plr.expand()
	#dice = Dice()
	#import test

	#params.debug_roll = test.test5[:]
	#params.debug = True

	#params.debug_roll = test.test_old1[:]
	params.auto = True

	#params.record_file = open(os.path.join( params.base_dir, "record.txt"), "w")
	params.record_file = open("record.txt", "w")
	#print("file contents : ", params.record_file.read())
	#params.record_file.write("__:__:__\n__:__:__\n__:__:__\n")

	canvas.after(500, board.checkKey, "r")

	root.mainloop()
