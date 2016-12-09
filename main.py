# import the necessary packages
from collections import deque
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy
from networktables import NetworkTable
import math

NetworkTable.setIPAddress("roborio-2609-frc.local")#Change the address to your own
NetworkTable.setClientMode()
NetworkTable.initialize()
sd = NetworkTable.getTable("RaspberryPi")
memoryPts = 64
pts = deque(maxlen=memoryPts) #Number of points of memory

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
camera.hflip = True
camera.resolution = (320, 240)
camera.framerate = 60
camera.awb_mode = 'off'
camera.awb_gains = (0.2, 0.2)
camera.brightness = 50
camera.exposure_mode = 'fireworks'
camera.exposure_mode = 'off'
#camera.color_effects = 'None'
camera.contrast = 0
camera.drc_strength = 'off'
camera.exposure_compensation = 0
camera.flash_mode = 'off'
camera.image_effect = 'none'
camera.iso = 400
#camera.led = False
camera.saturation = 0
camera.sharpness = 0
camera.video_denoise = False
camera.meter_mode = 'spot' #Retrieves or sets the metering mode of the camera.
camera.video_stabilization = False
rawCapture = PiRGBArray(camera, size=(320, 240))

kernel = numpy.ones((5,5), numpy.uint8)
 
# allow the camera to warmup
time.sleep(0.1)

loops = 0
timesum = 0 
CPS = 0
sd.putNumber('H_L',30)
sd.putNumber('H_U',90)
sd.putNumber('S_L',120)
sd.putNumber('S_U',255)
sd.putNumber('V_L',120)
sd.putNumber('V_U',255)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        
        
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    timestart = time.time()
    image = frame.array

    # HSV H:49-97 S: 179-255 V: 25-220
    try:
        H_L = sd.getNumber('H_L')
        H_U = sd.getNumber('H_U')
        S_L = sd.getNumber('S_L')
        S_U = sd.getNumber('S_U')
        V_L = sd.getNumber('V_L')
        V_U = sd.getNumber('V_U')
    except KeyError:
        print('RaspberryPi Connect: N/A 1')
    
    lower_green = numpy.array([H_L,S_L,V_L])
    upper_green = numpy.array([H_U,S_U,V_U])
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    image_hsv = cv2.inRange(hsv, lower_green, upper_green)

    # CV erode iterations 1 Border_constant
    image_erosion = cv2.erode(image_hsv, None, iterations=2)

    # CV dilate iterations 2 Border_constant
    image_dilation = cv2.dilate(image_erosion, None, iterations=2)


    # Find contours
    #ret,thresh = cv2.threshold(image_dilation,0,255,cv2.THRESH_BINARY)
    cnts = cv2.findContours(image_dilation.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = (0,0)

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # Find bounding box's
        #x,y,w,h = cv2.boundingRect(cnts)
        c = max(cnts, key=cv2.contourArea)
        ((x,y),radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only if radius meets a min size
        if radius > 10:
            cv2.circle(image,(int(x),int(y)),int(radius),(0,255,255),2)
            cv2.circle(int(M["m10"] / M["m00"])(image,center,5,(0,255,255),-1))
    #update points in queue
    pts.appendleft(center)
    for i in xrange(1, len(pts)):
        if pts[i-1] is None or pts [i] is None:
            continue
        #otherwise compute thickness of line and connect it
        thickness = int((numpy.sqrt(memoryPts) / float(i+1)*2.5))
        cv2.line(image,pts[i-1],pts[i],(0,0,255),thickness)
        centerX = int(M["m10"] / M["m00"])
        angleToTarget = math.atan((centerX-160)/320.9103533214) #  angleToTarget returns angle to target in rads.
        #                                                    320.9103533214 is our focal length in pixels
        #                                                    found out by width/(2*tan(FOV/2)) where FOV is in degrees
        #cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),3)
        sd.putNumber('centerX', centerX)
        sd.putNumber('angleToTarget', angleToTarget)
        sd.putNumber('centerY', int(M["m01"] / M["m00"]))
        #sd.putString('center', str(center))   

    # show the frame and other images
    
    #cv2.drawContours(image, contours, -1, (0,0,255), 3)
    #cv2.putText(image, "CPS: " + str(CPS) + " Loops: " + str(loops), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
    #cv2.imshow("Frame", image)
    #cv2.imshow("image_erosion", image_erosion)
    #cv2.imshow("thresh", thresh)
    #cv2.imshow("image_hsv", image_hsv)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
            break
    #deltatime = ((time.time()-timestart)*1000)
    #timesum += deltatime
    #loops += 1
    #CPS = timesum/loops

    
##    try:
##        #print('raspberryTime:', sd.getNumber('test'))
##        print('H_L:', sd.getNumber('H_L'))
##        print('H_U:', sd.getNumber('H_U'))
##        print('S_L:', sd.getNumber('S_L'))
##        print('S_U:', sd.getNumber('S_U'))
##        print('V_L:', sd.getNumber('V_L'))
##        print('V_U:', sd.getNumber('V_U'))
##    except KeyError:
##        print('RaspberryPi Connect: N/A 2')
    sd.putNumber('piLoops', loops)


cv2.destroyAllWindows()
