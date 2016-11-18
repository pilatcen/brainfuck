#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#





import sys
import image_png
from argparse import ArgumentParser


class Error(Exception):
	"""Vyjimka oznamujici kritickou chybu, pri ktere neni mozne pokracovat"""
	def __init__(self, message):
		self.message = message

class EndOfImage(Exception):
	""" Výjimka oznamující, že Instruction Pointer je na konci obrazku """
	pass



class BrainFuck:
	"""Interpretr jazyka brainfuck."""
	
	def __init__(self, data, memory=b'\x00', memory_pointer=0):
		"""Inicializace interpretru brainfucku."""
		
		try:
			if (memory_pointer < 0):
				raise (Error("memory_pointer nemuze byt zaporny!"))
		except (Error) as err:
			print (err.message)
			sys.exit(1)
		
		
		# data programu
		self.__data_ = data
		
		# inicializace proměnných
		self.__output_buffer_=list()
		self.__memory_=bytearray(memory)
		self.__MEM_SIZE_=len (memory)
		self.__memory_pointer_ = memory_pointer
		
		self.__input_buffer_=self.__fillInputBuffer_()
		self.__interpreter_()
		
		self.output=''.join (self.__output_buffer_)
		self.memory_pointer=self.__memory_pointer_
			
	#
	# pro potřeby testů
	#
	
	
	#############################################################
	#							PUBLIC							#
	#############################################################
	
	def get_memory(self):
		# Nezapomeňte upravit získání návratové hodnoty podle vaší implementace!
		return bytes (self.__memory_)
	
	def printMemory (self):
		""" pro vlastni debugovaci ucely """
		for byte in self.__memory_:
			print ("["+str(byte)+"]", end='');
		print()
		sys.stdout.flush()
	
	
	
	#############################################################
	#							PRIVATE							#
	#############################################################
	
	def __fillInputBuffer_(self):
		"""Naplni input_buffer, pokud se v kodu vyskytuje prikaz !"""
		
		input_buffer = list()
		
		try:
			exclamation_pos=self.__data_.index("!")
		except (ValueError):
			pass
		else:
			for i in range(exclamation_pos+1, len(self.__data_)):
				input_buffer.append(self.__data_[i])
		return (input_buffer)
	
	def __findMatchingRightBrake_(self, from_position):
		"""Najde pravou zavorku k leve."""
		
		left_brakes=1
		right_brakes=0
		
		for (i, char) in enumerate(self.__data_[from_position:]):
			if (char == '['):
				left_brakes+=1
			elif (char == ']'):
				right_brakes+=1
			if (right_brakes == left_brakes):
				return (i+from_position)
		return (-1)

	def __findMatchingLeftBrake_(self, from_position):
		"""Najde levou zavorku k prave."""
		
		left_brakes=0
		right_brakes=1
	
		for (i, char) in enumerate(self.__data_[from_position::-1]):
			if (char == ']'):
				right_brakes+=1
			elif (char == '['):
				left_brakes+=1
			if (left_brakes == right_brakes):
				return (from_position-i)
		return (-1)
	
	
	
	#################################
	#		Brainfuck commands		#
	#################################
	
	def __next_(self):
		if (self.__memory_pointer_+1==self.__MEM_SIZE_):
			self.__memory_.append (0)
			self.__MEM_SIZE_+=1
		self.__memory_pointer_+=1
		
	def __prev_(self):
		if (self.__memory_pointer_!=0):
			self.__memory_pointer_-=1
		
	def __increment_(self):
		if (self.__memory_[self.__memory_pointer_] < 255):
			self.__memory_[self.__memory_pointer_]+=1
		else:
			self.__memory_[self.__memory_pointer_]=0
	
	def __decrement_(self):
		if (self.__memory_[self.__memory_pointer_] > 0):
			self.__memory_[self.__memory_pointer_]-=1;
		else:
			self.__memory_[self.__memory_pointer_]=255
	
	def __manageInput_(self):
		if (len (self.__input_buffer_) != 0):
			temp=self.__input_buffer_.pop(0)
		else:
			temp=sys.stdin.read(1)
		self.__memory_[self.__memory_pointer_]=ord(temp)
	
	def __leftBrake_(self, i):
		matching_right_brake_position=self.__findMatchingRightBrake_(i+1)
		if (matching_right_brake_position == -1):
			raise (Error("syntax error at character "+str(i)+", missing right brake"))
		if (self.__memory_[self.__memory_pointer_] == 0):
			return (matching_right_brake_position)
		else:
			return (i)
	
	def __display_(self):
		self.__output_buffer_.append (chr (self.__memory_[self.__memory_pointer_]))
	
	def __rightBrake_(self, i):
		matching_left_brake_position=self.__findMatchingLeftBrake_(i-1)
		if (matching_left_brake_position == -1):
			raise (Error("syntax error at character "+str(i)+", missing left brake"))
		if (self.__memory_[self.__memory_pointer_] != 0):
			return (matching_left_brake_position)
		else:
			return (i)
	
	
	
	#####################################
	#		Brainfuck interpreter		#
	#####################################
	
	def __interpreter_(self):
		"""Interpretr jazyka Brainfuck"""
		
		i=0
		try:
			while (i < len(self.__data_)):
				command=self.__data_[i]
				if (command == '>'):
					self.__next_()
				elif (command == '<'):
					self.__prev_()
				elif (command == '+'):
					self.__increment_()
				elif (command == '-'):
					self.__decrement_()
				elif (command == '.'):
					self.__display_()
				elif (command == ','):
					self.__manageInput_()
				elif (command == '['):
					i=self.__leftBrake_(i)
				elif (command == ']'):
					i=self.__rightBrake_(i)
				elif (command == '!'):
					break
				i+=1
				
		except (Error) as err:
			print (err.message)
			sys.exit(1)
			
		return 0
	
	
#########################################
#				BrainCore				#
#########################################

class BrainCore():
	""" Rodicovska trida pro Brainloller a Braincopter """
	def __init__(self, filename):
		self.__image_=image_png.PngReader(filename)
		self.data = self._pixelsToCommands(self.__image_.rgb, self.__image_.getWidth(), self.__image_.getHeight())
		self.program = BrainFuck(self.data)
	
	def _pixelsToCommands(self, rgb_matrix, width, height):
		""" Prevede jednotlive pixely v obrazku na prikazy brainfucku, tato metoda bude prekryta """
		pass
	
	def _step(self, position, direction, width, height):
		""" udela 1 krok """
		
		if (
			(position['x'] == (width-1) and direction == 1) or
			(position['x'] == 0 and direction == 3) or
			(position['y'] == (height-1) and direction == 2) or
			(position['y'] == 0 and direction == 4)
			):
				raise (EndOfImage())
			
		if (direction == 1):
			position['x']+=1
		elif (direction == 2):
			position['y']+=1
		elif (direction == 3):
			position['x']-=1
		elif (direction == 4):
			position['y']-=1
		
		return (position)
	
	def _setIPDirection(self, old_direction, rotation):
		""" nastavi smer Instruction Pointeru """
		if (rotation == "right"):
			return (old_direction+1)
		elif (rotation == "left"):
			return (old_direction-1)
	

#########################################
#				BrainLoller				#
#########################################

class BrainLoller(BrainCore):
	"""Třída pro zpracování jazyka brainloller."""
	
	def __init__(self, filename):
		"""Inicializace interpretru brainlolleru."""
		BrainCore.__init__(self, filename)
	
	
	def _pixelsToCommands(self, rgb_matrix, width, height):
		""" Prevede jednotlive pixely v obrazku na prikazy brainfucku """
		pos={'y':0,'x':0}
		#smery: 1 - doleva, 2 - dolu, 3 - doprava, 4 - nahoru
		direction=1
		commands = []
		
		while (True):
			if (rgb_matrix[pos['y']][pos['x']] == (255,0,0)):
				commands.append('>')
			elif (rgb_matrix[pos['y']][pos['x']] == (128,0,0)):
				commands.append('<')
			elif (rgb_matrix[pos['y']][pos['x']] == (0,255,0)):
				commands.append('+')
			elif (rgb_matrix[pos['y']][pos['x']] == (0,128,0)):
				commands.append('-')
			elif (rgb_matrix[pos['y']][pos['x']] == (0,0,255)):
				commands.append('.')
			elif (rgb_matrix[pos['y']][pos['x']] == (0,0,128)):
				commands.append(',')
			elif (rgb_matrix[pos['y']][pos['x']] == (255,255,0)):
				commands.append('[')
			elif (rgb_matrix[pos['y']][pos['x']] == (128,128,0)):
				commands.append(']')
			elif (rgb_matrix[pos['y']][pos['x']] == (0,255,255)):
				direction=self._setIPDirection(direction, "right")
			elif (rgb_matrix[pos['y']][pos['x']] == (0,128,128)):
				direction=self._setIPDirection(direction, "left")
			
			try:
				pos=self._step(pos, direction, width, height)
			except (EndOfImage):
				return (''.join(commands))
		
		
#########################################
#				BrainCopter				#
#########################################

class BrainCopter(BrainCore):
	"""Třída pro zpracování jazyka braincopter."""
	
	def __init__(self, filename):
		"""Inicializace interpretru braincopteru."""
		BrainCore.__init__(self, filename)
	
	def _pixelsToCommands(self, rgb_matrix, width, height):
		""" Prevede jednotlive pixely v obrazku na prikazy brainfucku """
		pos={'y':0,'x':0}
		#smery: 1 - doleva, 2 - dolu, 3 - doprava, 4 - nahoru
		direction=1
		commands = []
		
		while (True):
			
			command_code=(65536 * rgb_matrix[pos['y']][pos['x']][0] + 256 * rgb_matrix[pos['y']][pos['x']][1] + rgb_matrix[pos['y']][pos['x']][2]) % 11
			
			if (command_code == 0):
				commands.append('>')
			elif (command_code == 1):
				commands.append('<')
			elif (command_code == 2):
				commands.append('+')
			elif (command_code == 3):
				commands.append('-')
			elif (command_code == 4):
				commands.append('.')
			elif (command_code == 5):
				commands.append(',')
			elif (command_code == 6):
				commands.append('[')
			elif (command_code == 7):
				commands.append(']')
			elif (command_code == 8):
				direction=self._setIPDirection(direction, "right")
			elif (command_code == 9):
				direction=self._setIPDirection(direction, "left")
			
			try:
				pos=self._step(pos, direction, width, height)
			except (EndOfImage):
				return (''.join(commands))

def main():
	
	parser = ArgumentParser()
	group = parser.add_mutually_exclusive_group()
	parser.add_argument('--version', action='version', version='1.0', help="show program's version number and exit")
	
	group.add_argument("-l", "--brainloller",
					action="store_true",
					default=False,
					help="File is brainloller source code.")
	group.add_argument("-c", "--braincopter",
					action="store_true",
					default=False,
					help="File is braincopter source code.")
	parser.add_argument("file", help="File with brainfuck/brainloller/braincopter source code. For brainloller or braincopter file must be png image.")
	
	args = parser.parse_args()
	
	if (args.brainloller == True):
		loller = BrainLoller(args.file)
		print (loller.program.output)
	elif (args.braincopter == True):
		copter = BrainCopter(args.file)
		print (copter.program.output)
	else:
		with open(args.file, 'r') as datainput:
			data=datainput.read()
		brainfuck = BrainFuck(data)
		print (brainfuck.output)
		
	
if __name__ == '__main__':
	main()
