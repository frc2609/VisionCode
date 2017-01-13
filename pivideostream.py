# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2

class PiVideoStream:
	def __init__(self, resolution=(320, 240), framerate=32):
		# initialize the camera and stream
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.camera.vflip = True
		self.camera.hflip = True
		self.camera.awb_mode = 'off'
		self.camera.awb_gains = (.2, .2)
		self.camera.brightness = 50
		self.camera.exposure_mode = 'sports'
		self.camera.exposure_mode = 'off'
		self.camera.contrast = 0
		self.camera.drc_strength = 'off'
		self.camera.exposure_compensation = 0
		self.camera.flash_mode = 'off'
		self.camera.image_effect = 'none'
		self.camera.iso = 400
		self.camera.saturation = 0
		self.camera.sharpness = 0
		self.camera.video_denoise = False
		self.camera.meter_mode = 'spot' #Retrieves or sets the metering mode of the camera.
		self.camera.video_stabilization = False
		self.camera.shutter_speed = 10000 #Random value chosen
		
		
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)

		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame = f.array
			self.rawCapture.truncate(0)

			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				return

	def read(self):
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
