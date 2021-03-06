import sys
# Add RealSense library path:
sys.path.append("/home/rikard/.pyenv/versions/3.9.0/lib/python3.9/site-packages/pyrealsense2")

import pyrealsense2 as rs
import numpy as np
import cv2
from pyzbar import pyzbar

# Start camera interface
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)

pipeline.start(config)

a = True

try: 
    while True:
        frame = pipeline.wait_for_frames()
        color_frame = frame.get_color_frame()
        if not color_frame:
            continue

        img = np.asanyarray(color_frame.get_data())
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 3)
        sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpen = cv2.filter2D(blur, -1, sharpen_kernel)

        thresh = cv2.threshold(sharpen, 160, 255, cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
        close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        cnts, _ = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            peri = cv2.arcLength(c, True)
            x,y,w,h = cv2.boundingRect(c)
            area = cv2.contourArea(c)
            ar = w / float(h)
            if (ar > .85 and ar < 1.3 and area > 1000):
                print("found! - " + str(area))
                cv2.rectangle(img, (x, y), (x+w, y+h), (36, 255, 12), 2)


        cv2.imshow('test', close)
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', img)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        
finally:
    cv2.destroyAllWindows()
    pipeline.stop()