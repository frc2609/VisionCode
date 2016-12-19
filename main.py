# import the necessary packages
from imutils.video import VideoStream
import time, cv2, numpy, imutils, math, argparse
from networktables import NetworkTable
from utils import *
import utils

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=-1,
	help="whether or not the Raspberry Pi camera should be used")
args = vars(ap.parse_args())
kernel = numpy.ones((5,5), numpy.uint8)
#frameNum = 0 # TODO: find out how to determine unique frames
loops = 0
key = 0
centerX = 0
centerY = 0
angleToTarget = 0
utils.hsvWrite(30,90,120,255,120,255) #Write Networktable values
cap = VideoStream(usePiCamera=args["picamera"] > 0).start() # initialize the video stream and allow the cammera sensor to warmup
time.sleep(2.0)
while True:
    image = cap.read() #Capture frame
    image = imutils.resize(image, width=320) #resize - needed to allow rest of toolpath to work
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) #Convert from BGR to HSV
    (lower_green,upper_green,display) = utils.hsvRead() #Get lower and Upper HSV values from the Networktable to use
    image_hsv = cv2.inRange(hsv, lower_green, upper_green) #Filter based on lower and upper HSV limits
    cnts = cv2.findContours(image_hsv.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]# Find contours
    if len(cnts) > 0:# only proceed if at least one contour was found
        c = max(cnts, key=cv2.contourArea)
        ((x,y),radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if (M["m00"]!=0): #Catch a div/0 error!
            center = (int(M["m10"] /(M["m00"])), int(M["m01"] / (M["m00"])))
        else:
            center = (int(M["m10"] /1), int(M["m01"] / 1))
        if radius > 25: #Only if radius meets a min size
            centerX = center[0]
            centerY = center[1]
            angleToTarget = math.atan((centerX-160)/317.5)*(180/math.pi) #angleToTarget returns angle to target in degrees
            target = 1
            if display != 0: #Draw bounding circle and center dot if display turned on
                cv2.circle(image,(int(x),int(y)),int(radius),(0,255,255),2)
                cv2.circle(image,center,5,(0,255,255),-1)
        else: # if no target is large enough
            target = -1 # return -1  for target
    else: # if no contours are found
        target = -1 # return -1  for target
    # show the frame and other images, output values to networktable
    if display != 0: #Draw display if turned on 
        cv2.imshow("Frame", image) #Display a screen with outputs
        key = cv2.waitKey(1) & 0xFF #Wait for keypress if there is a display
    utils.targetWrite(target,centerX,centerY,angleToTarget,loops)
    if key == ord("q"):# if the `q` key was pressed, break from the loop
            break
    loops += 1
cv2.destroyAllWindows()
cap.stop()
