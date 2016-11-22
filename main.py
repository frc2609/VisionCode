# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy

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
camera.vflip = False
camera.hflip = False
camera.resolution = (640, 480)
camera.framerate = 60
camera.awb_mode = 'off'
camera.awb_gains = (1.8, 0.9)
camera.exposure_mode = 'backlight'
camera.flash_mode = 'off'
camera.image_effect = 'none'
camera.iso = 800
camera.meter_mode = 'backlit' #Retrieves or sets the metering mode of the camera.
camera.video_stabilization = False
rawCapture = PiRGBArray(camera, size=(640, 480))

kernel = numpy.ones((5,5), numpy.uint8)
 
# allow the camera to warmup
time.sleep(0.1)

loops = 0
timesum = 0 
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	timestart = time.time()
	image = frame.array

        # CV erode iterations 1 Border_constant
	image_erosion = cv2.erode(image, kernel, iterations=1)

        # CV dilate iterations 2 Border_constant
	image_dilation = cv2.dilate(image_erosion, kernel, iterations=2)
	
        # HSV H:49-97 S: 179-255 V: 25-220
        lower_green = numpy.array([60,80,41])
        upper_green = numpy.array([110,140,220])
        hsv = cv2.cvtColor(image_dilation, cv2.COLOR_BGR2HSV)
        image_hsv = cv2.inRange(hsv, lower_green, upper_green)

        # Find contours
        ret,thresh = cv2.threshold(image_hsv,127,255,0)
        im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        # show the frame and other images
        cv2.drawContours(image, contours, -1, (0,255,0), 3)
	cv2.imshow("Frame", image)
	#cv2.imshow("image_erosion", image_erosion)
	#cv2.imshow("image_dilation", image_dilation)
	#cv2.imshow("image_hsv", image_hsv)
 
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
        key = cv2.waitKey(1) & 0xFF
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
	deltatime = ((time.time()-timestart)*1000)
	timesum += deltatime
	loops += 1
	print("loops: "+ str(loops))
	print("CPS: " + str(timesum/loops))

cv2.destroyAllWindows()
