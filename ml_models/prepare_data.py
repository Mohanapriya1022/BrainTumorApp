import os
import shutil
import random

# Source data
base_dir = r"d:\Finalpro\Brain Tumor labeled dataset"
# Destination organized data
target_dir = r"d:\Finalpro\Organized_Dataset"

classes = ['glioma', 'meningioma', 'notumor', 'pituitary']
split_ratio = 0.8 # 80% for training

def prepare_dataset():
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    for split in ['train', 'val']:
        for cls in classes:
            os.makedirs(os.path.join(target_dir, split, cls), exist_ok=True)

    for cls in classes:
        src_path = os.path.join(base_dir, cls)
        images = [f for f in os.listdir(src_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif'))]
        random.shuffle(images)
        
        train_count = int(len(images) * split_ratio)
        train_images = images[:train_count]
        val_images = images[train_count:]
        
        print(f"Copying {cls}: {len(train_images)} train, {len(val_images)} val")
        
        for img in train_images:
            shutil.copy(os.path.join(src_path, img), os.path.join(target_dir, 'train', cls, img))
            
        for img in val_images:
            shutil.copy(os.path.join(src_path, img), os.path.join(target_dir, 'val', cls, img))

    print(f"Dataset organized at {target_dir}")

if __name__ == "__main__":
    prepare_dataset()
