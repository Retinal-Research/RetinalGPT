from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches 

# Load the newly uploaded image for drawing bounding boxes
# new_image_path = '/media/xinli38/T7 Touch/V&T/IDRID/A. Segmentation/1. Original Images/a. Training Set/IDRiD_23.jpg'

# new_image_path = '/media/xinli38/T7 Touch/V&T/IDRID/A. Segmentation/1. Original Images/a. Training Set/IDRiD_32.jpg'
# new_image_path = '/media/xinli38/T7 Touch/V&T/IDRID/A. Segmentation/1. Original Images/a. Training Set/IDRiD_29.jpg'
# new_image_path = '/media/xinli38/T7 Touch/V&T/IDRID/A. Segmentation/1. Original Images/a. Training Set/IDRiD_11.jpg'
# new_image_path = '/media/xinli38/T7 Touch/V&T/IDRID/A. Segmentation/1. Original Images/b. Testing Set/IDRiD_72.jpg'
new_image_path = '/media/xinli38/T7 Touch/V&T/IDRID/A. Segmentation/2. All Segmentation Groundtruths/b. Testing Set/2. Haemorrhages/IDRiD_66_HE.tif'

new_image = Image.open(new_image_path)
new_image_array = np.array(new_image)

# Provided bounding boxes in normalized coordinates
normalized_bounding_boxes = [
        
# # IDRID 23
# [0.3713, 0.4662, 0.4937, 0.5688],

#             [
#                 0.399,
#                 0.5193,
#                 0.4184,
#                 0.5463
#             ],
#             [
#                 0.3629,
#                 0.4916,
#                 0.3666,
#                 0.4968
#             ],

    #32 
# [0.65, 0.5112, 0.71, 0.5462],

#             [
#                 0.6481,
#                 0.3841,
#                 0.7724,
#                 0.5674
#             ],

# 29
    # [0.3148, 0.5125, 0.3537, 0.5538],

    #         [
    #             0.3223,
    #             0.5091,
    #             0.3328,
    #             0.5397
    #         ],

# 11
# [0.66, 0.515, 0.7288, 0.56], 
# [0.55, 0.4637, 0.6338, 0.5462],


#             [
#                 0.5707,
#                 0.513,
#                 0.6875,
#                 0.6464
#             ],
#             [
#                 0.6229,
#                 0.4607,
#                 0.6425,
#                 0.5172
#             ],


# 72
# [0.6538, 0.5112, 0.7198, 0.6312],
# #  [0.5676, 0.5538, 0.6453, 0.6313],

#             [
#                 0.6448,
#                 0.4972,
#                 0.7771,
#                 0.7275
#             ],

[
                0.3022,
                0.6935,
                0.3176,
                0.7086
            ],
            [
                0.2621,
                0.6352,
                0.2824,
                0.6657
            ],
            [
                0.4536,
                0.4888,
                0.4627,
                0.5018
            ],
            [
                0.2048,
                0.4147,
                0.2178,
                0.4333
            ],
            [
                0.326,
                0.2777,
                0.3347,
                0.2883
            ],
            [
                0.2523,
                0.2577,
                0.3083,
                0.3143
            ]

]

# Convert normalized bounding boxes to absolute coordinates
height, width = new_image_array.shape[:2]
absolute_bounding_boxes = [
    [
        int(box[0] * width),  # x_min
        int(box[1] * height), # y_min
        int(box[2] * width),  # x_max
        int(box[3] * height)  # y_max
    ]
    for box in normalized_bounding_boxes
]

# Plot the image with bounding boxes
fig, ax = plt.subplots(figsize=(12, 12))
ax.imshow(new_image_array, cmap='gray')

first = True
count = 0
# Draw bounding boxes
for box in absolute_bounding_boxes:
    count += 1
    x_min, y_min, x_max, y_max = box
    if count == 100:
        first = False
    if first:
        rect = patches.Rectangle(
            (x_min, y_min), x_max - x_min, y_max - y_min,
            linewidth=2, edgecolor='blue', facecolor='none'
        )
        # first = False
    else:
        rect = patches.Rectangle(
            (x_min, y_min), x_max - x_min, y_max - y_min,
            linewidth=2, edgecolor='red', facecolor='none'
        )
    ax.add_patch(rect)

plt.title("Bounding Boxes on Uploaded Image")
plt.axis("off")
plt.show()