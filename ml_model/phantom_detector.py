from ultralytics import YOLO
import cv2
from datetime import datetime
from ultralytics import YOLO
import cv2
from datetime import datetime
from db_helper import init_db, save_event   # <-- ye import already add kiya tha

model = YOLO('yolov8n.pt')          # <-- YOLO model load ho raha hai
cap = cv2.VideoCapture(0)           # <-- camera khul raha hai

init_db()                            # <-- YE NAYI LINE — isko yahan daalo

ROOM_ID = "C-204"
ROOM_PROFILES = {
    "C-204": {"ac_w": 1200, "fans_w": 210, "lights_w": 290}
}
TARIFF_INR = 8.0
GRID_FACTOR = 0.72

empty_since = None
total_kwh_saved = 0
total_inr_saved = 0
total_co2_saved = 0

def is_room_booked(room_id):
    return True

def compute_impact(room_id, minutes_empty):
    profile = ROOM_PROFILES[room_id]
    total_watts = sum(profile.values())
    total_kw = total_watts / 1000
    hours = minutes_empty / 60
    kwh = total_kw * hours
    inr = kwh * TARIFF_INR
    co2 = kwh * GRID_FACTOR
    return round(kwh, 5), round(inr, 3), round(co2, 5)

print("System chalu ho gaya!")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, classes=[0], verbose=False)
    person_count = len(results[0].boxes)
    booked = is_room_booked(ROOM_ID)

    if booked and person_count == 0:
        if empty_since is None:
            empty_since = datetime.now()

        minutes_empty = (datetime.now() - empty_since).total_seconds() / 60
        kwh, inr, co2 = compute_impact(ROOM_ID, minutes_empty)

        # TERMINAL PE PRINT — screen ki tension chhodo, ye hamesha dikhega
        print(f"PHANTOM | Empty: {minutes_empty:.2f} min | "
              f"kWh: {kwh} | Rs: {inr} | CO2: {co2} kg")
    else:
        if empty_since is not None:
            minutes_empty = (datetime.now() - empty_since).total_seconds() / 60
            kwh, inr, co2 = compute_impact(ROOM_ID, minutes_empty)
            total_kwh_saved += kwh
            total_inr_saved += inr
            total_co2_saved += co2
            print(f"✅ ROOM FREED | {minutes_empty:.2f} min | "
                  f"kWh: {kwh} | Rs: {inr} | CO2: {co2}")
        empty_since = None

    # Simple screen display (bada text, alag rang)
    display = frame.copy()
    cv2.putText(display, f"People: {person_count} Booked: {booked}",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    if empty_since is not None:
        mins = (datetime.now() - empty_since).total_seconds() / 60
        kwh, inr, co2 = compute_impact(ROOM_ID, mins)
        cv2.putText(display, f"PHANTOM {mins:.1f}min", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(display, f"Rs{inr} | CO2:{co2}kg", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Room Occupancy Detector", display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
