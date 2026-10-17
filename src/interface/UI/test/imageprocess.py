import cv2
import numpy as np
#from collections import Counter

# total = 0
# num_red = 0
# num_yellow = 0
# num_blue = 0
color_ranges = {
        'red': [(0, 120, 70), (10, 255, 255), (170, 120, 70), (180, 255, 255)],
        'yellow': [(20, 100, 100), (30, 255, 255)],
        'blue': [(94, 80, 2), (126, 255, 255)]
    }

def detect_colors(frame):
    grid_width=30
    grid_height=20
    rx = 20
    ry = 50
    rw = 1050
    rh = 465
    num_red = 0
    num_yellow = 0
    num_blue = 0
    #dets = []
    while True:
        
        height, width = frame.shape[:2]
        roi_img = frame[ry:ry+rh, rx:rx+rw].copy()
        hsv = cv2.cvtColor(roi_img, cv2.COLOR_BGR2HSV)
        cv2.rectangle(frame,(200,150), (1050,465), (255,0,0),2)

        for color, ranges in color_ranges.items():
            if color == 'red':
                mask1 = cv2.inRange(hsv, np.array(ranges[0]), np.array(ranges[1]))
                mask2 = cv2.inRange(hsv, np.array(ranges[2]), np.array(ranges[3]))
                mask = cv2.bitwise_or(mask1, mask2)
            else:
                mask = cv2.inRange(hsv, np.array(ranges[0]), np.array(ranges[1]))

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 500:
                    x, y, w, h = cv2.boundingRect(cnt)
                    aspect_ratio = float(w) / h
                    if 0.8 < aspect_ratio < 1.2:
                        cx = x + w / 2
                        cy = y + h / 2

                        custom_x = round(grid_width * (1 - cx / rw), 2)
                        custom_y = round(grid_height * (cy / rh), 2)

                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.circle(frame, (int(rx+cx), int(ry+cy)), 5, (255, 255, 255), -1)

                        label = f"{color.upper()} ({custom_x}, {custom_y})"
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        if color == 'red':
                            num_red = 1
                        elif color == 'yellow':
                            num_yellow = 1
                        else:
                            num_blue = 1
                        # total = num_red + num_blue + num_yellow

        return frame, num_red, num_blue, num_yellow
