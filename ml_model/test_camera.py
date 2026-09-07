from ultralytics import YOLO
import cv2

# YOLO model load karo (pehli baar chalate waqt khud download hoga, ~6MB)
model = YOLO('yolov8n.pt')

# Laptop webcam kholo
cap = cv2.VideoCapture(0)

print("Camera chalu ho gaya! 'q' dabao band karne ke liye")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera nahi mil raha, check karo")
        break

    # YOLO se log detect karo (class 0 = person)
    results = model(frame, classes=[0], verbose=False)
    person_count = len(results[0].boxes)

    # Frame pe count likh do
    annotated_frame = results[0].plot()
    cv2.putText(annotated_frame, f"People: {person_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Room Occupancy Detector", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()