import cv2
import numpy as np
import os
import csv

IN_IMG_PATH = 'analyticka_kartografie\cv_1\img'
OUT_IMG_PATH = 'analyticka_kartografie\cv_1\out_img'
CSV_FOLDER_PATH = 'analyticka_kartografie\cv_1\csv_out'
COLOR_THRESHOLDS = {
    'black': {'min': [0,0,0], 'max': [15,15,15]},
    'grey': {'min': [57,57,57], 'max': [72,72,72]},
    'green': {'min': [15,90,25], 'max': [20,100,30]},
    'blue': {'min': [8,66,178], 'max': [23,78,200]},
    'red': {'min': [200,15,79], 'max': [210,25,95]},
    'brown': {'min': [210,130,195], 'max': [221,145,215]},
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
    relative_color_counts = {}
    masks = []

    for color, values in COLOR_THRESHOLDS.items():
        color_min = np.array(values.get('min')[::-1])
        color_max = np.array(values.get('max')[::-1])
        # print(color_min, color_max)

        image_mask = cv2.inRange(img, color_min, color_max)
        masks.append(image_mask)
        # write mask for each color
        # write_img(image_mask, f'{img_name}_{color}')

        count_pixels = cv2.countNonZero(image_mask)

        if color == 'red' or color == 'brown':
            count_pixels /=  4

        color_sum += count_pixels

        update_img_data[color] = count_pixels
        relative_color_counts[color] = (round((count_pixels / pixels_all)  * 100, 2))

        
    for c, v in relative_color_counts.items():
        update_img_data[f'{c}_relative'] = v
    
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
        loaded_img = cv2.imread(img)

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
