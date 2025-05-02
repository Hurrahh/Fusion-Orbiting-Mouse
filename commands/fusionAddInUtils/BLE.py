import asyncio
import queue
import struct
from bleak import BleakClient

DEVICE_ADD = "28:92:B7:56:19:DB"

CHAR_FLAG = "2A57"
CHAR_GX = " "
CHAR_GY = "00000012"
CHAR_GZ = "00000013"
CHAR_AX = "00000021"
CHAR_AY = "00000022"
CHAR_AZ = "00000023"
CHAR_MX = "00000031"
CHAR_MY = "00000032"
CHAR_MZ = "00000033"

async def ble(message_queue:queue.Queue):
    def getData(byte_array, byte_order='little'):
        return struct.unpack('f', byte_array)[0]

    async def notification_handler(C, data):
        data = getData(data)
        if(C.uuid == "00000011-0000-1000-8000-00805f9b34fb"): 
            message_queue.put(f"GX {data}")
            # with open(".ble_log.txt", 'a') as file:
                # file.write(f"GX {data}")
        elif(C.uuid == "00000012-0000-1000-8000-00805f9b34fb"): 
            message_queue.put(f"GY {data}")
            # with open(".ble_log.txt", 'a') as file:
                # file.write(f"GY {data}")
        elif(C.uuid == "00000013-0000-1000-8000-00805f9b34fb"): 
            message_queue.put(f"GZ {data}")
            # with open(".ble_log.txt", 'a') as file:
                # file.write(f"GZ {data}")
        elif(C.uuid == "00000021-0000-1000-8000-00805f9b34fb"): 
            message_queue.put(f"AX {data}")
            # with open(".ble_log.txt", 'a') as file:
                # file.write(f"AX {data}")
        elif(C.uuid == "00000022-0000-1000-8000-00805f9b34fb"): 
            message_queue.put(f"AY {data}")
            # with open(".ble_log.txt", 'a') as file:
                # file.write(f"AY {data}")
        elif(C.uuid == "00000023-0000-1000-8000-00805f9b34fb"): 
            message_queue.put(f"AZ {data}")
            # with open(".ble_log.txt", 'a') as file:
                # file.write(f"AZ {data}")
        elif(C.uuid == "00000031-0000-1000-8000-00805f9b34fb"): 
            message_queue.put(f"MX {data}")
            # with open(".ble_log.txt", 'a') as file:
                # file.write(f"MX {data}")
        elif(C.uuid == "00000032-0000-1000-8000-00805f9b34fb"): 
            message_queue.put(f"MY {data}")
            # with open(".ble_log.txt", 'a') as file:
                # file.write(f"MY {data}")
        elif(C.uuid == "00000033-0000-1000-8000-00805f9b34fb"): 
            message_queue.put(f"MZ {data}")
            # with open(".ble_log.txt", 'a') as file:
                # file.write(f"MZ {data}")
    
    async with BleakClient(DEVICE_ADD) as client:
        
        print("Connected!")
        await client.start_notify(CHAR_GX, notification_handler)
        await client.start_notify(CHAR_GY, notification_handler)
        await client.start_notify(CHAR_GZ, notification_handler)
        await client.start_notify(CHAR_AX, notification_handler)
        await client.start_notify(CHAR_AY, notification_handler)
        await client.start_notify(CHAR_AZ, notification_handler)
        await client.start_notify(CHAR_MX, notification_handler)
        await client.start_notify(CHAR_MY, notification_handler)
        await client.start_notify(CHAR_MZ, notification_handler)
        
        while True:
            await asyncio.sleep(1)

def main(message_queue:queue.Queue):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ble(message_queue))
