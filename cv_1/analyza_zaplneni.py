import cv2
import numpy as np
import os
import csv

IN_IMG_PATH = 'img'
OUT_IMG_PATH = 'out_img'
CSV_FOLDER_PATH = 'csv_out'
COLOR_THRESHOLDS = {
    'black': {'min': [0, 0, 0], 'max': [20, 20, 20]},
    'grey': {'min': [50, 50, 50], 'max': [90, 90, 90]},
    'blue': {'min': [0, 30, 60], 'max': [10, 102, 202]},
    'green': {'min': [0, 40, 0], 'max': [30, 132, 60]},
    'brown': {'min': [190, 80, 30], 'max': [240, 150, 74]},
    'red': {'min': [180, 0, 20], 'max': [205, 10, 55]}
}


def export_to_csv(data) -> None:
    csv_file = os.path.join(CSV_FOLDER_PATH, 'analyza_zaplnenosti_map.csv')
    with open(csv_file, 'w', newline='') as csv_file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames)
        writer.writeheader()
        writer.writerows(data)
    pass


def write_img(img, img_name) -> None:
    '''
    Writes out masked tif for given color
    '''
    cv2.imwrite(os.path.join(OUT_IMG_PATH, f'{img_name}.tif'), img)
    pass


def calculate_threshold_vals(img_data, img, pixels_all: int, octane_masks=False) -> dict:
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
            count_pixels //= 4

        color_sum += count_pixels

        update_img_data[color] = count_pixels
        relative_color_counts[color] = (round((count_pixels / pixels_all) * 100, 2))

    

    for c, v in relative_color_counts.items():
        relative_sum += v
        update_img_data[f'{c}_relative'] = v

    update_img_data['relative_sum'] = relative_sum
    # write composite mask for all colors

    final_mask = masks[0]
    for mask in masks[1:]:
        final_mask = final_mask | mask


    # if octane_masks == True:
        # write_img(final_mask, f'{img_name}_eight')
        # update_img_data['raster_name'] = img_name

    return update_img_data


def get_center_axies(h, w):
    centerX, centerY = (w//2), (h//2)
    return (centerX, centerY)


def halve_img(h, w, img):
    quarterX, quarterY = get_center_axies(h, w)
    quarters = {
        'topLeft': img[0:quarterY, 0:quarterX],
        'topRight': img[0:quarterY, quarterX:w],
        'bottomLeft': img[quarterY:h, 0:quarterX],
        'bottomRight': img[quarterY:h, quarterX:w],
    }

    quartered = []

    for k, v in quarters.items():
        quartered.append(v)
    return quartered


def octant_analysis(h, w, img):
    quartered = halve_img(h, w, img)
    eights_unpacked = []

    for q in quartered:
        eights = halve_img(q.shape[0], q.shape[1], q)
        for e in eights:
            eights_unpacked.append(e)

    return eights_unpacked


def get_image_statistics(images_to_compute: list) -> list:
    '''
    Calculates gceneral statistics for img
    '''
    data = []
    for img in images_to_compute:
        loaded_img = cv2.imread(img, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)

        img_data = {}

        img_name = img.rsplit('\\', 1)[1].removesuffix('.tif')
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



        eight_count = 1
                            
        for eight in octant_analysis(height, width, loaded_img):
            img_data_eights = {
                'raster_name': f'{img_name}_{eight_count}',
                'height': eight.shape[0],
                'width': eight.shape[1],
                'channels': eight.shape[2],
                'pixels_all': eight.shape[0]*eight.shape[1]
            }
            
            img_data['raster_name'] = f'{img_name}_{eight_count}'

            data.append(calculate_threshold_vals(img_data_eights, eight, pixels_all, octane_masks=True))
            eight_count +=1

            # cv2.imshow('a', eight)
            # cv2.waitKey(0)
        


        break
        # if img_name == 'zm_10_24bit':
        #     data.append(calculate_threshold_vals(img_data, loaded_img, pixels_all, img_name))
        #     data.append(octant_analysis(height, width, loaded_img))
        # else:
        #     data.append(calculate_threshold_vals(img_data, loaded_img, pixels_all, img_name))

    # print(data)
    return data


def main():
    '''
    Loads all images from \\img folder, exports results to csv
    '''
    images_to_compute = [os.path.join(IN_IMG_PATH, img_p)
                         for img_p in os.listdir(IN_IMG_PATH)]
    print(images_to_compute)
    export_to_csv(get_image_statistics(images_to_compute)) 


    # export_to_csv(get_image_statistics(images_to_compute))
pass


if __name__ == "__main__":
    pass
    main()
