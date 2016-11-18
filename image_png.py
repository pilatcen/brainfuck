#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zlib

class PNGWrongHeaderError(Exception):
	"""Výjimka oznamující, že načítaný soubor zřejmě není PNG-obrázkem."""
	pass


class PNGNotImplementedError(Exception):
	"""Výjimka oznamující, že PNG-obrázek má strukturu, kterou neumíme zpracovat."""
	pass

class PNGError(Exception):
	"""Výjimka oznamující, že PNG-obrázek je pravděpodobně poškozen."""
	pass


class PngReader():
	"""Třída pro práci s PNG-obrázky."""
	
	def __init__(self, filepath):
		
		self.__image_file_=open (filepath, 'rb')
		
		self.__width_=None
		self.__height_=None
		self.__png_filters_=None
		self.__raw_data_=bytearray()
		self.__raw_rgb_matrix_=None
		
		# RGB-data obrázku jako seznam seznamů řádek,
		#   v každé řádce co pixel, to trojce (R, G, B)
		self.rgb = []
		
		self.__run_()
		
		self.__image_file_.close()
		
	
	def getWidth(self):
		return (self.__width_)
	
	def getHeight(self):
		return (self.__height_)
	
	
	
	def __checkHeader_(self):
		""" Zkontroluje hlavicku obrazku """
		image_header=self.__image_file_.read(8)
		if (image_header != b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'):
			self.__image_file_.close()
			raise PNGWrongHeaderError()
	
	
	def __parseChunks_(self):
		""" Nacte strukturu chunku """
		
		raw_data=bytearray()
		
		while (True):
			chunk_length=int.from_bytes(self.__image_file_.read(4), byteorder='big')
			chunk_type=self.__image_file_.read(4)
			chunk_data=self.__image_file_.read(chunk_length)
			chunk_crc=int.from_bytes(self.__image_file_.read(4), byteorder='big')
			
			#kontrola CRC 
			if (chunk_crc != zlib.crc32(chunk_type + chunk_data)):
				self.__image_file_.close()
				raise PNGError()
				
			#IDAT muze byt jen jeden a musi byt prvni po hlavicce
			if (chunk_type == b'IHDR'):
				if ((self.__width_ != None) or (self.__height_ != None)):
					self.__image_file_.close()
					raise PNGError()
				
				#IHDR musi mit delku 13
				if (chunk_length != 13):
					self.__image_file_.close()
					raise PNGError()
				
				self.__width_=int.from_bytes(chunk_data[0:4], byteorder='big')
				self.__height_=int.from_bytes(chunk_data[4:8], byteorder='big')
				
				#jine png nepodporujeme :)
				if (chunk_data[8:13] != b'\x08\x02\x00\x00\x00'):
					self.__image_file_.close()
					raise PNGNotImplementedError()
			
			
			elif (chunk_type == b'IDAT'):
				raw_data.extend(chunk_data)
			elif (chunk_type == b'IEND'):
				return raw_data
			
		
	def __run_(self):
		""" Naplni pole self.rgb dekomprimovanymi a odfiltrovanymi daty """
		self.__checkHeader_()
		raw_data=self.__parseChunks_()
		self.__createMatrixfromRawImage_(zlib.decompress(raw_data))
		
		for i in range (0, self.__height_):
			if (self.__png_filters_[i] == 0):
				#filtr 0 nic nedela
				self.rgb.append (self.__raw_rgb_matrix_[i])
			elif (self.__png_filters_[i] == 1):
				self.rgb.append (self.__filter1_ (i))
			elif (self.__png_filters_[i] == 2):
				self.rgb.append (self.__filter2_ (i))
			elif (self.__png_filters_[i] == 3):
				self.rgb.append (self.__filter3_ (i))
			elif (self.__png_filters_[i] == 4):
				self.rgb.append (self.__filter4_ (i))
		
		
	def __createMatrixfromRawImage_(self, raw_data):
		"""
			Z dekomprimovanych dat vytvori 2D matrix a pole 
			self.__png_filters_ naplni cisly filtru pro kazdy radek 
		
		"""
		row_width=1+(self.__width_*3)
		
		png_filters=[]
		matrix=[]
		
		for i in range(0,self.__height_):
			png_filters.append(raw_data[i*row_width])
			raw_row=raw_data[(i*row_width)+1:((i+1)*row_width)]
			
			row=[]
			for j in range(0, row_width-1, 3):
				row.append((raw_row[j], raw_row[j+1], raw_row[j+2]))
				
			matrix.append(row)
			
		self.__raw_rgb_matrix_=matrix
		self.__png_filters_=png_filters
		
		
	def __filter1_(self, row_number):
		"""
			Filtr c. 1
			Recon(x) = Filt(x) + Recon(a)
		"""
		line = []
		row=self.__raw_rgb_matrix_[row_number]
		
		for i in range (0, self.__width_):
			if (i == 0):
				line.append (row[i])
			else:
				line.append (self.__sum_(row[i],line[i-1]))
		
		return (line)
	
	def __filter2_(self, row_number):
		"""
			Filtr c. 2
			Recon(x) = Filt(x) + Recon(b)
		"""
		row=self.__raw_rgb_matrix_[row_number]
		
		if (row_number != 0):
			line = []
			up_row=self.rgb[row_number-1]
			
			for i in range (0, self.__width_):
				line.append (self.__sum_(row[i], up_row[i]))
			
			return (line)
			
		else:
			return (row)
	
	def __filter3_(self, row_number):
		"""
			Filtr c. 3
			Recon(x) = Filt(x) + (Recon(a) + Recon(b)) // 2 
		"""
		line = []
		row=self.__raw_rgb_matrix_[row_number]
		
		if (row_number == 0):
			for i in range (0, self.__width_):
				if (i == 0):
					line.append (row[i])
				else:
					line.append (self.__sum_(row[i], self.__divide_(line[i-1])))
		else:
			up_row=self.__rgb[row_number-1]
			
			for i in range (0, self.__width_):
				if (i == 0):
					line.append (self.__sum_(row[i], self.__divide_(up_row[i])))
				else:
					line.append (self.__sum_(row[i], (self.__divide_(self.__sum_(line[i-1], up_row[i])))))
					
		return (line)
	
	
	
	def __filter4_(self, row_number):
		"""
			Filtr c. 4
			Recon(x) = Filt(x) + PaethPredictor(Recon(a), Recon(b), Recon(c)) 
		"""
		
		line = []
		row=self.__raw_rgb_matrix_[row_number]
		
		for i in range (0, self.__width_):
			a=(0,0,0)
			b=(0,0,0)
			c=(0,0,0)
			x=[0,0,0]
			
			if (row_number != 0):
				b=self.rgb[row_number-1][i]
			if (i!=0):
				a=line[i-1]
			if (i!=0 and row_number != 0):
				c=self.rgb[row_number-1][i-1]
				
			for j in range (0, 3):
				x[j]=self.__paeth_(a[j], b[j], c[j])
				
			line.append (self.__sum_(row[i], x))
		
		return (line)
	
	
	def __sum_(self, x, y):
		""" Secte 2 pixely mod 256 """
		return ((x[0]+y[0])%256, (x[1]+y[1])%256, (x[2]+y[2])%256)
		
	def __divide_(self, x):
		""" Vsechny slozky pixelu deli 2mi """
		return (((x[0] // 2), (x[1] // 2), (x[2] // 2)))
	
	def __paeth_(self, a, b, c):
		""" PaethPredictor """
		p = a + b - c
		pa = abs(p - a)
		pb = abs(p - b)
		pc = abs(p - c)
		if pa <= pb and pa <= pc:
			return a
		elif pb <= pc:
			return b
		else:
			return c
	

def main():
	PngReader("test_data/sachovnice.png")
	
		
if __name__ == '__main__':
	main()
		
