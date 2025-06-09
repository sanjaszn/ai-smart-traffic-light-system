from vidstab import VidStab

stabilizer = VidStab(kp_method='ORB')  # ORB is more stable than default
stabilizer.stabilize(
    input_path='D:/XAMPP/htdocs/Projects/trafficAI/data/raw/trafficVid.mp4',
    output_path='D:/XAMPP/htdocs/Projects/trafficAI/data/raw/trafficVid_stable_v2.mp4',
    smoothing_window=30,  # Increase for smoother motion
    border_size=50        # Crop outer shaking edges
)
