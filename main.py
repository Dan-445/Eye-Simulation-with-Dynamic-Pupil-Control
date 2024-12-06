import cv2
import numpy as np
from ultralytics import YOLO
import tkinter as tk
from tkinter import colorchooser
import threading

# Load the YOLO model
model = YOLO("eye-seg.pt")

# Function to map detected coordinates to the simulation frame
def map_to_simulation_frame(center, frame_size, sim_size):
    """
    Map the detected center coordinates to the simulation frame dimensions.
    """
    x, y = center
    frame_width, frame_height = frame_size
    sim_width, sim_height = sim_size

    # Scale coordinates to the simulation frame size
    mapped_x = int(x * sim_width / frame_width)
    mapped_y = int(y * sim_height / frame_height)

    return (mapped_x, mapped_y)

# Function to smooth the movement of the eye (sclera, iris, pupil)
def smooth_movement(current, target, smoothing_factor=0.1):
    """Smoothly move the eye components towards target positions."""
    return (int(current[0] + (target[0] - current[0]) * smoothing_factor),
            int(current[1] + (target[1] - current[1]) * smoothing_factor))

# Function to draw the simulated eye dynamically based on detection sizes and positions
def draw_dynamic_eye_simulation(sclera_detected, sclera_center, sclera_size,
                                iris_detected, iris_center, iris_size,
                                pupil_detected, pupil_center, pupil_size, brightness, sclera_color, iris_color, pupil_color):
    """
    Draw the eye simulation dynamically based on detection sizes and positions.
    """
    simulation_height, simulation_width = 1080, 1920  # Full screen size (1920x1080)
    
    # Create a black background (no background color)
    simulation_frame = np.zeros((simulation_height, simulation_width, 3), dtype=np.uint8)

    # Draw the sclera (ellipse for eye shape) only if detected
    if sclera_detected:
        sclera_width, sclera_height = sclera_size
        cv2.ellipse(
            simulation_frame,
            sclera_center,
            (sclera_width, sclera_height),
            0, 0, 360,
            sclera_color, -1  # -1 means filled ellipse
        )

    # Draw the iris (circle) only if detected
    if iris_detected:
        iris_width, iris_height = iris_size
        iris_radius = min(iris_width, iris_height) // 2
        cv2.circle(simulation_frame, iris_center, iris_radius, iris_color, -1)  # Iris color

    # Draw the pupil (circle) only if detected
    if pupil_detected:
        pupil_width, pupil_height = pupil_size
        pupil_radius = min(pupil_width, pupil_height) // 2
        cv2.circle(simulation_frame, pupil_center, pupil_radius, pupil_color, -1)  # Pupil color

    return simulation_frame

# Global variables for color selection
sclera_color = (255, 255, 255)  # Default sclera color (white)
iris_color = (0, 255, 0)  # Default iris color (green)
pupil_color = (0, 0, 0)  # Default pupil color (black)
brightness = 50
tracking_enabled = True  # Flag to control tracking state

# Function to open color picker and set sclera color
def choose_sclera_color():
    global sclera_color
    color = colorchooser.askcolor()[0]  # Open color picker dialog
    if color:
        sclera_color = tuple(map(int, color[::-1]))  # Convert from RGB to BGR (OpenCV format)

# Function to open color picker and set iris color
def choose_iris_color():
    global iris_color
    color = colorchooser.askcolor()[0]  # Open color picker dialog
    if color:
        iris_color = tuple(map(int, color[::-1]))  # Convert from RGB to BGR (OpenCV format)

# Function to open color picker and set pupil color
def choose_pupil_color():
    global pupil_color
    color = colorchooser.askcolor()[0]  # Open color picker dialog
    if color:
        pupil_color = tuple(map(int, color[::-1]))  # Convert from RGB to BGR (OpenCV format)

# Function to toggle tracking state
def toggle_tracking():
    global tracking_enabled
    tracking_enabled = not tracking_enabled  # Toggle the state
    if tracking_enabled:
        tracking_button.config(text="Stop Tracking")
    else:
        tracking_button.config(text="Start Tracking")

# Tkinter window setup for the color change UI
def create_ui():
    window = tk.Tk()
    window.title("Eye Simulation Color Control")

    # Create buttons for each color change
    sclera_button = tk.Button(window, text="Choose Sclera Color", command=choose_sclera_color)
    sclera_button.pack(pady=10)

    iris_button = tk.Button(window, text="Choose Iris Color", command=choose_iris_color)
    iris_button.pack(pady=10)

    pupil_button = tk.Button(window, text="Choose Pupil Color", command=choose_pupil_color)
    pupil_button.pack(pady=10)

    # Button to start/stop tracking
    global tracking_button
    tracking_button = tk.Button(window, text="Stop Tracking", command=toggle_tracking)
    tracking_button.pack(pady=10)

    # Start the Tkinter window
    window.mainloop()

# Start the UI in a separate thread so it runs asynchronously with the video processing
ui_thread = threading.Thread(target=create_ui, daemon=True)
ui_thread.start()

# Video capture for YOLO detection
video_path = "vid1.mp4"
cap = cv2.VideoCapture(video_path)

# Check if the video file opened successfully
if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Define frame dimensions based on the video capture
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Get the width of the frame
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Get the height of the frame

# Video writer for combined output
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = int(cap.get(cv2.CAP_PROP_FPS))
combined_writer = cv2.VideoWriter("combined_output.mp4", fourcc, fps, (1920, 1080))  # Combined frame width

# Main loop
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("End of video reached or error occurred.")
        break

    # If tracking is enabled, run YOLO detection on the frame
    if tracking_enabled:
        # Run YOLO detection on the frame
        results = model(frame)

        # Initialize flags for detection
        sclera_detected = False
        iris_detected = False
        pupil_detected = False

        # Default positions and sizes
        sclera_center = (960, 540)  # Center of the screen (half of 1920x1080)
        sclera_size = (300, 200)  # Default sclera size (width, height)
        iris_center = sclera_center
        iris_size = (150, 150)  # Default iris size
        pupil_center = sclera_center
        pupil_size = (50, 50)  # Default pupil size

        # Process detections
        for box in results[0].boxes:
            class_id = int(box.cls.cpu().numpy()[0])  # Get class ID
            bbox = box.xyxy[0].cpu().numpy().astype(int)  # Bounding box coordinates
            center_x = (bbox[0] + bbox[2]) // 2
            center_y = (bbox[1] + bbox[3]) // 2
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]

            # Map detected positions and sizes to simulation frame
            mapped_center = map_to_simulation_frame((center_x, center_y), (frame_width, frame_height), (1920, 1080))
            mapped_size = (int(width * 1920 / frame_width), int(height * 1080 / frame_height))

            if class_id == 0:  # Sclera (Eye)
                sclera_detected = True
                sclera_center = mapped_center
                sclera_size = (mapped_size[0] // 2, mapped_size[1] // 2)
            elif class_id == 1:  # Iris
                iris_detected = True
                iris_center = mapped_center
                iris_size = mapped_size
            elif class_id == 2:  # Pupil
                pupil_detected = True
                pupil_center = mapped_center
                pupil_size = mapped_size

        # Generate the simulation frame with the updated colors
        simulation_frame = draw_dynamic_eye_simulation(
            sclera_detected=sclera_detected,
            sclera_center=sclera_center,
            sclera_size=sclera_size,
            iris_detected=iris_detected,
            iris_center=iris_center,
            iris_size=iris_size,
            pupil_detected=pupil_detected,
            pupil_center=pupil_center,
            pupil_size=pupil_size,
            brightness=brightness,
            sclera_color=sclera_color,
            iris_color=iris_color,
            pupil_color=pupil_color
        )

        # Write the simulation frame to the output video
        combined_writer.write(simulation_frame)

        # Display the simulation frame
        cv2.imshow("Eye Simulation", simulation_frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources and close windows
cap.release()
combined_writer.release()
cv2.destroyAllWindows()
