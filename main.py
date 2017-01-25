# import the necessary packages
from pivideostream import PiVideoStream
from WebcamVideoStream import WebcamVideoStream
import time, cv2, numpy, imutils, math, argparse
from networktables import NetworkTable
from utils import *
import utils
from cv2 import countNonZero

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera",
	help="whether or not the Raspberry Pi camera should be used")
args = vars(ap.parse_args())

kernel = numpy.ones((5,5), numpy.uint8)
#frameNum = 0 # TODO: find out how to determine unique frames
loops = 0
key = 0
centerX = 0
centerY = 0
angleToTarget = 0
#utils.hsvWrite(30,90,120,255,120,255) #Write Networktable values Green
utils.hsvWrite(80,120,80,120,190,255) #Write Networktable values Blue
#utils.hsvWrite(130,120,80,200,190,255) #Write Networktable values Red
if (args["picamera"] > 0):
    cap = PiVideoStream().start()
else:
    cap = WebcamVideoStream().start()
time.sleep(2.0)
target = -1
while True:
    image = cap.read() #Capture frame
    imageCopy = image
##    if loops == 0:
##        oldimageCopy = imageCopy
    image = imutils.resize(image, width=320) #resize - needed to allow rest of toolpath to work
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) #Convert from BGR to HSV
    (lower_green,upper_green,display) = utils.hsvRead() #Get lower and Upper HSV values from the Networktable to use
    image_hsv = cv2.inRange(hsv, lower_green, upper_green) #Filter based on lower and upper HSV limits
    cnts = cv2.findContours(image_hsv.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]# Find contours
##    difference = cv2.subtract(imageCopy, oldimageCopy)    
##    result = not numpy.any(difference)
##    if result is True:
##        print "Pictures are the same"
##    else:
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
        cv2.imshow("Frame", image) #Display a screen with outputs        key = cv2.waitKey(1) & 0xFF #Wait for keypress if there is a display
##    oldimageCopy=imageCopy
    utils.targetWrite(target,centerX,centerY,angleToTarget,loops)
    if key == ord("q"):# if the `q` key was pressed, break from the loop
            break
    loops += 1
    
cv2.destroyAllWindows()
cap.stop()
