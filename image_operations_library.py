#!/Users/hannesbajohr/opt/anaconda3/bin/python
from PIL import Image, ImageOps
import sys
from os import listdir
import os
from os.path import isfile, join
import glob
import imageio
import urllib.request


def get_files (path):
	files =[]
	if path[-1] != "/":
		sys.exit("End the path with a '/'.")
	for f in listdir(path):
		if isfile(path + f):
			files.append(path + f)
	try:
		files.remove(path+".DS_Store")
	except:
		pass
	return(files)

def cropper(path,left,top,right,bottom):
	files=get_files(path)

	for file_img in files:
		img = Image.open(file_img)
		area = (left, top, right, bottom)
		cropped_img = img.crop(area)
		cropped_img.save(path + "cropped/" + os.path.basename(os.path.normpath(file_img)), "JPEG", quality=100, subsampling=0)

def pad_img(path):
	files=get_files(path)
	for file_img in files:
		if os.path.isfile(path + "padded_square/"+ os.path.basename(os.path.normpath(file_img))):
			pass
		else:
			try: 
				img = Image.open(file_img)
				width, height = img.size
				if not os.path.exists(path+"padded_square"):
					os.makedirs(path+"padded_square")
				if width == height:
					img.save(path + "padded_square/" + os.path.basename(os.path.normpath(file_img)), "JPEG", quality=100, subsampling=0)
				elif width > height:
					result = Image.new(img.mode, (width, width), 0)
					result.paste(img, (0, (width - height) // 2))
					result.save(path + "padded_square/" + os.path.basename(os.path.normpath(file_img)), "JPEG", quality=100, subsampling=0)
				else:
					result = Image.new(img.mode, (height, height), 0)
					result.paste(img, ((height - width) // 2, 0))
					result.save(path + "padded_square/" + os.path.basename(os.path.normpath(file_img)), "JPEG", quality=100, subsampling=0)
				print("processed: " + os.path.basename(os.path.normpath(file_img)))
			except:
				print("Error with file " + file_img)

def fit_to_size(path, size):
	files=get_files(path)
	for file_img in files:
		if os.path.isfile(path + "fit_to_size/"+ os.path.basename(os.path.normpath(file_img))):
			print(os.path.basename(os.path.normpath(file_img)) + " exists already")
			pass
		else:
			if not os.path.exists(path + "fit_to_size"):
				os.makedirs(path + "fit_to_size")
			try: 
				img = Image.open(file_img)
				fit_and_resized_image = ImageOps.fit(img, (size, size), Image.ANTIALIAS) #oder: fit_and_resized_image = file_img.resize((size, size), Image.ANTIALIAS)
				fit_and_resized_image.save(path + "fit_to_size/" + os.path.basename(os.path.normpath(file_img)), "JPEG", quality=100, subsampling=0)
			except:
				print("Error with: " + os.path.basename(os.path.normpath(file_img)))

def convert_to_rgb(path):
	files=get_files(path)
	for file_img in files:
		img = Image.open(file_img)
		rgbimg = Image.new("RGB", img.size)
		rgbimg.paste(img)
		rgbimg.save(path + "converted_to_rgb/" + os.path.basename(os.path.normpath(file_img)), "JPEG", quality=100, subsampling=0)

def convert_to_grayscale(path):
	files=get_files(path)
	for file_img in files:
		img = Image.open(file_img).convert('LA')
		if not os.path.exists(path+"converted_to_rgb/"):
					os.makedirs(path+"converted_to_rgb")
		img.save(path + "converted_to_grayscale/" + os.path.basename(os.path.normpath(file_img)), "PNG")

def slice_in_grid (path, no_width, no_height):
	k=0
	files=get_files(path)
	for file_img in files:
		print("Processing " + file_img)
		img = Image.open(file_img)
		imgwidth, imgheight = img.size
		for i in range(0,imgheight,round(imgheight/no_height)):
			for j in range(0,imgwidth,round(imgwidth/no_width)):
				box = (j, i, j+(round(imgwidth/no_width)), i+(round(imgheight/no_height)))
				a = img.crop(box)
				if not os.path.exists(path+"sliced_in_grid"):
					os.makedirs(path+"sliced_in_grid")
				a.save(path + "sliced_in_grid/" + str(i) + "-" + str(j) + "-" + os.path.basename(os.path.normpath(file_img)) + ".jpg", "JPEG", quality=100, subsampling=0)
				k +=1

def make_animation(path):
	fp_in = path + "*.*"
	fp_out = path + "OUTPUT.gif"

	img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
	img.save(fp=fp_out, format='GIF', append_images=imgs,save_all=True, duration=100, loop=0)

def remove_landscape(path):
	files=get_files(path)
	for file_img in files:
		img = Image.open(file_img)
		width, height = img.size
		if width > height:
			os.remove(file_img)
			print("Removed " + file_img)
		if width == height:
			os.remove(file_img)
			print("Removed " + file_img)

def compare_if_img_same(path):
	files=get_files(path)
	print("Comparing…")
	try:
		for i in range (0, len(files)):
			im1 = Image.open(files[i])
			im2 = Image.open(files[i+1])
			if list(im1.getdata()) == list(im2.getdata()):
				print("Identical: " + files[i] + " and " + files[i+1] + "\n")
	except:
		print("Error: " + files[i])

def convert_mp4_to_GIF(filename, output):
	import ffmpy
	ff = ffmpy.FFmpeg(
		inputs = {filename : None},
		outputs = {output + ".gif" : None})
	ff.run

def download_images_from_ISBNs(ISBN_file, standard_image_URL, extension, local_download_path):
	f=open(ISBN_file, 'r', encoding='utf-8-sig')
	URL_list = f.readlines()
	if not os.path.exists(local_download_path):
		os.makedirs(local_download_path)
	for ISBN in URL_list:
		ISBN = ISBN[0:-1]
		URL = standard_image_URL + ISBN + extension
		print((URL) + ": "),
		try:
			if os.path.isfile(local_download_path + ISBN + extension):
				print("already exists")				
			else:
				with urllib.request.urlopen(URL) as response, open(local_download_path + os.path.basename(os.path.normpath(ISBN)) + ".jpg", "wb") as out_file: 
					out = response.read()
					out_file.write(out)
					#print("saved")
		except:
			print("no image")
	print("no image total: " + str(x))

def list_img_too_wide(path):
	files=get_files(path)
	for file_img in files:
		img = Image.open(file_img)
		#print(file_img)
		#print(img.getpixel((4,4)))
		if img.getpixel((175,55)) == (255, 255, 255):
			if not os.path.exists(path+"check"):
				os.makedirs(path+"check")
			os.rename(file_img, path + "check/" + (os.path.basename(os.path.normpath(file_img))))

def check_channel_no(path):
	img_list = []
	files=get_files(path)

	for file_img in files:
	
		image = imageio.imread(file_img)
		if(len(image.shape)<3):
			img_list.append(file_img)
			#print(file_img)
			img_list.append(file_img)
	print("\n".join(img_list))
	'''for files in img_list:
			img = Image.open(files)
			if not os.path.exists(path+"converted_to_rgb/"):
						os.makedirs(path+"converted_to_rgb")
			print(files)
			print(os.path.basename(os.path.normpath(files)))
			rgbimg = Image.new("RGB", img.size)
			rgbimg.paste(img)
			rgbimg.save(path + "converted_to_rgb/" + os.path.basename(os.path.normpath(file_img)), "JPEG", quality=100, subsampling=0)'''

