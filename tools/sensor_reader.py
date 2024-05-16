import os
import time
import json
import csv
import os
import time
import json
import socket
import serial
from .mlx import *
import multiprocessing
import numpy as np
import cv2
import time

#
#
# START EDIT PARAMETERS
#
#

GAIN = 7 # Gain setting (same as firmware)
RESOLUTION = 0 # Resolution setting (same as firmware)
BAUD = 115200 # Baud rate
COM = '/dev/ttyACM1' # Serial port
ENABLE_WS = True # Enable WebSocket server. Disable if not using websocket. Script will crash otherwise.
NR_OF_SENSORS = 32 # Number of sensors
TEMP_COMP = True

#
#
# END EDIT PARAMETERS
#
#

def plot_colormap(queue):
    
    is_first = True
    zero_data = [np.zeros((8, 4)), np.zeros((8, 4)), np.zeros((8, 4))]
  
    while True:
        all_data = queue.get()
        if all_data is None:
            break
        
        components = ['X', 'Y', 'Z']
        for i in range(3):
            
            data = all_data[i * 32 : (i + 1) * 32]
            
            # Reshape the 1D array into a 2D array (4x8)
            data_matrix = np.reshape(data, (8, 4)) - zero_data[i]

            if is_first:
                zero_data[i] = data_matrix
                continue
            
            data_matrix = np.abs(data_matrix)

            # Scale the values to 0-255 for better visualization
            val_range = np.max(data_matrix)
            
            
            data_matrix = ((data_matrix) / val_range * 255).astype(np.uint8)

            # Create a colormap image using OpenCV
            colormap = cv2.applyColorMap(data_matrix, cv2.COLORMAP_BONE)

            scaled_colormap = cv2.resize(colormap, (400, 800), interpolation=cv2.INTER_NEAREST)  # Adjust the size as needed

            # Display the resized colormap image
            cv2.imshow('Map ' + components[i], scaled_colormap)
        
        if is_first:
            is_first = False
        
        cv2.waitKey(1)


ser = serial.Serial(COM, BAUD) 
    

def read_and_publish_sensor_sync(name, que):

    queue = multiprocessing.Queue()

    # Start the process
    process = multiprocessing.Process(target=plot_colormap, args=(queue,))
    process.start()
    
    level = 0
    
    prev_x = [0] * NR_OF_SENSORS
    prev_y = [0] * NR_OF_SENSORS
    prev_z = [0] * NR_OF_SENSORS
    
    cycle_x = [0] * NR_OF_SENSORS
    cycle_y = [0] * NR_OF_SENSORS
    cycle_z = [0] * NR_OF_SENSORS
    
    is_first = True

    # Define the UDP server address and port
    udp_server_address = ('localhost', 9870)

    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open( os.path.join(os.path.dirname(os.path.realpath(__file__)), f'../../data/raw/sensor/table_calibration/{name}.csv'), 'w', newline='') as csvfile:

        csv_writer = csv.writer(csvfile)
        header_row = ["t_wall [s]", "level_sensor []"]
        for i in range(NR_OF_SENSORS):
            header_row.append(f"X{i} [uT]")
            header_row.append(f"Y{i} [uT]")
            header_row.append(f"Z{i} [uT]")
            
        csv_writer.writerow(header_row)
        
        is_running = True
        
        while is_running:
        
            if not que.empty():
                cmd = que.get()
                
                if cmd[0] == "stop":
                    is_running = False
                    continue
                elif cmd[0] == "set_level":
                    level = cmd[1]           
        
            data = ser.read(1)
            if data == b'\xAA':
                data_bytes = ser.read(6 * NR_OF_SENSORS)
                row = {"t": time.time(), "level_sensor": level}

                for i in range(NR_OF_SENSORS):
                    x = ~ ( (data_bytes[i * 3 * 2] << 8) + data_bytes[i * 3 * 2 + 1] )
                    y = ~ ( (data_bytes[i * 3 * 2 + 2] << 8) + data_bytes[i * 3 * 2 + 3] )
                    z = ~ ( (data_bytes[i * 3 * 2 + 4] << 8) + data_bytes[i * 3 * 2 + 5] )

                    if not is_first:
                        
                        # Check for large jumps and correct them
                        if abs(x - prev_x[i]) > 2 ** 15:
                            cycle_x[i] += 1 if x < prev_x[i] else -1
                            
                        if abs(y - prev_y[i]) > 2 ** 15:
                            cycle_y[i] += 1 if y < prev_y[i] else -1
                        
                        if abs(z - prev_z[i]) > 2 ** 15:
                            cycle_z[i] += 1 if z < prev_z[i] else -1      
                    
                    prev_x[i] = x
                    prev_y[i] = y
                    prev_z[i] = z
                    
                    x += cycle_x[i] * 2 ** 16
                    y += cycle_y[i] * 2 ** 16
                    z += cycle_z[i] * 2 ** 16                    
                                            
                    is_first = False

                    x *= mlx90393_lsb_lookup[0][GAIN][RESOLUTION][0] 
                    y *= mlx90393_lsb_lookup[0][GAIN][RESOLUTION][0] 
                    z *= mlx90393_lsb_lookup[0][GAIN][RESOLUTION][1] 
                    
                    x += mlx90393_lsb_lookup[0][GAIN][RESOLUTION][0] * 2 ** 16
                    y += mlx90393_lsb_lookup[0][GAIN][RESOLUTION][0] * 2 ** 16
                    z += mlx90393_lsb_lookup[0][GAIN][RESOLUTION][1] * 2 ** 16

                    row[f"X{i}"] = x
                    row[f"Y{i}"] = y
                    row[f"Z{i}"] = z
 
                csvrow = [row["t"], row["level_sensor"]]
                
                for i in range(NR_OF_SENSORS):
                    csvrow.append(row[f"X{i}"])
                    csvrow.append(row[f"Y{i}"])
                    csvrow.append(row[f"Z{i}"])

                queue.put(np.array([row[f"X{i}"] for i in range(NR_OF_SENSORS)] + [row[f"Y{i}"] for i in range(NR_OF_SENSORS)] + [row[f"Z{i}"] for i in range(NR_OF_SENSORS)]))

                csv_writer.writerow(csvrow)
                json_data = json.dumps(row)
                udp_socket.sendto(json_data.encode(), udp_server_address)                

        udp_socket.close()
        queue.put(None)
        process.join()
        # ser.close()
