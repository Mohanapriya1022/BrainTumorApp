from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_pdf(report, save_path):

    c = canvas.Canvas(save_path, pagesize=letter)

    c.drawString(100, 750, "Brain Tumor Clinical Report")
    c.drawString(100, 730, f"Patient: {report.patient.name}")
    c.drawString(100, 710, f"Tumor Type: {report.tumor_type}")
    c.drawString(100, 690, f"Tumor Level: {report.tumor_level}")

    c.drawString(100, 660, "Doctor Comments:")
    c.drawString(100, 640, report.doctor_comments or "Pending")

    image_path = report.image_path
    if os.path.exists(image_path):
        c.drawImage(image_path, 100, 400, width=200, height=200)

    c.save()