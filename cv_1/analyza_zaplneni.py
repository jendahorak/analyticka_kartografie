import cv2
import numpy as np
import os
import csv

IN_IMG_PATH = 'img'
OUT_IMG_PATH = 'out_img'
CSV_FOLDER_PATH = 'csv_out'
COLOR_THRESHOLDS = {
    'black': {'min': [0,0,0], 'max': [20,20,20]},
    'grey': {'min': [50,50,50], 'max': [90,90,90]},
    'blue': {'min': [0,30,60], 'max': [10,102,202]},
    'green': {'min': [0,40,0], 'max': [30,132,60]},
    'brown': {'min': [190,80,30], 'max': [240,150,74]},
    'red': {'min': [180,0,20], 'max': [205,10,55]}
    }


def export_to_csv(data) -> None:
    csv_file = os.path.join(CSV_FOLDER_PATH, 'analyza_zaplnenosti_map.csv')
    with open(csv_file, 'w', newline='') as csv_file:           
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames)
        writer.writeheader()
        writer.writerows(data)
    pass


def write_img(img, img_name)-> None:
    '''
    Writes out masked tif for given color
    '''
    cv2.imwrite(os.path.join(OUT_IMG_PATH,f'{img_name}.tif'), img)
    pass

def calculate_threshold_vals(img_data, img, pixels_all, img_name)-> dict:
    '''
    Calculates absolute and relative amount of pixels of given color specified by COLOR_THRESHOLDS
    '''
    update_img_data = img_data
    color_sum = 0
    relative_sum = 0    
    relative_color_counts = {}
    masks = []
    color_thresholds_changing = COLOR_THRESHOLDS

    for color, values in COLOR_THRESHOLDS.items():
        color_min = np.array(values.get('min')[::-1], np.uint8)
        color_max = np.array(values.get('max')[::-1], np.uint8)
        

        image_mask = cv2.inRange(img, color_min, color_max)
        masks.append(image_mask)
        # write mask for each color

        count_pixels = cv2.countNonZero(image_mask)

        if color == 'red' or color == 'brown':
            count_pixels //=  4

        color_sum += count_pixels

        update_img_data[color] = count_pixels
        relative_color_counts[color] = (round((count_pixels / pixels_all)  * 100, 2))
    

    for c, v in relative_color_counts.items():
        relative_sum += v
        update_img_data[f'{c}_relative'] = v
    
    update_img_data['relative_sum'] = relative_sum
    # write composite mask for all colors
    final_mask = masks[0]
    for mask in masks[1:]:
        final_mask = final_mask | mask
    write_img(final_mask, f'{img_name}_composite')


    return update_img_data

def get_image_statistics(images_to_compute:list) -> list:
    '''
    Calculates general statistics for img
    '''
    data = []
    for img in images_to_compute:
        loaded_img = cv2.imread(img, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)

        img_data = {}

        img_name = img.rsplit('\\', 1)[1]
        dimensions = str(loaded_img.shape)
        height = loaded_img.shape[0]
        width = loaded_img.shape[1]
        channels = loaded_img.shape[2]
        pixels_all = height*width

        img_data = {
            'raster_name': img_name,
            'height': height,
            'width': width,
            'channels': channels,
            'pixels_all': pixels_all
        }

        data.append(calculate_threshold_vals(img_data, loaded_img, pixels_all, img_name))
    return data


def main():
    '''
    Loads all images from \\img folder, exports results to csv
    '''
    images_to_compute = [os.path.join(IN_IMG_PATH, img_p)for img_p in os.listdir(IN_IMG_PATH)]
    get_image_statistics(images_to_compute)
    export_to_csv(get_image_statistics(images_to_compute)) 
pass


if __name__ == "__main__":
    pass
    main()
