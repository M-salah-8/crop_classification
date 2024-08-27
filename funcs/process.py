import rasterio
import numpy as np
import glob

# add corigestring to the function
def stack_images(data_dr, output_dr):
  tif_files = sorted(glob.glob(data_dr+'/*.tif'))
  # get tifs properties from the first file
  src = rasterio.open(tif_files[0])
  meta = src.meta
  meta.update(count= len(tif_files)*7,dtype= np.float32)
  # stack images
  arrays_stack = np.zeros([len(tif_files)*7,meta['height'], meta['width']])
  for index,tif in enumerate(tif_files):
    src = rasterio.open(tif)
    array = src.read().astype(np.float32)
    ndvi = (array[3] - array[2]) / (array[3] + array[2])
    array = np.append(array, np.expand_dims(ndvi, axis=0), axis=0)
    arrays_stack[index*7+0:index*7+7] = array

  with rasterio.open(output_dr, 'w', **meta) as dst:
    dst.write(arrays_stack)