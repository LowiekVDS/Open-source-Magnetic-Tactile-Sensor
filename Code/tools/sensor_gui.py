import multiprocessing
import numpy as np
import cv2
import time

class SensorGUI:
    
    def __init__(self) -> None:
        self.is_first = True
        self.zero_data = [np.zeros((8, 4)), np.zeros((8, 4)), np.zeros((8, 4))]
    

    def plot_colormap(self, all_data):

        components = ['X', 'Y', 'Z']
        for i in range(3):
            
            data = all_data[i * 32 : (i + 1) * 32]
            
            # Reshape the 1D array into a 2D array (4x8)
            data_matrix = np.reshape(data, (8, 4)) - self.zero_data[i]

            if self.is_first:
                self.zero_data[i] = data_matrix
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
        
        if self.is_first:
            self.is_first = False
        
        cv2.waitKey(1)
        
def play_gui(all_data, skip = 1):
    
    print(all_data.shape)
    sensor_gui = SensorGUI()
    for i in range(0, all_data.shape[0], skip):
        sensor_gui.plot_colormap(all_data[i, :])
        # time.sleep(rate)
    
    cv2.destroyAllWindows()