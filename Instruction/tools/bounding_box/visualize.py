import argparse
import json

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from PIL import Image


def visualize_normalized_boxes(image_path, normalized_bounding_boxes, cmap=None):
    image = Image.open(image_path)
    image_array = np.array(image)
    height, width = image_array.shape[:2]

    absolute_bounding_boxes = [
        [
            int(box[0] * width),
            int(box[1] * height),
            int(box[2] * width),
            int(box[3] * height)
        ]
        for box in normalized_bounding_boxes
    ]

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(image_array, cmap=cmap)

    for box in absolute_bounding_boxes:
        x_min, y_min, x_max, y_max = box
        rect = patches.Rectangle(
            (x_min, y_min),
            x_max - x_min,
            y_max - y_min,
            linewidth=2,
            edgecolor="blue",
            facecolor="none"
        )
        ax.add_patch(rect)

    plt.title("Bounding Boxes")
    plt.axis("off")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Visualize normalized bounding boxes on an image.")
    parser.add_argument("--image-path", required=True)
    parser.add_argument(
        "--boxes-json",
        required=True,
        help="JSON string representing a list of normalized boxes."
    )
    parser.add_argument("--cmap", default=None)
    args = parser.parse_args()

    boxes = json.loads(args.boxes_json)
    visualize_normalized_boxes(args.image_path, boxes, cmap=args.cmap)


if __name__ == "__main__":
    main()
