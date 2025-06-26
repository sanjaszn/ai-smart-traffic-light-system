import cv2
import numpy as np

video_path = r"D:\XAMPP\htdocs\Projects\trafficAI\data\raw\roadTrafficVideo_trimmed.mp4"
frame_number = 50  # Frame to pause and draw on

# Target size for drawing (e.g., screen-friendly 1280x720)
display_width = 1280
display_height = 720

zones = []
current_zone = []

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        current_zone.append((x, y))
        print(f"Point (resized): ({x}, {y})")

def draw_zones_on_frame(frame):
    for i, zone in enumerate(zones):
        pts = np.array(zone, np.int32)
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        cx = int(np.mean([p[0] for p in zone]))
        cy = int(np.mean([p[1] for p in zone]))
        cv2.putText(frame, f"Zone {chr(65 + i)}", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

def main():
    global current_zone
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()

    if not ret:
        print("Error reading frame.")
        return

    original_h, original_w = frame.shape[:2]
    resized_frame = cv2.resize(frame, (display_width, display_height))

    scale_x = original_w / display_width
    scale_y = original_h / display_height

    print(f"Original: {original_w}x{original_h} | Resized: {display_width}x{display_height}")
    print("🔹 Left click to select points for a zone")
    print("🔹 Press ENTER to finish a zone")
    print("🔹 Press ESC to finish and save\n")

    cv2.namedWindow("Draw Zones")
    cv2.setMouseCallback("Draw Zones", click_event)

    while True:
        display = resized_frame.copy()
        draw_zones_on_frame(display)

        if len(current_zone) > 1:
            cv2.polylines(display, [np.array(current_zone, np.int32)], isClosed=False, color=(0, 0, 255), thickness=1)
            for pt in current_zone:
                cv2.circle(display, pt, 5, (0, 0, 255), -1)

        cv2.imshow("Draw Zones", display)
        key = cv2.waitKey(1)

        if key == 13:  # ENTER
            if len(current_zone) >= 3:
                zones.append(current_zone.copy())
                current_zone.clear()
                print(f"✔️ Zone {chr(64 + len(zones))} saved\n")
            else:
                print("⚠️ Select at least 3 points to define a zone.")

        elif key == 27:  # ESC
            print("\n✅ All zones completed.\n")
            break

    cap.release()
    cv2.destroyAllWindows()

    # Convert zones to original resolution
    print("\n📐 Zones scaled to original resolution:\n")
    for i, zone in enumerate(zones):
        scaled = [(int(x * scale_x), int(y * scale_y)) for (x, y) in zone]
        print(f'"Zone {chr(65 + i)}": np.array([')
        for pt in scaled:
            print(f"    [{pt[0]}, {pt[1]}],")
        print("], np.int32),\n")

if __name__ == "__main__":
    main()
