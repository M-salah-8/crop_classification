import ee

# get gee weekly composits images
def Composite(aoi, date, data_source):
  # Only include the bands 2,3,4,8,11,12 for Sentinel-2
  bands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12'] # select bands from NASA ARSET training
  sentinel2_w = ee.ImageCollection(data_source) \
                      .filterBounds(aoi) \
                      .filterDate(date, date.advance(1, 'week')) \
                      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
                      .select(bands) \
                      .map(lambda image: image) \
                      .mean()
  return sentinel2_w

def getWeeklySentinelComposite(startDate, endDate, data_source, aoi):
	weekDifference = ee.Date(startDate).advance(1, 'week').millis().subtract(ee.Date(startDate).millis())
	listMap = ee.List.sequence(ee.Date(startDate).millis(), ee.Date(endDate).millis(), weekDifference)
	sentinel2_weekly = ee.ImageCollection.fromImages(listMap.map(lambda dateMillis: Composite(aoi, ee.Date(dateMillis), data_source).set('date', ee.Date(dateMillis).format('YYYY-MM-dd'))))
	s2_list_size = sentinel2_weekly.size().getInfo()
	sen2w_list = sentinel2_weekly.toList(s2_list_size)
	return s2_list_size, sen2w_list

# export images to drive func
def export_image(image, aoi):
  date = image.get('date').getInfo()
  export_params = {
    'region': aoi, # Use the same geometry as the filter
    'scale': 10, # 10 m resolution
    'crs': 'EPSG:4326', # WGS 84 CRS
    'folder': 'tatti_data', # The name of the folder in your Google Drive
    'description': f's2_{date}' # The name of the file in your Google Drive
    ''
  }
  # Export the images to Google Drive
  task = ee.batch.Export.image.toDrive(image, **export_params)
  task.start()