# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# NT publish number (fps)
# //Resize to 320x240 Cubic
# CV erode iterations 1 Border_constant
# CV dilate iterations 2 Border_constant
# HSV H:49-97 S: 179-255 V: 25-220
# Find contours
# Filter contours Min-area: 60 Min-perim: 150 Min-width: 20 Max-width:1000 min-height:20 max-height:1000 Solidity: 24-55
# NT Publish contoursreport
# find lines
# Publish LinesReport

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 60
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)
 
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
 
	# show the frame
	cv2.imshow("Frame", image)
	key = cv2.waitKey(1) & 0xFF
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

