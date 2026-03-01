from ultralytics import YOLO
import os

# Define dataset path (Organized one)
DATASET_PATH = r"d:\Finalpro\Organized_Dataset"

def train_model():
    # Load a model
    model = YOLO('yolov8n-cls.pt') 

    print(f"Starting training on {DATASET_PATH}...")
    
    # YOLOv8 expects the path to a folder containing 'train' and 'val' subfolders
    results = model.train(
        data=DATASET_PATH, 
        epochs=10, # Kept low for demonstration, increase for better accuracy
        imgsz=224, 
        batch=16,
        project='brain_tumor_cls',
        name='v1'
    )
    
    print("Training Complete.")
    print("Best model weights will be in 'brain_tumor_cls/v1/weights/best.pt'")

if __name__ == '__main__':
    if os.path.exists(DATASET_PATH):
        train_model()
    else:
        print(f"Error: Organized dataset not found at {DATASET_PATH}. Please run prepare_data.py first.")
