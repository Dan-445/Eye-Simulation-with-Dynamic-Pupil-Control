
# Eye Simulation with Dynamic Pupil Control

This project simulates an eye with a dynamic pupil, iris, and sclera. The pupil size can change based on ambient light using a light sensor connected to a Raspberry Pi. The simulation also allows you to change the colors of the eye (sclera, iris, pupil) via a simple GUI.

There are two scripts:

1. **`main.py`**: Runs on a standard PC without the Raspberry Pi. Simulates the eye without light sensor control.
2. **`pi.py`**: Runs on a Raspberry Pi with a light sensor to dynamically change the pupil size based on ambient light.



## Requirements

- **Python 3.x**
- **OpenCV**: Used for image processing and video handling
  - Install with: `pip install opencv-python`
- **Ultralytics YOLOv8**: For object detection (eyes)
  - Install with: `pip install ultralytics`
- **Tkinter**: For the GUI controls
  - Install with: `pip install tk`
- **Raspberry Pi-specific libraries (for `pi.py`)**:
  - **RPi.GPIO** (GPIO control for Pi)
  - **gpiozero** (for ADC (e.g., MCP3008) usage)
  - **MCP3008 (for reading the light sensor)**:
    - Install with: `pip install gpiozero`



## Running the Scripts

### 1. **Without Raspberry Pi** (PC Version: `main.py`)

This version simulates the eye and allows you to change the eye colors (sclera, iris, pupil) via a GUI.

#### Steps:
1. Make sure you have Python and required libraries installed.
2. Place the **`main.py`** script and the **YOLO model** (`eye-seg.pt`) in the same directory.
3. Run the script using:
   ```
   python main.py
   ```
4. The program will display the simulation in a window. You can select the sclera, iris, and pupil colors using the color pickers in the GUI.
5. Press **`q`** to exit the simulation.

### 2. **With Raspberry Pi** (Raspberry Pi Version: `pi.py`)

This version includes the light sensor (LDR or Photoresistor) connected to a Raspberry Pi, which adjusts the pupil size based on ambient light.

#### Steps:

1. **Hardware Setup**:
   - Connect a light sensor (e.g., LDR) to an ADC (e.g., MCP3008) and connect the MCP3008 to the Raspberry Pi.
   - Use `GPIO` to read values from the ADC.
2. Make sure you have **Python 3.x**, and the required libraries installed, including `RPi.GPIO`, `gpiozero`, and `MCP3008` for the light sensor.
3. Place the **`pi.py`** script and the **YOLO model** (`eye-seg.pt`) in the same directory.
4. Run the script using:
   ```
   python pi.py
   ```
5. The program will read the light sensor values and dynamically adjust the pupil size. The color pickers for the sclera, iris, and pupil are available in the GUI.

---

## Features

- **Dynamic Pupil Size**: The pupil size dynamically adjusts based on the ambient light using a light sensor connected to the Raspberry Pi.
- **Color Customization**: You can change the sclera, iris, and pupil colors using a color picker UI.
- **Tracking Toggle**: You can toggle object detection (tracking) on/off using a button in the UI.

---

## Troubleshooting

- **Problem**: "No module named 'RPi' error"
  - **Solution**: Make sure the `RPi.GPIO` library is installed on the Raspberry Pi. Run `pip install RPi.GPIO`.

- **Problem**: "YOLO model not found" error
  - **Solution**: Make sure the YOLO model file `eye-seg.pt` is present in the same directory as the script.

---

## License

This project is open-source and available under the [MIT License](LICENSE).
```

---

### Instructions:

1. **Setup**: 
   - Ensure that you have the dependencies installed based on the script you are using (`main.py` or `pi.py`).
2. **Running the Scripts**:
   - Use `main.py` on your PC for general simulation without light sensor control.
   - Use `pi.py` on your Raspberry Pi to simulate the eye and adjust the pupil size based on the light sensor input.
