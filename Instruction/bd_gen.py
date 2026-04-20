import os
import cv2
import json
from collections import defaultdict

# 输入 mask 文件夹路径和输出结果路径
mask_folder = "MICCAI/task2/masks"  # 替换为你的 mask 文件夹路径
output_file = "MICCAI/task2/bounding_boxes.json"


# 初始化结果存储
results = defaultdict(lambda: defaultdict(list))

# 合并近距离的病灶函数
def merge_close_bounding_boxes(bounding_boxes, threshold):
    merged_boxes = []
    for box in bounding_boxes:
        x_min, y_min, x_max, y_max = box[0], box[1], box[2], box[3]
        merged = False
        for merged_box in merged_boxes:
            mx_min, my_min, mx_max, my_max = merged_box[0], merged_box[1], merged_box[2], merged_box[3]
            # 检查是否接近
            if (abs(x_min - mx_max) <= threshold or abs(x_max - mx_min) <= threshold) and \
               (abs(y_min - my_max) <= threshold or abs(y_max - my_min) <= threshold):
                # 更新现有的合并框
                merged_box[0] = min(mx_min, x_min)
                merged_box[1] = min(my_min, y_min)
                merged_box[2] = max(mx_max, x_max)
                merged_box[3] = max(my_max, y_max)
                merged = True
                break
        if not merged:
            merged_boxes.append([x_min, y_min, x_max, y_max])
    return merged_boxes

# 检查并过滤重叠面积过大的框
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
            # 计算交集
            inter_x_min = max(x1_min, x2_min)
            inter_y_min = max(y1_min, y2_min)
            inter_x_max = min(x1_max, x2_max)
            inter_y_max = min(y1_max, y2_max)
            inter_area = max(0, inter_x_max - inter_x_min) * max(0, inter_y_max - inter_y_min)
            # 计算 box2 面积
            area2 = (x2_max - x2_min) * (y2_max - y2_min)
            # 如果交集面积占 box1 或 box2 的比例过大
            if inter_area / area1 > overlap_threshold or inter_area / area2 > overlap_threshold:
                if area1 < area2:
                    keep = False
                    break
        if keep:
            filtered_boxes.append(box1)
    return filtered_boxes

# 忽略过小的框（相对所有框面积）
def filter_small_boxes_relative(bounding_boxes, min_relative_area=0.05):
    if not bounding_boxes:
        return []

    # 计算所有框的平均面积
    total_area = sum((box[2] - box[0]) * (box[3] - box[1]) for box in bounding_boxes)
    avg_area = total_area / len(bounding_boxes)

    # 过滤掉面积小于平均面积的指定比例的框
    return [
        box for box in bounding_boxes
        if (box[2] - box[0]) * (box[3] - box[1]) >= avg_area * min_relative_area
    ]

# 动态调整阈值以满足指定的最大框数量
def adjust_threshold(bounding_boxes, max_boxes, initial_threshold=10, step=5):
    threshold = initial_threshold
    while True:
        merged_boxes = merge_close_bounding_boxes(bounding_boxes, threshold)
        merged_boxes = filter_overlapping_boxes(merged_boxes)  # 添加过滤步骤
        merged_boxes = filter_small_boxes_relative(merged_boxes)  # 添加过滤相对过小框步骤
        if len(merged_boxes) <= max_boxes:
            return merged_boxes
        threshold += step

# # 遍历文件夹中的所有文件
# for filename in os.listdir(mask_folder):
#     # 检查是否为图像文件
#     if filename.endswith(('.png', '.jpg', '.jpeg', '.tif')):
#         # 解析文件名获取图像 ID 和类型（例如 HE, MA）
#         base_name, ext = os.path.splitext(filename)
#         parts = base_name.split("_")
#         if len(parts) < 3:
#             print(f"无法解析文件名: {filename}")
#             continue
#         image_id = f"{parts[0]}_{parts[1]}"
#         mask_type = parts[2]

#         # 读取 mask 图像
#         mask_path = os.path.join(mask_folder, filename)
#         mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

#         if mask is None:
#             print(f"无法读取文件: {filename}")
#             continue

#         # 获取图像尺寸以便归一化
#         height, width = mask.shape[:2]

#         # 找到目标轮廓
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         # 提取每个轮廓的 bounding box
#         bounding_boxes = [
#             [
#                 int(x),
#                 int(y),
#                 int(x + w),
#                 int(y + h)
#             ]
#             for (x, y, w, h) in [cv2.boundingRect(cnt) for cnt in contours]
#         ]

#         # 动态调整阈值以限制最多保留 10 个 bounding boxes
#         adjusted_boxes = adjust_threshold(bounding_boxes, max_boxes=10, initial_threshold=20, step=2)

#         # 对坐标进行归一化
#         normalized_boxes = [
#             [
#                 round(box[0] / width, 4),
#                 round(box[1] / height, 4),
#                 round(box[2] / width, 4),
#                 round(box[3] / height, 4)
#             ]
#             for box in adjusted_boxes
#         ]

#         m_t = ''
#         if mask_type == "EX":
#             m_t = "Hard Exudates"
#         elif mask_type == "HE":
#             m_t = "Haemorrhages"
#         elif mask_type == "MA":
#             m_t = "Microaneurysms"
#         elif mask_type == "SE":
#             m_t = "Soft Exudates"

#         # 将结果存储到字典中
#         results[image_id][m_t].extend(normalized_boxes)

# # 将结果保存为 JSON 文件
# with open(output_file, "w") as f:
#     json.dump(results, f, indent=4)

# print(f"Bounding boxes 已保存到: {output_file}")



# 遍历文件夹中的所有文件
for filename in os.listdir(mask_folder):
    # 检查是否为图像文件
    if filename.endswith(('.png', '.jpg', '.jpeg', '.tif')):
        # 读取 mask 图像
        mask_path = os.path.join(mask_folder, filename)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

        if mask is None:
            print(f"无法读取文件: {filename}")
            continue

        # 获取图像尺寸以便归一化
        height, width = mask.shape[:2]

        # 找到目标轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 提取每个轮廓的 bounding box
        bounding_boxes = [
            [
                int(x),
                int(y),
                int(x + w),
                int(y + h)
            ]
            for (x, y, w, h) in [cv2.boundingRect(cnt) for cnt in contours]
        ]

        # 动态调整阈值以限制最多保留 10 个 bounding boxes
        adjusted_boxes = adjust_threshold(bounding_boxes, max_boxes=10, initial_threshold=50, step=5)

        # 对坐标进行归一化
        normalized_boxes = [
            [
                round(box[0] / width, 4),
                round(box[1] / height, 4),
                round(box[2] / width, 4),
                round(box[3] / height, 4)
            ]
            for box in adjusted_boxes
        ]

        # 将结果存储到字典中
        results[filename] = normalized_boxes

# 将结果保存为 JSON 文件
with open(output_file, "w") as f:
    json.dump(results, f, indent=4)

print(f"Bounding boxes 已保存到: {output_file}")
