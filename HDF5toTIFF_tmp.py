import h5py
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import from_origin


with h5py.File('D:\Flooding model\Machine Learning\data collecting\Environment temperature\store\A.HDF5', 'r') as file:
    def explore_structure(name, node):
        if isinstance(node, h5py.Dataset):
            node_type = 'Dataset'
            node_shape = node.shape
            node_dtype = node.dtype
        elif isinstance(node, h5py.Group):
            node_type = 'Group'
            node_shape = None
            node_dtype = None
        else:
            node_type = 'Unknown'
            node_shape = None
            node_dtype = None

        print(f"{name}: {node_type}")
        if node_shape is not None:
            print(f" - Shape: {node_shape}")
        if node_dtype is not None:
            print(f" - Data Type: {node_dtype}")

    # Explore the structure
    file.visititems(explore_structure)

with h5py.File('D:\Flooding model\Machine Learning\data collecting\Environment temperature\store\A.HDF5', 'r') as file:
    surfaceTemperature = file['FS/VERENV/surfaceTemperature'][:]  # Extracting the first layer of the dataset

    latitudes = file['FS/Latitude'][:]
    longitudes = file['FS/Longitude'][:]
    year = file['FS/ScanTime/Year'][0]
    month = file['FS/ScanTime/Month'][0]
    day =  file['FS/ScanTime/DayOfMonth'][0]
    hour =  file['FS/ScanTime/Hour'][0] 
    minute = file['FS/ScanTime/Minute'][0]
    second = file['FS/ScanTime/Second'][0] 
    time = str(year) + '-' + str(month) + '-' + str(day) + '-' + str(hour) + ':' + str(minute) + ':' + str(second)
print(time)
#surfaceTemperature = surfaceTemperature.reshape((1,7925,49))
#print(surfaceTemperature.shape)

lat_min, lat_max = 24.396308, 49.384358
lon_min, lon_max = -125.0, -66.93457

# Adjusting the data to focus on Conus
lat_indices = np.where((latitudes >= lat_min) & (latitudes <= lat_max))[0]
lon_indices = np.where((longitudes >= lon_min) & (longitudes <= lon_max))[0]

surfaceTemperature_conus = surfaceTemperature[lon_indices[0]:lon_indices[-1] + 1, lat_indices[0]:lat_indices[-1] + 1]    
     
plt.figure(figsize=(10, 5))
# Plot
#plt.imshow(surfacetemperature_conus, cmap='viridis', origin='lower', aspect='auto',
#           extent=[longitudes[lon_indices[0]], longitudes[lon_indices[-1]], 
#                   latitudes[lat_indices[0]], latitudes[lat_indices[-1]]],
#           vmin=0, vmax=10)
plt.imshow(surfaceTemperature, cmap='viridis')  # You can change the colormap (cmap) as desired

# Show the plot

plt.colorbar(label='surfaceTemperature')
#plt.xlabel('Longitude')
#plt.ylabel('Latitude')
#plt.title('surfaceTemperature_conus over the Contiguous United States (CONUS)')
plt.show()