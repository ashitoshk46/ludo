try:
	import tkinter as tk
	from tkinter import font as tkFont
except:
	import Tkinter as tk
	import tkFont
import time
import random
import cv2
import os
from PIL import Image, ImageTk
import numpy as np
import test


canvas = None

class Params:
	def __init__(self):
		self.base_dir = os.getcwd()
		self.current = None
		self.width = 800
		self.height = 600
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
		self.win_pieces = [[], [], [], []]
		self.piece_size = np.zeros((4, 4), dtype = np.uint16) #0]big size    #1]middle size    #2]small size
		self.piece_multiples = np.zeros((4, 4), dtype = np.uint16) #0]Single    #1]Multipes
		self.piece_pos_in_path = np.zeros((4, 4), dtype = np.uint16)
		image = Image.open(os.path.join(self.base_dir, "images", self.image_names[0]))
		self.ratio = image.size[1]/image.size[0]
		self.path = np.zeros((self.cells_for_player * 8 + 4, 2), dtype = np.uint16)
		self.win = np.zeros((4, self.cells_for_player - 1, 2), dtype = np.uint16)
		self.set_path()
		self.change = None
		self.set_extra_path()
		self.set_position()
		self.debug = False#True
		if self.debug:
			self.dice_roll = 1
		else:
			self.dice_roll = -1
		self.debug_roll = [int(i % 6) for i in range(50)]
		#print(self.debug_roll)
		self.roll_id = 0
		self.dice_pos = 0
		self.active = None
		self.toggleMenu = None
		self.menuFont1 = None
		self.rootFont1 = None
		self.menuFont2 = None
		self.rootFont2 = None
		self.menuFont3 = None
		self.rootFont3 = None
		self.menuFont4 = None
		self.rootFont4 = None
		self.focused = False
		self.screen_width = None
		self.screen_height = None
		self.game_started = False
		self.double = None
	
	def set_extra_path(self):
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
	
	def set_player_pos(self):
		self.player_pos = [
			[params.marginX, params.marginY],
			[params.marginX + (params.cells_for_player + 3) * params.cell_size, params.marginY],
			[params.marginX + (params.cells_for_player + 3) * params.cell_size, params.marginY + (params.cells_for_player + 3) * params.cell_size],
			[params.marginX, params.marginY + (params.cells_for_player + 3) * params.cell_size]
		]
	
	
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
			print(info)
	
	def change(self):
		self.change()
	
	def styleButton(self, widget, i):
		if i == 0:
			widget.config(font = self.rootFont1, bg = "#aaaaaa", activebackground="#bbbbff", bd = 5, width = 10)
		elif i == 1:
			widget.config(font = self.menuFont1, bg = "#aaaaaa", activebackground="#bbbbff", bd = 5, width = 10)
	
	def styleLabel(self, widget, i):
		if i == 0:
			widget.config(font = self.rootFont2, bd = 5)
		elif i == 1:
			widget.config(font = self.menuFont2, bd = 5)
	
	def styleCheckbutton(self, widget, i):
		if i == 0:
			widget.config(font = self.rootFont3)
		elif i == 1:
			widget.config(font = self.menuFont3)
	
	def styleEntry(self, widget, i):
		if i == 0:
			widget.config(font = self.rootFont4, width = 4)
		elif i == 1:
			widget.config(font = self.menuFont4, width = 4)
	
	def toggle(self):
		#print(self.button1.cget)
		#print(self.button1.cget("text"))
		if self.button1.cget("text") == "Show Menu":
			self.button1.config(text = "Hide Menu")
		elif self.button1.cget("text") == "Hide Menu":
			self.button1.config(text = "Show Menu")
		self.toggleMenu()
		if self.focused:
			self.focused = False
		else:
			self.focused = True
	
	def setGUI(self):
		self.button1 = tk.Button(canvas, text = "Hide Menu", command=self.toggle)
		self.button1.place(x = self.marginX + params.width - 225, y = 10)
		params.styleButton(self.button1, 0)
		self.button1.bind("<Button-1>", self.clickIn)
		self.button1.bind("<ButtonRelease-1>", self.clickOut)
	
	def clickIn(self, event):
		print("clickIn!")
	
	def clickOut(self, event):
		print("clickOut!")

	
class Int(tk.StringVar):
	def get(self):
		tmp = super().get()
		if tmp == "":
			return params.cells_for_player
		else:
			try:
				return int(tmp)
			except:
				return params.cells_for_player
	
	def set(self, val):
		try:
			super().set(str(int(val)))
		except:
			super().set(str(params.cells_for_player))

	
class Board:
	def __init__(self, dx, dy):
		params.print_debug_entry_path("Board in __init__ !")
		self.dx = dx
		self.dy = dy
		#self.trail()
		self.dice = None
		self.set_board()
		params.set_player_pos()
		self.players = [
			Player(0, "#ff0000"),
			Player(1, "#00ff00"),
			Player(2, "#0000ff"),
			Player(3, "#ffff00")
		]
		self.setDice()
		canvas.bind("<Key>", self.keyEvent)
		self.dice_pos = 0
		params.dice_pos = 0
		self.players[self.dice_pos].expand()
		params.change = self.change
		#print(self.change)
		self.font1 = tkFont.Font(root=root, size=20)
		params.rootFont1 = self.font1
		params.print_debug_entry_path("Board out off __init__ !")
	
	def setDice(self):
		self.dice = Dice(params.marginX, params.marginY)
	
	def delDice(self):
		del(self.dice)
	
	def setPlayers(self):
		self.players[0].repos()
		self.players[1].repos()
		self.players[2].repos()
		self.players[3].repos()
	
	def delPlyers(self):
		del(self.players)
	
	def keyEvent(self, event):
		params.print_debug_entry_path("Board in keyEvent !")
		if not params.focused and not params.game_started:
			params.print_debug_entry_path("Board out off keyEvent because cnavas is not focused!")
			return
		#print(event.char)
		#print(event.keycode)
		#print(event.char == 'r')
		#print(event.char == 'n')
		if event.char == "r":
			self.dice.roll_the_dice()
			rt = self.players[self.dice_pos].check_for_active()
			print(rt)
			if rt[0] == "not ok":
				#print(time.time())
				#time.sleep(1)
				#print(time.time())
				canvas.after(500, params.change)
			elif rt[0] == "ok" and not rt[1] == None:
				print("Only on out!")
				print("pid : ", params.dice_pos, " pcid or rt[1] : ", rt[1])
				print("in the home or rt[2]", rt[2])
				if not (len(rt[2]) > 0 and params.dice_roll == 5):
					canvas.addtag_withtag("myCurrentTag", params.pieces[params.dice_pos][rt[1]])
					#print(canvas.gettags("!"))
					#print("0:0:", canvas.gettags(params.pieces[params.dice_pos][rt[1]]))
					#canvas.dtag(params.pieces[params.dice_pos][rt[1]], "!")
					#print("1:1:", canvas.gettags(params.pieces[params.dice_pos][rt[1]]))
					params.active = rt[1]
					canvas.after(500, self.players[params.dice_pos].makeMove, "myCurrentTag")
				print("only one out end !")
			
		elif event.char == 'n' and params.debug:
			params.double = False
			self.change()
			
		elif event.char == '':
			pass
		
		if event.keycode == 37:
			print("Left key!")
		elif event.keycode == 38:
			print("Up key!")
		elif event.keycode == 39:
			print("Right key!")
		elif event.keycode == 40:
			print("Down key!")
		params.print_debug_entry_path("Board out off keyEvent !")
	
	def change(self):
		params.print_debug_entry_path("Board in change !")
		print("Params.double : ", params.double)
		print("params.active : ", params.active)
		if not params.active == None:
			canvas.dtag("myCurrentTag", "myCurrentTag")
			params.active = None
		if params.double:
			params.double = False
			print("Lucky got second chance!")
			self.dice.move(params.player_pos[self.dice_pos][0], params.player_pos[self.dice_pos][1])
			params.print_debug_entry_path("Board out off change becuse got second change!")
			return
		self.players[self.dice_pos].compress()
		self.dice_pos = int((self.dice_pos + 1) % 4)
		params.dice_pos = int((params.dice_pos + 1) % 4)
		self.dice.move(params.player_pos[self.dice_pos][0], params.player_pos[self.dice_pos][1])
		self.players[self.dice_pos].expand()
		params.print_debug_entry_path("Board out off change !")
	
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
		
		for i in range(cfp - 1):
			self.board.append(canvas.create_rectangle(params.win[0][i][0], params.win[0][i][1], params.win[0][i][0] + cs, params.win[0][i][1] + cs, fill = "#ff0000", width = 2))
		for i in range(cfp - 1):
			self.board.append(canvas.create_rectangle(params.win[1][i][0], params.win[1][i][1], params.win[1][i][0] + cs, params.win[1][i][1] + cs, fill = "#00ff00", width = 2))
		for i in range(cfp - 1,):
			self.board.append(canvas.create_rectangle(params.win[2][i][0], params.win[2][i][1], params.win[2][i][0] + cs, params.win[2][i][1] + cs, fill = "#0000ff", width = 2))
		for i in range(cfp - 1):
			self.board.append(canvas.create_rectangle(params.win[3][i][0], params.win[3][i][1], params.win[3][i][0] + cs, params.win[3][i][1] + cs, fill = "#ffff00", width = 2))
		
		for i in range(1, cfp_1):
			indx = len(self.board) - 1
			#print("ex0 : ", indx)
			#print("ex1 : ", self.board[indx])
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
	
	def redraw_board(self):
		params.print_debug_entry_path("Board in redraw_board !")
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
		
		canvas.coords(self.board[0], self.dx, self.dy, self.dx + f, self.dy + f)
		canvas.coords(self.board[1], self.dx, self.dy, self.dx + cs * cfp, self.dy + cs * cfp)
		canvas.coords(self.board[2], self.dx + cfp_3 * cs, self.dy, self.dx + cs * cfp2_3, self.dy + cs * cfp)
		canvas.coords(self.board[3], self.dx + cfp_3 * cs, self.dy + cfp_3 * cs, self.dx + cs * cfp2_3, self.dy + cs * cfp2_3)
		canvas.coords(self.board[4], self.dx, self.dy + cfp_3 * cs, self.dx + cs * cfp, self.dy + cs * cfp2_3)
		canvas.coords(self.board[5], self.dx + cfp * cs, self.dy + cfp * cs, self.dx + cfp_3 * cs, self.dy + cfp_3 * cs)
		
		indx = 6
		#print("rindx : ", indx)
		for i in range(cfp):
			canvas.coords(self.board[indx], self.dx + cs * i, self.dy + cs * cfp, self.dx + cs * (i + 1), self.dy + cs * cfp_1)
			indx += 1
		for i in range(cfp - 1, -1, -1):
			canvas.coords(self.board[indx], self.dx + cs * cfp, self.dy + cs * i, self.dx + cs * cfp_1, self.dy + cs * (i + 1))
			indx += 1
		canvas.coords(self.board[indx], self.dx + cs * cfp_1, self.dy, self.dx + cs * cfp_2, self.dy + cs)
		indx += 1
		
		#print("rindx : ", indx)
		for i in range(cfp):
			canvas.coords(self.board[indx], self.dx + cs * cfp_2, self.dy + cs * i, self.dx + cs * cfp_3, self.dy + cs * (i + 1))
			indx += 1
		for i in range(cfp_3, cfp2_3):
			canvas.coords(self.board[indx], self.dx + cs * i, self.dy + cs * cfp, self.dx + cs * (i + 1), self.dy + cs * cfp_1)
			indx += 1
		canvas.coords(self.board[indx], self.dx + cfp2_2 * cs, self.dy + cfp_1 * cs, self.dx + cfp2_3 * cs, self.dy + cfp_2 * cs)
		indx += 1
		
		#print("rindx : ", indx)
		for i in range(cfp2_2, cfp_2, -1):
			canvas.coords(self.board[indx], self.dx + i * cs, self.dy + cfp_2 * cs, self.dx + (i + 1) * cs, self.dy + cfp_3 * cs)
			indx += 1
		for i in range(cfp_3, cfp2_3):
			canvas.coords(self.board[indx], self.dx + cs * cfp_2, self.dy + cs * i, self.dx + cs * cfp_3, self.dy + cs * (i + 1))
			indx += 1
		canvas.coords(self.board[indx], self.dx + cs * cfp_1, self.dy + cs * cfp2_2, self.dx + cs * cfp_2, self.dy + cs * cfp2_3)
		indx += 1
		
		#print("rindx : ", indx)
		for i in range(cfp2_2, cfp_2, -1):
			canvas.coords(self.board[indx], self.dx + cs * cfp, self.dy + cs * i, self.dx + cs * cfp_1, self.dy + cs * (i + 1))
			indx += 1
		for i in range(cfp - 1, -1, -1):
			canvas.coords(self.board[indx], self.dx + cs * i, self.dy + cs * cfp_2, self.dx + cs * (i + 1), self.dy + cs * cfp_3)
			indx += 1
		canvas.coords(self.board[indx], self.dx, self.dy + cs * cfp_1, self.dx + cs, self.dy + cs * cfp_2)
		indx += 1
		
		#print("rindx : ", indx)
		for i in range(cfp - 1):
			canvas.coords(self.board[indx], params.win[0][i][0], params.win[0][i][1], params.win[0][i][0] + cs, params.win[0][i][1] + cs)
			indx += 1
		for i in range(cfp - 1):
			canvas.coords(self.board[indx], params.win[1][i][0], params.win[1][i][1], params.win[1][i][0] + cs, params.win[1][i][1] + cs)
			indx += 1
		for i in range(cfp - 1,):
			canvas.coords(self.board[indx], params.win[2][i][0], params.win[2][i][1], params.win[2][i][0] + cs, params.win[2][i][1] + cs)
			indx += 1
		for i in range(cfp - 1):
			canvas.coords(self.board[indx], params.win[3][i][0], params.win[3][i][1], params.win[3][i][0] + cs, params.win[3][i][1] + cs)
			indx += 1
		
		#print("rindx : ", indx)
		for i in range(1, cfp_1):
			#print("ex0 : ", indx)
			#print("ex1 : ", self.board[indx])
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (i + 0.07) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "right"))
			indx += 1
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (i - 0.08) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "right"))
			indx += 1
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (i - 0.15) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "right"))
			indx += 1
		for i in range(1, cfp_1):
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i + 0.07) * cs, 1.5, 1.5, "down"))
			indx += 1
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i - 0.08) * cs, 1.5, 1.5, "down"))
			indx += 1
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i - 0.15) * cs, 1.5, 1.5, "down"))
			indx += 1
		for i in range(cfp2_2, cfp_2, -1):
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (i - 0.07) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "left"))
			indx += 1
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (i + 0.08) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "left"))
			indx += 1
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (i + 0.15) * cs, self.dy + (cfp_1 + 0.5) * cs, 1.5, 1.5, "left"))
			indx += 1
		for i in range(cfp2_2, cfp_2, -1):
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i - 0.07) * cs, 1.5, 1.5, "up"))
			indx += 1
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i + 0.08) * cs, 1.5, 1.5, "up"))
			indx += 1
			canvas.coords(self.board[indx], self.redraw_arrow(self.dx + (cfp_1 + 0.5) * cs, self.dy + (i + 0.15) * cs, 1.5, 1.5, "up"))
			indx += 1
		params.print_debug_entry_path("	Board out off redraw_board !")
	
	def repos(self):
		self.players[self.dice_pos].expand()
	
	def arrow(self, dx, dy, sx, sy, color, dir = "left"):
		params.print_debug_entry_path("	Board in arrow !", dx, dy, sx, sy, color, dir)
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
			print("Nothing to return!")
			return None
		params.print_debug_entry_path("	Board out off arrow !")
	
	def redraw_arrow(self, dx, dy, sx, sy, dir = "left"):
		params.print_debug_entry_path("	Board in arrow !", dx, dy, sx, sy, dir)
		cs4 = params.cell_size // 4
		if dir == "right":
			return (dx, dy - cs4 * sy, dx, dy + cs4 * sy, dx + cs4 * sx, dy, dx, dy - cs4 * sy)
		elif dir == "left":
			return (dx, dy - cs4 * sy, dx, dy + cs4 * sy, dx - cs4 * sx, dy, dx, dy - cs4 * sy)
		elif dir == "down":
			return (dx - cs4 * sx, dy, dx + cs4 * sx, dy, dx, dy + cs4 * sx, dx - cs4 * sx, dy)
		elif dir == "up":
			return (dx - cs4 * sx, dy, dx + cs4 * sx, dy, dx, dy - cs4 * sy, dx - cs4 * sx, dy)
		else:
			print("Nothing to return!")
			return None
		params.print_debug_entry_path("	Board out off arrow !")
	
	#just a trail code to represent a single cell and piece in it
	def trail(self):
		params.print_debug_entry_path("	Board in trail !")
		self.r = canvas.create_rectangle(self.dx, self.dy, self.dx + params.cell_size, self.dy + params.cell_size, fill="red")
		image = Image.open(os.path.join(params.base_dir, "images", "yellowPieceAlpha.png"))
		print(image.size)
		x = params.cell_size * 0.5
		y = x * image.size[1] / image.size[0]
		image = image.resize((int(x), int(y)), Image.ANTIALIAS)
		#print(params.piece_pos[0][0][1])
		self.imgs = []
		arg = 1
		size = "middle"
		for i in range(arg):
			print(self.dx)
			print(params.piece_pos[arg - 1][i][0])
			print(self.dy)
			print(params.piece_pos[arg - 1][i][1])
			print(self.dx + params.piece_pos[arg - 1][i][0])
			print(self.dy + params.piece_pos[arg - 1][i][1])
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
	def __init__(self, id, color):
		params.print_debug_entry_path("Player in __init__", id, color)
		self.id = id
		self.color = color
		#dx = 150
		#dy = 200
		self.set_my_pos()
		dx = self.dx
		dy = self.dy
		#params.player_pos[self.id][0] = self.dx
		#params.player_pos[self.id][1] = self.dy
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
	
	def repos(self):
		ptc = params.player_compress[self.id]
		for i in range(4):
			canvas.coords(params.pieces[self.id][i], self.dx + ptc[i][0], self.dy + ptc[i][1])
			canvas.itemconfig(self.expaned_pos[i], state = tk.HIDDEN)
			canvas.itemconfig(params.pieces[self.id][i], image = canvas.images["big"][self.id], tags = (str(self.id * 4 + i), "@-1"))
	
	def set_images(self):
		for i in range(4):
			canvas.itemconfig(params.pieces[self.id][i], image =  params.images["big"][self.id])
	
	def set_my_pos(self):
		self.dx = params.player_pos[self.id][0]
		self.dy = params.player_pos[self.id][1]
	
	def redraw_player(self):
		#params.player_pos[self.id][0] = self.dx
		#params.player_pos[self.id][1] = self.dy
		self.state = "normal"
		
		self.set_my_pos()
		dx = self.dx
		dy = self.dy
		cs = params.cell_size
		cfp = params.cells_for_player
		
		canvas.coords(self.home_site, dx + cs * 1.25, dy + cs * 1.75, dx + cs * 4.75, dy + cs * 4.25)
		
		#st = tk.HIDDEN
		#self.expaned_pos = np.zeros(4, dtype = np.uint8)
		canvas.coords(self.expaned_pos[0], dx + cs * 0.25, dy + cs * 0.5, dx + cs * 1.75, dy + cs * 1.5)
		canvas.coords(self.expaned_pos[1], dx + cs * 4.25, dy + cs * 0.5, dx + cs * 5.75, dy + cs * 1.5)
		canvas.coords(self.expaned_pos[2], dx + cs * 4.25, dy + cs * 4.5, dx + cs * 5.75, dy + cs * 5.5)
		canvas.coords(self.expaned_pos[3], dx + cs * 0.25, dy + cs * 4.5, dx + cs * 1.75, dy + cs * 5.5)
		
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
			canvas.coords(params.pieces[self.id][i], dx + ptc[i][0], dy + ptc[i][1])
	
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
		#print("__:__", item, tags)
		try:
			pos = int(tags[2].split("@")[1])
		except:
			pos = int(tags[1].split("@")[1])
		if pos == -1:
			self.bringOut()
			params.print_debug_entry_path("Player out off move with retuen !")
			return
		old_pos = pos
		#print("pos : ", pos)
		#print("pos + 1 : ", pos + 1)
		#print("len(params.path) : ", len(params.path))
		#print("int((pos + num) % len(params.path)) : ", int((pos + num) % len(params.path)))
		rt = self.check_for_active()
		print("here : ", rt)
		print("here : ", pid, pcid)
		if rt[0] == "not ok":
				canvas.after(500, params.change)
				print("not ok")
				return
		elif rt[0] == "ok" and rt[3][0] == pcid:
			pass
		elif rt[0] == "still_in":
			if pcid in (rt[2] + rt[3]):
				pass
			else:
				canvas.after(500, params.change)
				print("still_in")
				return
		elif rt[0] == "still_out":
			if pcid in rt[3]:
				pass
			else:
				canvas.after(500, params.change)
				print("still_out")
				return
		else:
			print("Else : ")
		for i in range(num + 1):
			#print("pos in : ", pos)
			if pos >= 0:
				pos = int((pos + 1) % len(params.path))
				if (pos + 1) == params.path_out[pid]:
					pos = (pid * -10) -2
			elif pos < 0:
				pos = pos - 1
				#if pos  == (pid * -10) + (len(params.win[0]) * -1) - 2 and i == num - 1:
				#	canvas.itemconfig( params.pieces[pid][pcid], state = tk.HIDDEN )
				#	params.print_debug_entry_path("Player out off with win and return !")
				#	return
				#else:
				#	pass
				
			#print("pos out : ", pos)
		#print("pos : ", pos)
		#print("pos : ", (pid * -10) + (len(params.win[0]) * -1) - 2)
		#print(pos < 0 and (pid * -10) + (len(params.win[0]) * -1) - 2 == pos)
		#print(pos < 0, (pid * -10) + (len(params.win[0]) * -1) - 2 == pos)
		if pos < 0 and (pid * -10) + (len(params.win[0]) * -1) - 2 == pos:
			canvas.itemconfig( params.pieces[pid][pcid], state = tk.HIDDEN )
			params.print_debug_entry_path("Player out off with win and return !")
			#params.dice_roll = -1
			params.change()
			return
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
		#active = 0
		#in_home = 0
		active_items = []
		inside_home = [] 
		for i in range(4):
			items = canvas.find_withtag(params.pieces[id][i])
			print("tags : ", id, id4, i, items)
			tags = canvas.gettags(items[0])
			print("tags : ", tags)
			try:
				pos = int(tags[1].split("@")[1])
			except:
				pos = int(tags[2].split("@")[1])
			num = params.dice_roll
			print("_:", pos, num)
			if pos == -1:
				#in_home += 1
				inside_home.append(i)
				continue
			for j in range(num+1):
				print("pos in : ", pos)
				if pos >= 0:
					pos = int((pos + 1) % len(params.path))
					if (pos + 1) == params.path_out[id]:
						pos = (id * -10) -2
					print("pos btn0 : ", pos)
				elif pos < 0:
					pos = pos - 1
				print("pos out : ", pos)
			print("pos:__:", pos  + 2 + (id * -10) )
			if pos  + 2 + (id * 10) > -8:
				#active += 1
				print("i : ", i)
				active_items.append(i)
		print("Active_items : ", active_items)
		print("In_home : ", inside_home)
		print("Active : ", active_items)
		if len(active_items) == 1:
			return ["ok", active_items[0], inside_home, active_items] # only one piece out so can be moved automatically
		elif (num == 5 and len(inside_home) > 0):
			return ["still_in", None, inside_home, active_items] # reamain still because there are more that 0 pieces inside the home and dice_roll is 5 i.e dice trow is 6
		elif len(active_items) > 0:
			return ["still_out", None, inside_home, active_items] # ramain still because more than one pieces outside
		else:
			return ["not ok", None, inside_home, active_items]
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
		if not params.focused and not params.game_started:
			params.print_debug_entry_path("Player is out off makeMove because canvas is not focused!")
			return
		print("Player in makeMove !", event)
		if params.dice_roll == -1:
			params.print_debug_entry_path("Player out off makeMove with return !")
			return 
		if "<class 'tkinter.Event'>" == str(type(event)):
			params.current = tk.CURRENT
		else:
			params.current = "myCurrentTag"
		#	return
		print("params.current : ", params.current)
		
		print(canvas.find_withtag(params.current))
		items = canvas.find_withtag(params.current)
		if len(items) > 1:
			print("	Problem !")
		tags = canvas.gettags(params.current)
		print("tags : ", tags, params.dice_pos)
		id = int(tags[0])
		pid = id //4
		pcid = int(id % 4)
		if not pid == params.dice_pos:
			params.print_debug_entry_path("Player out off makeMove with return because selected piece is not belong to current player !")
			print("!00!")
			return
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
				print("!00!")
				return
			#self.bringOut(id)
		else:
			rt = self.move(id, params.dice_roll)
			if rt == "ok":
				params.change()
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
	
	def redraw(self):
		for i in range(6):
			canvas.coords(self.dice_roll, self.pos[0], self.pos[1])
			coords.itemconfig(self.dice_roll, image = self.get_images(i, 0.75, 0.75), state = tk.HIDDEN)
	
	def repos(self):
		self.pos = [params.cell_size * params.cells_for_player // 2, params.cell_size * params.cells_for_player // 2]
		for i in range(6):
			canvas.coords(self.dice_roll, self.pos[0], self.pos[1])
	
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
		if params.debug:
			params.dice_roll = params.debug_roll[params.roll_id]
			params.roll_id += 1
		else:
			roll = int(int(random.random() * 1000) % 6)
			params.dice_roll = roll
		if params.dice_roll == 5:
			params.double = True
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
		self.mx = 15
		self.my = 15
		self.width = 0
		self.height = 0
		
		self.font1 = tkFont.Font(root=root, size=20)
		params.menuFont1 = self.font1
		self.font2 = tkFont.Font(root=root, size=15)
		params.menuFont2 = self.font2
		self.font3 = tkFont.Font(root=root, size=15)
		params.menuFont3 = self.font3
		self.font4 = tkFont.Font(root=root, size=20)
		params.menuFont4 = self.font4
		
		self.menu()
		self.Options()
		self.showMenu()
		
		params.toggleMenu = self.toggle
		self.hidden = False
	
	def reconfig(self):
		#x = root.winfo_rootx()+ params.width - 4
		x = root.winfo_rootx() - 4
		y = root.winfo_rooty() - 31
		if x + self.width + params.width + 10 <= params.screen_width:
			x += params.width
		else:
			x -= (self.width + 8)
		#print("board : ", x, y)
		if y < 0:
			y= str(y)
		else:
			y = "+" + str(y)
		#print("+" + str(x) + "+" + str(y) + "")
		self.top.geometry("" + str(self.width) + "x" + str(self.height) + "+" + str(x) + str(y) + "")
		self.top.lift()
	
	def nothing(self):
		pass
	
	def toggle(self):
		if self.hidden == True:
			self.top.deiconify()
			self.hidden = False
		else:
			self.top.withdraw()
			self.hidden = True
	
	def menu(self):
		self.master = tk.Toplevel()
		#self.master.withdraw()
		self.master.title("Menu")
		#self.top.attributes('-topmost', 'true')
		self.width1 = 200
		self.height1 = 320
		#self.reconfig()
		self.master.protocol("WM_DELETE_WINDOW", self.nothing)
		self.top = self.master
		
		self.newGame = tk.Button(self.master, text="New Game", command= self.freshStartGame)
		self.newGame.place(x = self.mx, y = self.my)
		params.styleButton(self.newGame, 1)
		
		self.options = tk.Button(self.master, text="Options", command= self.showOptions)
		self.options.place(x = self.mx, y = self.my+75)
		params.styleButton(self.options, 1)
		
		self.help = tk.Button(self.master, text="Help", command= self.help)
		self.help.place(x = self.mx, y = self.my+150)
		params.styleButton(self.help, 1)
		
		self.about = tk.Button(self.master, text="About", command= self.about)
		self.about.place(x = self.mx, y = self.my+225)
		params.styleButton(self.about, 1)
	
	def showMenu(self):
		self.master.deiconify()
		self.top.withdraw()
		self.top = self.master
		self.width = self.width1
		self.height = self.height1
		self.reconfig()
	
	def freshStartGame(self):
		self.options.config(state = tk.DISABLED)
		params.game_started = True
		#board.dice.repos()
		board.setPlayers()
		board.players[params.dice_pos].compress()
		board.dice_pos = 0
		params.dice_pos = 0
		board.dice.move(params.player_pos[params.dice_pos][0], params.player_pos[params.dice_pos][1])
		board.players[params.dice_pos].expand()
		#board.repos()
		params.toggle()
	
	def Stop(self):
		pass
	
	def Continue(self):	
		pass
	
	def setAuto(self):
		params.auto = True
	
	def unsetAuto(self):
		params.auto = False
	
	def Options(self):
		self.master2 = tk.Toplevel()
		self.master2.title("Set Options!")
		self.top = self.master2
		self.master2.withdraw()
		#self.top.attributes('-topmost', 'true')
		self.width2 = 250
		self.height2 = 320
		#self.reconfig()
		self.master2.protocol("WM_DELETE_WINDOW", self.nothing)
		
		self.scrollbar = tk.Scrollbar(self.master2, orient=tk.VERTICAL)
		self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.canvas = tk.Canvas(self.master2, width = self.width2, height = self.height2, yscrollcommand = self.scrollbar.set, scrollregion=(0, 0, self.width2, 1000))
		self.canvas.pack()
		self.scrollbar.config(command = self.canvas.yview)
		
		self.backUp = tk.Button(self.canvas, text = "Back", command = self.showMenu)
		self.canvas.create_window(self.mx + 10, self.my, window = self.backUp, anchor = tk.NW)
		params.styleButton(self.backUp, 1)
		
		
		self.debug = Int()
		self.debug.set(0)
		self.debug.trace("w", self.callback_1)
		self.debugState = tk.Checkbutton(self.canvas, text = "DEBUG(" + u"\u2714" + "/" + u"\u2718" + ")", variable = self.debug)
		self.canvas.create_window(self.mx, self.my + 75, window = self.debugState, anchor = tk.NW)
		params.styleCheckbutton(self.debugState, 1)
		
		self.auto = Int()
		self.auto.set(0)
		self.auto.trace("w", self.callback_2)
		self.autoState = tk.Checkbutton(self.canvas, text = "AUTO(" + u"\u2714" + "/" + u"\u2718" + ")", variable = self.auto)
		self.canvas.create_window(self.mx, self.my + 110, window = self.autoState, anchor = tk.NW)
		params.styleCheckbutton(self.autoState, 1)
		
		self.widthLabel = tk.Label(self.canvas, text = "Canvas_width")
		self.canvas.create_window(self.mx - 5, self.my + 155, window = self.widthLabel, anchor = tk.NW)
		params.styleLabel(self.widthLabel, 1)
		self.widthVar = Int()
		self.widthVar.set(params.width)
		self.widthVar.trace("w", self.callback1)
		self.widthEntry = tk.Entry(self.canvas, textvariable = self.widthVar)
		self.canvas.create_window(self.mx + 155, self.my + 155, window = self.widthEntry, anchor = tk.NW)
		params.styleEntry(self.widthEntry ,1)
		
		self.heightLabel = tk.Label(self.canvas, text = "Canvas_height")
		self.canvas.create_window(self.mx - 5, self.my + 200, window = self.heightLabel, anchor = tk.NW)
		params.styleLabel(self.heightLabel, 1)
		self.heightVar = Int()
		self.heightVar.set(params.height)
		self.heightVar.trace("w", self.callback2)
		self.heightEntry = tk.Entry(self.canvas, textvariable = self.heightVar)
		self.canvas.create_window(self.mx + 155, self.my + 200, window = self.heightEntry, anchor = tk.NW)
		params.styleEntry(self.heightEntry ,1)
		
		self.cellSizeLabel = tk.Label(self.canvas, text = "cell_size")
		self.canvas.create_window(self.mx - 5, self.my + 250, window = self.cellSizeLabel, anchor = tk.NW)
		params.styleLabel(self.cellSizeLabel, 1)
		self.cellSizeVar = Int()
		self.cellSizeVar.set(params.cell_size)
		self.cellSizeVar.trace("w", self.callback3)
		self.cellSizeEntry = tk.Entry(self.canvas, textvariable = self.cellSizeVar)
		self.canvas.create_window(self.mx + 155, self.my + 250, window = self.cellSizeEntry, anchor = tk.NW)
		params.styleEntry(self.cellSizeEntry ,1)
		
		self.cellsForPlayerLabel = tk.Label(self.canvas, text = "cells_for_players")
		self.canvas.create_window(self.mx - 5, self.my + 300, window = self.cellsForPlayerLabel, anchor = tk.NW)
		params.styleLabel(self.cellsForPlayerLabel, 1)
		self.cellsForPlayerVar = Int()
		self.cellsForPlayerVar.set(params.cells_for_player)
		self.cellsForPlayerVar.trace("w", self.callback4)
		self.cellsForPlayerEntry = tk.Entry(self.canvas, textvariable = self.cellsForPlayerVar)
		self.canvas.create_window(self.mx + 155, self.my + 300, window = self.cellsForPlayerEntry, anchor = tk.NW)
		params.styleEntry(self.cellsForPlayerEntry ,1)
		
		self.backDown = tk.Button(self.canvas, text = "Back", command = self.showMenu)
		self.canvas.create_window(self.mx + 10, self.my + 500, window = self.backDown, anchor = tk.NW)
		params.styleButton(self.backDown, 1)
		
		#print("self.canvas.bbox(tk.ALL) : ", self.canvas.bbox(tk.ALL))
		#You can use the bbox method to get a bounding box for a given object, or a group of objects;
		#canvas.bbox(ALL) returns the bounding box for all objects on the canvas:
		print("canvas_scrollbar0 : ", self.canvas.bbox(tk.ALL))
		self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
	
	def showOptions(self):
		self.master2.deiconify()
		self.top.withdraw()
		self.top = self.master2
		self.width = self.width2
		self.height = self.height2
		self.reconfig()
	
	def callback_1(self, *args):
		print("debug : ", self.debug.get())
		if int(self.debug.get()) == 1:
			params.debug = True
		else:
			params.debug = False
	
	def callback_2(self, *args):
		print("auto : ", self.auto.get())
		if int(self.auto.get()) == 1:
			params.auto = True
		else:
			params.auto = False
	
	def callback1(self, *args):
		params.width = int(self.widthVar.get())
		canvas.config(width = self.widthVar.get())
		print("redraw_completed1!")
	
	def callback2(self, *args):
		params.height = self.heightVar.get()
		canvas.config(height = self.heightVar.get())
		print("redraw_completed2!")
	
	def callback3(self, *args):
		params.cell_size = self.cellSizeVar.get()
		params.set_player_pos()
		params.set_extra_path()
		params.setImages(canvas)
		board.redraw_board()
		for i in range(4):
			board.players[i].set_images()
			board.players[i].redraw_player()
		print("redraw_completed3!", type(self.cellSizeVar.get()))
	
	def callback4(self, *args):
		params.cells_for_player = self.cellsForPlayerVar.get()
		params.set_player_pos()
		params.set_extra_path()
		params.setImages(canvas)
		board.redraw_board()
		for i in range(4):
			board.players[i].set_images()
			board.players[i].redraw_player()
		print("redraw_completed4!")
	
	def help(self):
		print("Help!")
	
	def about(self):
		print("About!")


def on_configure(event):
	gui.reconfig()

params = Params()

root = tk.Tk()
params.screen_width = root.winfo_screenwidth()
params.screen_height = root.winfo_screenheight()
root.title("my Ludo Game")
root.geometry("+0+0")
root.bind("<Configure>", on_configure)

canvas = tk.Canvas(root, width = params.width, height = params.height, bg="#666666")
canvas.pack()
canvas.focus_set()
params.setImages(canvas)

gui = GUI()
board = Board(params.marginX, params.marginY)

print("tk.StringVar : ", tk.StringVar)
#plr = Player(0, params.marginX, params.marginY, "#ff0000")
#plr.expand()
#dice = Dice()
params.debug_roll = test.test1[:]

params.setGUI()
#root.protocol('WM_TAKE_FOCUS', on_focus_in())
root.mainloop()