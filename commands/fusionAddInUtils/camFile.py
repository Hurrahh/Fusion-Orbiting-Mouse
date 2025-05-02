import adsk.core, adsk.fusion, adsk.cam
import threading
import queue
import math
import time
import asyncio
from bleak import BleakClient
import struct

# UUIDs (Replace with actual UUIDs of the BLE device)
DEVICE_ADD = "06:70:db:b3:cd:e8"
CHAR = "00000041"

# Shared queue for pitch, roll, yaw updates
latest_data = {"pitch": 0.0, "roll": 0.0, "yaw": 0.0}
lock = threading.Lock()

# Fusion 360 application objects
app = adsk.core.Application.get()
ui = app.userInterface
viewport = app.activeViewport

# Function to calculate eye position from Pitch, Roll, Yaw
def calculate_eye_position(pitch, yaw, radius, target):
    pitch_rad = math.radians(pitch)
    yaw_rad = math.radians(yaw)

    x = radius * math.sin(pitch_rad) * math.cos(yaw_rad)
    y = radius * math.sin(pitch_rad) * math.sin(yaw_rad)
    z = radius * math.cos(pitch_rad)

    return adsk.core.Point3D.create(target.x + x, target.y + y, target.z + z)

# Function to calculate radius (distance from eye to target)
def calculate_radius(eye, target):
    dx, dy, dz = eye.x - target.x, eye.y - target.y, eye.z - target.z
    return (dx**2 + dy**2 + dz**2) ** 0.5

# Function to update camera position
def update_camera():
    try:
        camera = viewport.camera
        target = camera.target
        eye = camera.eye
        radius = calculate_radius(eye, target)
        
        with lock:
           pitch =latest_data["pitch"]
           roll =latest_data["roll"]
           yaw =latest_data["yaw"]

        # Calculate new eye position
        new_eye = calculate_eye_position(pitch, yaw, radius, target)

        # Compute new upVector based on roll
        roll_rad = math.radians(roll)
        up_vector = adsk.core.Vector3D.create(math.sin(roll_rad), math.cos(roll_rad), 0)

        # Apply new camera settings
        camera.eye = new_eye
        camera.upVector = up_vector
        camera.isSmoothTransition = True
        viewport.camera = camera
        viewport.refresh()

    except Exception as e:
        ui.messageBox(f"Error updating camera: {e}")

def timer_callback(args):
    """ This function is called periodically by Fusion 360 Timer Events """
    update_camera()

async def ble():        
    async with BleakClient(DEVICE_ADD) as client:
        
        async def notification_handler(C, data):
            try:
                values = list(map(float, data.decode("utf-8").split(',')))  # Convert received data
                if len(values) == 3:
                    pitch, roll, yaw = values
                    with lock:
                        latest_data["pitch"] = pitch
                        latest_data["roll"] = roll
                        latest_data["yaw"] = yaw
            except Exception as e:
                ui.messageBox(f"BLE Data Error: {e}")
        
        print("Connected!")
        await client.start_notify(CHAR, notification_handler)
        
        while True:
            await asyncio.sleep(1)

# Camera Update Thread
# def camera_update_thread():
#     try:
#         while True:
#             if not data_queue.empty():
#                 with lock:
#                     pitch, roll, yaw = data_queue.get()
#                 adsk.doEvents()  # Ensure UI thread processing
#                 update_camera(pitch, roll, yaw)
#             time.sleep(0.1)  # Reduce CPU usage
#     except Exception as e:
#         ui.messageBox(f"Exception in camera thread {e}")

# Start the Threads
# t1 = threading.Thread(target=ble_thread, daemon=True)
# t2 = threading.Thread(target=camera_update_thread, daemon=True)

# t1.start()
# t2.start()
