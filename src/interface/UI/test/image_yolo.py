import cv2
import time
from ultralytics import YOLO

model = YOLO("best.pt")

CLASS_MAP = {
    'red': 'red',
    'blue': 'blue',
    'yellow': 'yellow'
}

prev_time = 0

def detect_colors(frame):
    global prev_time
    grid_width = 30
    grid_height = 20

    num_red = 0
    num_yellow = 0
    num_blue = 0

    frame = cv2.resize(frame, (550, 440))

    # FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time

    results = model(frame, conf=0.3, imgsz=416, verbose=False)[0]
    height, width = frame.shape[:2]

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label_name = model.names[cls_id].lower()

        if label_name not in CLASS_MAP:
            continue

        conf = float(box.conf[0])   # ⭐ CONFIDENCE

        # (optional) lọc thêm lần nữa
        if conf < 0.4:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        custom_x = round(grid_width * (1 - cx / width), 2)
        custom_y = round(grid_height * (cy / height), 2)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.circle(frame, (int(cx), int(cy)), 5, (255,255,255), -1)

        # ⭐ HIỂN THỊ CONFIDENCE
        text = f"{label_name.upper()} {conf:.2f} ({custom_x},{custom_y})"
        cv2.putText(frame, text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        if label_name == 'red':
            num_red = 1
        elif label_name == 'yellow':
            num_yellow = 1
        elif label_name == 'blue':
            num_blue = 1

    cv2.putText(frame, f"FPS: {int(fps)}", (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    return frame, num_red, num_blue, num_yellow
