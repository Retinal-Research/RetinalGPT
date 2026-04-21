import argparse
import json
import os
from collections import defaultdict

import cv2


def merge_close_bounding_boxes(bounding_boxes, threshold):
    merged_boxes = []
    for box in bounding_boxes:
        x_min, y_min, x_max, y_max = box[0], box[1], box[2], box[3]
        merged = False
        for merged_box in merged_boxes:
            mx_min, my_min, mx_max, my_max = merged_box[0], merged_box[1], merged_box[2], merged_box[3]
            if (abs(x_min - mx_max) <= threshold or abs(x_max - mx_min) <= threshold) and \
               (abs(y_min - my_max) <= threshold or abs(y_max - my_min) <= threshold):
                merged_box[0] = min(mx_min, x_min)
                merged_box[1] = min(my_min, y_min)
                merged_box[2] = max(mx_max, x_max)
                merged_box[3] = max(my_max, y_max)
                merged = True
                break
        if not merged:
            merged_boxes.append([x_min, y_min, x_max, y_max])
    return merged_boxes


def filter_overlapping_boxes(bounding_boxes, overlap_threshold=0.5):
    filtered_boxes = []
    for i, box1 in enumerate(bounding_boxes):
        x1_min, y1_min, x1_max, y1_max = box1
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        keep = True
        for j, box2 in enumerate(bounding_boxes):
            if i == j:
                continue
            x2_min, y2_min, x2_max, y2_max = box2
            inter_x_min = max(x1_min, x2_min)
            inter_y_min = max(y1_min, y2_min)
            inter_x_max = min(x1_max, x2_max)
            inter_y_max = min(y1_max, y2_max)
            inter_area = max(0, inter_x_max - inter_x_min) * max(0, inter_y_max - inter_y_min)
            area2 = (x2_max - x2_min) * (y2_max - y2_min)
            if inter_area / area1 > overlap_threshold or inter_area / area2 > overlap_threshold:
                if area1 < area2:
                    keep = False
                    break
        if keep:
            filtered_boxes.append(box1)
    return filtered_boxes


def filter_small_boxes_relative(bounding_boxes, min_relative_area=0.05):
    if not bounding_boxes:
        return []

    total_area = sum((box[2] - box[0]) * (box[3] - box[1]) for box in bounding_boxes)
    avg_area = total_area / len(bounding_boxes)

    return [
        box for box in bounding_boxes
        if (box[2] - box[0]) * (box[3] - box[1]) >= avg_area * min_relative_area
    ]


def adjust_threshold(bounding_boxes, max_boxes, initial_threshold=10, step=5):
    threshold = initial_threshold
    while True:
        merged_boxes = merge_close_bounding_boxes(bounding_boxes, threshold)
        merged_boxes = filter_overlapping_boxes(merged_boxes)
        merged_boxes = filter_small_boxes_relative(merged_boxes)
        if len(merged_boxes) <= max_boxes:
            return merged_boxes
        threshold += step


def _normalize_boxes(boxes, width, height):
    return [
        [
            round(box[0] / width, 4),
            round(box[1] / height, 4),
            round(box[2] / width, 4),
            round(box[3] / height, 4)
        ]
        for box in boxes
    ]


def generate_bounding_boxes(
    mask_folder,
    output_file,
    max_boxes=10,
    initial_threshold=50,
    step=5,
    grouped_by_lesion_type=False
):
    results = defaultdict(lambda: defaultdict(list)) if grouped_by_lesion_type else {}

    mask_type_map = {
        "EX": "Hard Exudates",
        "HE": "Haemorrhages",
        "MA": "Microaneurysms",
        "SE": "Soft Exudates"
    }

    for filename in os.listdir(mask_folder):
        if not filename.endswith((".png", ".jpg", ".jpeg", ".tif")):
            continue

        mask_path = os.path.join(mask_folder, filename)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"Unable to read file: {filename}")
            continue

        height, width = mask.shape[:2]
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bounding_boxes = [
            [int(x), int(y), int(x + w), int(y + h)]
            for (x, y, w, h) in [cv2.boundingRect(cnt) for cnt in contours]
        ]

        adjusted_boxes = adjust_threshold(
            bounding_boxes,
            max_boxes=max_boxes,
            initial_threshold=initial_threshold,
            step=step
        )
        normalized_boxes = _normalize_boxes(adjusted_boxes, width, height)

        if grouped_by_lesion_type:
            base_name = os.path.splitext(filename)[0]
            parts = base_name.split("_")
            if len(parts) < 3:
                print(f"Unable to parse grouped mask filename: {filename}")
                continue
            image_id = f"{parts[0]}_{parts[1]}"
            mask_type = mask_type_map.get(parts[2], parts[2])
            results[image_id][mask_type].extend(normalized_boxes)
        else:
            results[filename] = normalized_boxes

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    print(f"Bounding boxes saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate normalized bounding boxes from lesion masks.")
    parser.add_argument("--mask-folder", required=True, help="Folder containing mask images.")
    parser.add_argument("--output-file", required=True, help="Output JSON path.")
    parser.add_argument("--max-boxes", type=int, default=10)
    parser.add_argument("--initial-threshold", type=int, default=50)
    parser.add_argument("--step", type=int, default=5)
    parser.add_argument("--grouped-by-lesion-type", action="store_true")
    args = parser.parse_args()

    generate_bounding_boxes(
        mask_folder=args.mask_folder,
        output_file=args.output_file,
        max_boxes=args.max_boxes,
        initial_threshold=args.initial_threshold,
        step=args.step,
        grouped_by_lesion_type=args.grouped_by_lesion_type
    )


if __name__ == "__main__":
    main()
