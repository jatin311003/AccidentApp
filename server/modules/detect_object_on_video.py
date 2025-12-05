from ultralytics import YOLO
import cv2
import math
import cvzone

def detect_object_on_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    model = YOLO('./models/yolov8n.pt')
    classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                  "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                  "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                  "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
                  "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                  "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
                  "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                  "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                  "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                  "teddy bear", "hair drier", "toothbrush"
                  ]

    while True:
        success, img = cap.read()
        if not success:
            break

        results = model(img, stream=True)
        vehicles = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1

                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                label = classNames[cls].upper()

                # Only check for vehicle classes
                if label in ["CAR", "TRUCK", "BUS", "MOTORBIKE"]:
                    vehicles.append((x1, y1, x2, y2))
                    cvzone.cornerRect(img, (x1, y1, w, h))
                    cvzone.putTextRect(img, f'{label} {conf}', (max(0, x1), max(35, y1)), colorR=(0,165,255))

        # Check for collisions (bounding box overlaps)
        for i in range(len(vehicles)):
            for j in range(i + 1, len(vehicles)):
                x1, y1, x2, y2 = vehicles[i]
                a1, b1, a2, b2 = vehicles[j]

                # Intersection logic
                if x1 < a2 and x2 > a1 and y1 < b2 and y2 > b1:
                    # Collision detected
                    cv2.putText(img, '🚨 ACCIDENT DETECTED!', (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        yield img

cv2.destroyAllWindows()
