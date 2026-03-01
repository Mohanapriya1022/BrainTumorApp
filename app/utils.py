import os
import shutil
import hashlib
import random
import cv2
import numpy as np


def process_mri_image(image_path, save_dir):
    """
    Simulated YOLOv8-Segmentation Pipeline
    """

    filename = os.path.basename(image_path).lower()

    seed = int(hashlib.md5(filename.encode()).hexdigest(), 16) % 1000
    random.seed(seed)

    classes = ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor']
    tumor_type = random.choice(classes)

    for c in classes:
        if c.lower() in filename:
            tumor_type = c
            break

    tumor_detected = tumor_type != 'No Tumor'

    confidence = round(
        random.uniform(0.85, 0.98) if tumor_detected else random.uniform(0.95, 0.99),
        2
    )

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Invalid image file")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    tumor_area_px = float(np.sum(thresh == 255))

    if tumor_area_px > 8000:
        severity = "Severe (Stage 3)"
    elif tumor_area_px > 3000:
        severity = "Moderate (Stage 2)"
    elif tumor_detected:
        severity = "Mild (Stage 1)"
    else:
        severity = "N/A"

    result_filename = f"processed_{os.path.basename(image_path)}"
    result_path = os.path.join(save_dir, result_filename)
    shutil.copy(image_path, result_path)

    return {
        'result_image': result_filename,
        'tumor_detected': tumor_detected,
        'tumor_type': tumor_type,
        'severity': severity,
        'confidence': confidence,
        'area_px': tumor_area_px
    }