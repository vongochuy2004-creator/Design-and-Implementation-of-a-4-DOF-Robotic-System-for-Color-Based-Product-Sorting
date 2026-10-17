from ultralytics import YOLO

model = YOLO('best.pt')  # load a pretrained YOLO detection model

result = model('20251216_213632.jpg')  # predict on an image
result[0].show()  # Display results