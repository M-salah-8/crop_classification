import os
import rasterio
# from rasterio.warp import transform_bounds
import numpy as np
import matplotlib.patches as patches
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.font_manager import FontProperties
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import rasterio.warp

# Plot Class profiles over our dataset
def plot_class_profiles(class_dfs, class_colors, class_names, bands):
	fig = plt.figure(figsize = (17,20))
	n=1 #counter
	for band in bands: # Iterate over band names
		ax = fig.add_subplot(4,2,n)
		ax.set_title(band)
		band_vals = []
		for class_df in class_dfs:
			band_vals.append(class_df[class_df.columns[class_df.columns.to_series().str.contains(band)]])
		for c in range(4):
			for index, row in band_vals[c].iterrows(): # Plot line for each class in the selected band
				ax.plot(row, color=class_colors[c])
		ax.set_xticks(range(len(row)))
		ax.set_xticklabels([str(x) for x in range(1, len(row)+1)]) # Replace column names with numbers
		handles = [plt.Line2D([], [], color=color) for color in class_colors]
		ax.legend(handles=handles, loc="best", fontsize='small', ncol=2, labels=class_names)
		n = n+1
	plt.show()
	plt.close()

# Plot Class profiles over our dataset (mean)
def plot_class_profiles_mean(train_pts, class_colors, class_names, bands):
	grouped_tp = train_pts.groupby(['type']).mean()
	fig = plt.figure(figsize = (17,20))
	n=1 #counter
	for band in bands: # Iterate over band names
		ax = fig.add_subplot(4,2,n)
		ax.title.set_text(band)
		band_val = grouped_tp[grouped_tp.columns[grouped_tp.columns.to_series().str.contains(band)]] # Select all columns in the dataframe containing a band name e.g. B2
		i = 0
		for index, row in band_val.iterrows(): # Plot line for each class in the selected band
			ax.plot(row, color=class_colors[i])
			i = i+1
		ax.set_xticks(range(len(row)))
		ax.set_xticklabels([str(x) for x in range(1, len(row)+1)]) # Replace column names with numbers
		ax.legend(loc="best", fontsize='small', ncol=2, labels=class_names)
		n = n+1
	plt.show()
	plt.close()

class Map():
	def draw_north_arrow(self, ax):
		arrow_ax = inset_axes(ax, width="10%", height="10%", loc=3)
		arrow_scale = 0.7
		arrow_ax.set_aspect('equal', adjustable='box')
		ax_length = arrow_ax.get_xlim()[1]-arrow_ax.get_xlim()[0]
		ax_height = arrow_ax.get_ylim()[1]-arrow_ax.get_ylim()[0]
		shape_length = ax_length * arrow_scale
		padding_length = ((1-arrow_scale)/2) * ax_length
		base_start= arrow_ax.get_xlim()[0] + padding_length
		base_end = base_start + shape_length
		height_start= arrow_ax.get_ylim()[0] + padding_length
		height_end = height_start + shape_length
		width = shape_length
		height = shape_length
		x_bottom_left ,y_bottom_left = base_start, height_start
		x_top, y_top = width / 2 + base_start, height_end
		x_bottom_right, y_bottom_right = base_end, height_start
		x_mid, y_mid = width / 2 + base_start, height / 4 + height_start
		line_width = arrow_ax.transData.transform((0, 1))[1]*0.003

		arrow_polygon = patches.Polygon([[x_bottom_left, y_bottom_left], [x_top, y_top], [x_bottom_right, y_bottom_right],[x_mid,y_mid]],
						facecolor= 'goldenrod', edgecolor= 'black', linewidth= line_width)
		hashs = patches.Polygon([[x_top, y_top], [x_bottom_right, y_bottom_right],[x_mid,y_mid]],
						facecolor= 'darkgoldenrod', hatch = '//////',
						edgecolor= 'black', linewidth= line_width)
		# gray_background = patches.Rectangle((arrow_ax.get_xlim()[0], arrow_ax.get_ylim()[0]), ax_length, ax_height, facecolor= 'gray', alpha=0.5)
		# draw a rectangle that covers the whole axes that has a gray color with low capacity
		# arrow_ax.add_patch(gray_background)
		arrow_ax.add_patch(arrow_polygon)
		arrow_ax.add_patch(hashs)
		text_x = width / 2 + base_start
		# text_y = height / 2.2 + height_start
		text_y = ax_length * 0.05
		arrow_ax.text(text_x, text_y, 'N', ha='center', va='center', fontsize=arrow_ax.transData.transform((0, 1))[1]*0.015, fontweight='bold', color= 'black')
		arrow_ax.set_axis_off()

	def draw_scale_bar(self, ax, src):
		bbox = src.bounds
		if src.crs.to_string() == 'EPSG:4326':
			center_lon = (bbox.left + bbox.right) / 2
			utm_zone = int((center_lon + 180) / 6) + 1
			utm_crs = rasterio.crs.CRS.from_string(f"EPSG:326{utm_zone}")
			transform , proj_width, proj_height = rasterio.warp.calculate_default_transform(src.crs, utm_crs, src.width, src.height, *bbox)
		elif src.crs.to_string().startswith('EPSG:326') or src.crs.to_string().startswith('EPSG:327'):
			transform = src.transform
			proj_width, proj_height = src.width, src.height
		else:
			print("CRS not supported")
		x_scale = transform[0]
		y_scale = transform[4]
		scale = abs(x_scale)

		width = scale * proj_width
		scale_bar_length = str(round(width * 0.1))
		scale_bar_length = int(scale_bar_length[0] + '0' * (len(scale_bar_length) - 1))
		scale_bar_percentage = str((scale_bar_length / width) * 100)

		scale_ax = inset_axes(ax, width=f"{scale_bar_percentage}%", height="10%", loc=3,
							bbox_to_anchor=(0.1, 0, 1, 1), bbox_transform=ax.transAxes)
		ax_length = scale_ax.get_xlim()[1]-scale_ax.get_xlim()[0]
		ax_height = scale_ax.get_ylim()[1]-scale_ax.get_ylim()[0]
		width = ax_length
		height = ax_length * 0.2
		x_bottom_left= scale_ax.get_xlim()[0]
		y_bottom_left= scale_ax.get_ylim()[0] + ax_height * 0.5 - height * 0.5

		line_rectangle = patches.Rectangle((x_bottom_left, y_bottom_left), width, height,
						facecolor= 'black', edgecolor= 'black', linewidth= scale_ax.transData.transform((0, 1))[1]*0.001)
		black_rectangel = patches.Rectangle((x_bottom_left, y_bottom_left), width/2, height,
						facecolor= 'white', edgecolor= 'black', linewidth= scale_ax.transData.transform((0, 1))[1]*0.001)
		# gray_background = patches.Rectangle((x_bottom_left, y_bottom_left), ax_length, ax_height/2 + height * 0.5, facecolor= 'gray', alpha=0.5)
		# scale_ax.add_patch(gray_background)
		scale_ax.add_patch(line_rectangle)
		scale_ax.add_patch(black_rectangel)
		text_x = width / 2
		text_y = scale_ax.get_ylim()[0] + ax_height * 0.5 + height
		bar_font_size = scale_ax.transData.transform((0, 1))[1]*0.015
		scale_ax.text(text_x, text_y, str(scale_bar_length)+" m", ha='center', va='bottom', fontsize=bar_font_size, fontweight='bold', color= 'black', bbox=dict(facecolor='white', edgecolor='white', pad=0))
		scale_ax.set_axis_off()

	def to_deg(self, decimal_degrees):
		degrees = int(decimal_degrees)
		minutes = int((decimal_degrees - degrees) * 60)
		seconds = int(((decimal_degrees - degrees) * 60 - minutes) * 60)

		if abs(decimal_degrees) < 0.00001:
				return f'{degrees}°00\'00\"'
		elif abs(decimal_degrees) < 0.0001:
				return f'{degrees}°{minutes}\'{seconds}"'
		else:
				return f'{degrees}°{minutes}\'{seconds}"'

	def set_map_ticks(self, ax, src):
		bbox = src.bounds
		bbox = rasterio.warp.transform_bounds(src.crs, 'EPSG:4326', *bbox)
		xlim = ax.get_xlim()
		ylim = ax.get_ylim()
		xticks = [self.to_deg(i)+" E" for i in [bbox[0]+((bbox[2]-bbox[0])/8), (bbox[0]+bbox[2])/2, bbox[2]-((bbox[2]-bbox[0])/8)]]
		yticks = [self.to_deg(i)+" N" for i in [bbox[1]+((bbox[3]-bbox[1])/8), (bbox[1]+bbox[3])/2, bbox[3]-((bbox[3]-bbox[1])/8)]]
		ax.set_xticks([xlim[0]+((xlim[1]-xlim[0])/8), (xlim[0]+xlim[1])/2, xlim[1]-((xlim[1]-xlim[0])/8)])  # set x ticks to 3
		ax.set_xticklabels(xticks)
		ax.set_yticks([ylim[0]+((ylim[1]-ylim[0])/8), (ylim[0]+ylim[1])/2, ylim[1]-((ylim[1]-ylim[0])/8)])  # set y ticks to 3
		ax.set_yticklabels(yticks,rotation=90, va='center')
	
	def draw_map(self, src, class_names, class_colors, title):
		array = src.read(1).astype(np.float32)
		array[array == src.nodata] = np.nan
		_, ax = plt.subplots(facecolor = 'white')
		ax.imshow(array, cmap=ListedColormap(class_colors))
		self.draw_north_arrow(ax)
		self.draw_scale_bar(ax, src)
		self.set_map_ticks(ax, src)
		ax.grid(color='black', linestyle='-', linewidth=0.5)
		ax.legend(handles=[mpatches.Patch(color=class_colors[i], label=class_names[i]) for i in range(len(class_names))], 
						loc='best', bbox_to_anchor=(1, 1), fontsize=8)
		ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
		plt.savefig(os.path.join('results', f'{title.replace(" ", "_")}.png'), dpi=300, bbox_inches='tight')
		plt.show()
		plt.close()

def draw_table(table_df, title):
	fig, ax = plt.subplots(facecolor= 'white')
	table = ax.table(cellText=table_df.values, colLabels=table_df.columns, loc='center', cellLoc='center')
	table.auto_set_font_size(False)
	for (row, col), cell in table.get_celld().items():
		if (row == 0) or (col == 0):
			cell.set_text_props(fontproperties=FontProperties(weight='bold'))
	table.set_fontsize(8)
	ax.set_title(title, fontsize=14, fontweight='bold')
	ax.axis('off')
	fig.tight_layout()
	plt.savefig(os.path.join('results', f'{title.lower().replace(" ", "_")}.png'), dpi=300, bbox_inches='tight')
	plt.show()
	plt.close()