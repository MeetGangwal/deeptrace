# import os
# import shutil
# import random
# from pathlib import Path

# def split_dataset(raw_dir="data/raw", processed_dir="data/processed", split_ratio=0.8):
#     # Depending on how the Kaggle zip extracted, locate the real/fake folders
#     raw_path = Path(raw_dir)
    
#     # Check possible paths
#     real_src = raw_path / "real" if (raw_path / "real").exists() else raw_path / "Deep_Fakes" / "Real"
#     fake_src = raw_path / "fake" if (raw_path / "fake").exists() else raw_path / "Deep_Fakes" / "Fake"

#     for category, source_dir in [("real", real_src), ("fake", fake_src)]:
#         images = [f for f in os.listdir(source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
#         random.shuffle(images)
        
#         # 80% for training, 20% for validation
#         split_idx = int(len(images) * split_ratio)
#         train_imgs = images[:split_idx]
#         val_imgs = images[split_idx:]
        
#         # Define destination paths
#         train_dest = Path(processed_dir) / "train" / category
#         val_dest = Path(processed_dir) / "val" / category
        
#         # Create directories if they don't exist
#         train_dest.mkdir(parents=True, exist_ok=True)
#         val_dest.mkdir(parents=True, exist_ok=True)
        
#         print(f"Copying {category} -> {len(train_imgs)} to train, {len(val_imgs)} to val")
        
#         for img in train_imgs:
#             shutil.copy(source_dir / img, train_dest / img)
            
#         for img in val_imgs:
#             shutil.copy(source_dir / img, val_dest / img)

# if __name__ == "__main__":
#     print("⏳ Splitting dataset...")
#     split_dataset()
#     print("✅ Dataset splitting complete!")

import os
import shutil
import random

def split_dataset(val_split=0.2):
    raw_dir = "data/raw/deepfake_frames_3990_20f"
    processed_dir = "data/processed"
    
    print("⏳ Cleaning old processed data...")
    if os.path.exists(processed_dir):
        shutil.rmtree(processed_dir)
        
    for split in ['train', 'val']:
        for category in ['real', 'fake']:
            os.makedirs(os.path.join(processed_dir, split, category), exist_ok=True)
            
    print("⏳ Scanning pre-grouped video folders...")
    
    def process_category(category):
        cat_dir = os.path.join(raw_dir, category)
        if not os.path.exists(cat_dir):
            print(f"❌ Error: Could not find {cat_dir}")
            return 0, 0
            
        # Get all the video subfolders (e.g., 'celebdf_celeb_synthesis_id0...')
        video_folders = [f for f in os.listdir(cat_dir) if os.path.isdir(os.path.join(cat_dir, f))]
        
        # Shuffle consistently
        random.seed(42)
        random.shuffle(video_folders)
        
        val_idx = int(len(video_folders) * val_split)
        val_vids = video_folders[:val_idx]
        train_vids = video_folders[val_idx:]
        
        def copy_frames(vid_list, split_name):
            count = 0
            for vid in vid_list:
                vid_path = os.path.join(cat_dir, vid)
                frames = [f for f in os.listdir(vid_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                for frame in frames:
                    src = os.path.join(vid_path, frame)
                    # We rename the frame slightly to ensure unique filenames across the whole dataset
                    new_filename = f"{vid}_{frame}"
                    dst = os.path.join(processed_dir, split_name, category, new_filename)
                    shutil.copy2(src, dst)
                    count += 1
            return count
            
        print(f"⏳ Copying {category.capitalize()} images...")
        val_count = copy_frames(val_vids, 'val')
        train_count = copy_frames(train_vids, 'train')
        
        return train_count, val_count

    train_real, val_real = process_category('real')
    train_fake, val_fake = process_category('fake')
    
    print("\n✅ Dataset splitting complete!")
    print(f"Real -> Train: {train_real} | Val: {val_real}")
    print(f"Fake -> Train: {train_fake} | Val: {val_fake}")

if __name__ == "__main__":
    split_dataset()