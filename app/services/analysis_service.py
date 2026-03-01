import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

def calculate_tumor_area(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    tumor_pixels = np.sum(thresh == 255)
    return tumor_pixels


def generate_progression_graph(patient_reports, save_path):
    dates = []
    volumes = []

    for report in patient_reports:
        area = calculate_tumor_area(report.image_path)
        dates.append(report.created_at.strftime("%Y-%m"))
        volumes.append(area)

    plt.figure()
    plt.plot(dates, volumes, marker='o')
    plt.title("Tumor Progression")
    plt.xlabel("Date")
    plt.ylabel("Tumor Volume (Pixels)")
    plt.savefig(save_path)
    plt.close()