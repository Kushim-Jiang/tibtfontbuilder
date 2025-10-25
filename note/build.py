import cv2
import numpy as np
import os

import cv2
import numpy as np
import os


def find_peaks(projection, threshold=0.5):
    max_val = np.max(projection)
    threshold_val = max_val * threshold
    peaks = []
    in_peak = False
    for i, val in enumerate(projection):
        if val > threshold_val and not in_peak:
            in_peak = True
            start = i
        elif val <= threshold_val and in_peak:
            in_peak = False
            end = i
            peaks.append((start + end) // 2)
    if in_peak:
        peaks.append((start + len(projection)) // 2)
    return peaks


def segment_table_cells(
    image_path, output_dir="cells", threshold=0.5, min_width=400, min_height=500, cell_list: list = []
):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    h_proj = np.sum(binary, axis=1)
    v_proj = np.sum(binary, axis=0)
    h_lines = find_peaks(h_proj, threshold)
    v_lines = find_peaks(v_proj, threshold)
    print(f"检测到 {len(h_lines)} 条横线, {len(v_lines)} 条竖线")
    os.makedirs(output_dir, exist_ok=True)

    cell_id = 0
    for i in range(len(h_lines) - 1):
        for j in range(len(v_lines) - 1):
            y1, y2 = h_lines[i], h_lines[i + 1]
            x1, x2 = v_lines[j], v_lines[j + 1]
            cell = img[y1:y2, x1:x2]

            h, w = cell.shape
            if w >= min_width and h >= min_height:
                if cell_list:
                    cell_filename = os.path.join(output_dir, f"{cell_list[cell_id]}.png")
                else:
                    cell_filename = os.path.join(output_dir, f"cell_{cell_id+1}.png")
                cv2.imwrite(cell_filename, cell)
                cell_id += 1
    print(f"共保存符合尺寸要求的 {cell_id} 个单元格图像到 {output_dir}/")


def get_list_a(prefix: int):
    return [f"u{prefix*16*16 + i*16 + j:05X}" for j in range(16) for i in range(16)]


def get_list_b(a: int, b: int):
    result = ["_1", "_2"]
    for i in range(0, (b - a + 1) // 2):
        hex_str1 = f"{(a + i):05X}"
        hex_str2 = f"{(a + i + (b-a+1)//2):05X}"
        result.append(f"u{hex_str1}")
        result.append(f"u{hex_str2}")
    return result


for index in range(30, 102):
    offset = 22 if index == 101 else 80
    segment_table_cells(
        f"22238/22238-2008-gbt-e-300_{index:03d}.jpg",
        output_dir="filtered_names",
        threshold=0.7,
        min_width=2000,
        min_height=100,
        cell_list=get_list_b(0xF0000 + 80 * (index - 30), 0xF0000 + 80 * (index - 30) + offset),
    )
