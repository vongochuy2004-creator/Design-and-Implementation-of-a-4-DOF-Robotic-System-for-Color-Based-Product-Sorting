
import cv2
from image_yolo import detect_colors

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Không mở được camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame, r, b, y = detect_colors(frame)

    print(f"RED={r}, BLUE={b}, YELLOW={y}")

    cv2.imshow("YOLO Color Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
