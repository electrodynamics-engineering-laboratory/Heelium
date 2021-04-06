from picamera import PiCamera
import time
import serial
import shutil
import os
import logging

class CameraControl:
	def __init__(self, log_dir):
		# creates camera log
		FORMAT = "%(asctime)s %(relativeCreated)d %(levelname)s %(message)s"
		logging.basicConfig(filename=log_dir, format=FORMAT)
		self.logger = logging.getLogger()

		self.resolution = (2592, 1944)	# defaults for images
		self.framerate = 15
		self.mode = "image"
		self.image_dir = "/home/pi/pictures/"
		self.video_dir = "/home/pi/videos/"
		try:
			self.camera = PiCamera()
			self.camera.resolution = self.resolution
			self.framerate = self.framerate
			self.logger.info("Camera initialized")
		except Exception as e:
			self.logger.error(e)

	def take_picture(self, imagename):
		try:
			self.set_camera_mode("image")
			img = os.path.join(self.image_dir, imagename)
			self.camera.start_preview()
			time.sleep(5)
			self.camera.capture(img)
			self.camera.stop_preview()
		except Exception as e:
			self.logger.error(e)
			self.logger.warning("Information about above video error: imagename={}".format(imagename))
			print("Unable to take image")

	def take_video(self, videoname, seconds):
		try:
			self.set_camera_mode("video")
			vid = os.path.join(self.video_dir, videoname)
			self.camera.start_preview()
			self.camera.start_recording(vid)
			time.sleep(abs(seconds))
			self.camera.stop_recording()
			self.camera.stop_preview()
		except Exception as e:
			self.logger.error(e)
			self.logger.warning("Information about above video error: videoname={} seconds={}".format(videoname, seconds))
			print("Unable to take video")

	def set_image_directory(self, name):
		self.image_dir = name

	def set_video_directory(self, name):
		self.video_dir = name

	def get_image_directory(self):
		return self.image_dir

	def get_video_directory(self):
		return self.video_dir

	def set_camera_mode(self, mode):
		try:
			# set the mode to imaging
			if ( (str(mode).lower() == "image") or (mode == 0) ):
				self.mode = "image"
				self.resolution = (2592, 1944)	# defaults for images
				self.framerate = 15
			# set the mode to imaging
			elif ( (str(mode).lower() == "video") or (mode == 1) ): 
				self.mode = "image"
				self.resolution = (1920, 1080)	# defaults for video
				self.framerate = 30
			# now change camera settings
			self.camera.resolution = self.resolution
			self.camera.framerate = self.framerate
		except Exception as e:
			self.logger.error(e)
			print("Error changing imaging modes")

if __name__ == '__main__':
	try:
		FORMAT = "%(asctime)s %(relativeCreated)d %(levelname)s %(message)s"
		logging.basicConfig(filename="/home/pi/log/camera", format=FORMAT)
		logger = logging.getLogger()
	except Exception as e:
		print(e)
		sys.exit()
	try:	
		control = CameraControl("/home/pi/log/camera.driver")
		print("Initialized Camera Control")
	except Exception as e:
		print("Could not create Camera Control object")
		logger.error(e)
	# sets timer and img/vid incrementors
	timer = 0
	image = 0
	video = 0
	try:
		# test image
		img_name = "test.jpg"
		control.take_picture(img_name)
		print("Test image created")
	except Exception as e:
		print("Test image failed")
		logger.error(e)
		sys.exit()

	try:
		vid_name = "test.h264"
		control.take_video(vid_name, 15)	# 15 second video
		print("Video created {}".format(vid_name))
	except Exception as e:
		print("Test video failed")
		logger.error(e)
		sys.exit()

	while(timer < 210):	# runs loop for 210 minutes (3.5 hours)
		timer += 1
		time.sleep(5)
		try:
			if (timer % 2 == 0):
				image += 1
				img_name = "image-{}.jpg".format(image)
				control.take_picture(img_name) 		# takes picture every 2 minutes
				print("Imaged {}".format(img_name))
				logger.info("Image successfully created: {}".format(img_name))
		except Exception as e:
			print("Error capturing image file") # error logged in camera.log by cameracontrol class
			logger.warning(e)

		try:
			if (timer % 20 == 0):					# takes a short video every 20 minutes
				video += 1
				vid_name = "video-{}.h264".format(video)
				control.take_video(vid_name, 15)	# 15 second video
				print("Video created {}".format(vid_name))
				logger.info("Video successfully created: {}".format(vid_name))
		except:
			print("Error capturing video file") # error logged in camera.log by cameracontrol class
			logger.warning(e)