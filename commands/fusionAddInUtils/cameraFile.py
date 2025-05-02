import adsk.core, adsk.fusion, adsk.cam
import threading
import queue
import math
import time
import asyncio
from bleak import BleakClient
import struct

DEVICE_ADD = "06:70:db:b3:cd:e8"
CHAR = "00000041"

data_queue = queue.Queue()
lock = threading.Lock()

app = adsk.core.Application.get()
ui = app.userInterface
viewport = app.activeViewport

def calculate_eye_position(pitch, yaw, radius, target):
    pitch_rad = math.radians(pitch)
    yaw_rad = math.radians(yaw)

    x = radius * math.sin(pitch_rad) * math.cos(yaw_rad)
    y = radius * math.sin(pitch_rad) * math.sin(yaw_rad)
    z = radius * math.cos(pitch_rad)

    return adsk.core.Point3D.create(target.x + x, target.y + y, target.z + z)

def calculate_radius(eye, target):
    dx, dy, dz = eye.x - target.x, eye.y - target.y, eye.z - target.z
    return (dx**2 + dy**2 + dz**2) ** 0.5

def update_camera(pitch, roll, yaw):
    try:
        camera = viewport.camera
        target = camera.target
        eye = camera.eye
        radius = calculate_radius(eye, target)

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


async def ble():
    def getData(byte_array, byte_order='little'):
        return struct.unpack('f', byte_array)[0]

    async def notification_handler(C, data):
        # values = list(map(float, data.decode("utf-8").split(',')))
        try:
                values = list(map(float, data.decode("utf-8").split(',')))  # Convert received data
                if len(values) == 3:
                    pitch, roll, yaw = values
                    with lock:
                        data_queue.put((pitch, roll, yaw))  # Add to queue
        except Exception as e:
            ui.messageBox(f"BLE Data Error: {e}")
        # message_queue.put(f"{data}")
        # with open(".ble_log.txt", 'a') as file:
            # file.write(f"GX {data}")
        
    async with BleakClient(DEVICE_ADD) as client:
        
        print("Connected!")
        await client.start_notify(CHAR, notification_handler)
        
        while True:
            await asyncio.sleep(1)


# BLE Client Thread
async def run_ble_client():
    async with BleakClient(DEVICE_ADD) as client:
        async def notification_handler(sender, data):
            try:
                values = list(map(float, data.decode("utf-8").split(',')))  # Convert received data
                if len(values) == 3:
                    pitch, roll, yaw = values
                    with lock:
                        data_queue.put((pitch, roll, yaw))  # Add to queue
            except Exception as e:
                ui.messageBox(f"BLE Data Error: {e}")

        # await client.start_notify(PITCH_CHAR_UUID, notification_handler)
        # await client.start_notify(ROLL_CHAR_UUID, notification_handler)
        # await client.start_notify(YAW_CHAR_UUID, notification_handler)

        while True:
            await asyncio.sleep(1)  # Keep the async loop running

def ble_thread():
    asyncio.run(run_ble_client())

# Camera Update Thread
def camera_update_thread():
    try:
        while True:
            if not data_queue.empty():
                with lock:
                    pitch, roll, yaw = data_queue.get()
                adsk.doEvents()  # Ensure UI thread processing
                update_camera(pitch, roll, yaw)
            time.sleep(0.1)  # Reduce CPU usage
    except Exception as e:
        ui.messageBox(f"Exception in camera thread {e}")

# Start the Threads
# t1 = threading.Thread(target=ble_thread, daemon=True)
# t2 = threading.Thread(target=camera_update_thread, daemon=True)

# t1.start()
# t2.start()
