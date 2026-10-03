import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import base64
import time
import cv2
import torch
import numpy as np
from PIL import Image
import io
from torchvision import transforms

from model import DeepfakeDetector, get_device
from face_extractor import FaceExtractor
from explainability import GradCAM

class InferenceService:
    def __init__(self, checkpoint_path="models/deepfake_detector.pt"):
        self.device = get_device()
        print(f"Loading deepfake model onto {self.device}...")
        
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.class_names = checkpoint["class_names"]
        
        self.model = DeepfakeDetector(num_classes=len(self.class_names), pretrained=False).to(self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()

        self.cam = GradCAM(self.model, self.model.backbone.layer4)
        self.extractor = FaceExtractor()
        
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

    def decode_base64_image(self, base64_str: str) -> np.ndarray:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        img_bytes = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def analyze_frame(self, base64_str: str, timestamp: float = 0.0):
        start_time = time.time()
        frame_bgr = self.decode_base64_image(base64_str)
        
        # 1. Face Extraction
        cropped_face, face_box = self.extractor.extract_face(frame_bgr)
        if cropped_face is None:
            return {
                "status": "no_face_detected",
                "prediction": "Unknown",
                "confidence": 0.0,
                "is_fake": False,
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }

        # 2. Preprocess Face Crop
        face_rgb = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
        tensor = self.transform(face_rgb).unsqueeze(0).to(self.device)

        # 3. Model Inference
        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.softmax(outputs, dim=1)[0]
            fake_prob = probs[0].item()
            real_prob = probs[1].item()

        # 4. Explainability / Localization (if classified as manipulated)
        is_fake = fake_prob >= 0.70
        signals = []
        manipulation_box = None
        region_name = None

        if is_fake:
            signals.append("Facial artifact detected")
            with torch.enable_grad():
                heatmap = self.cam.generate_heatmap(tensor, target_class=0)
                box, region = self.cam.locate_suspicious_region(heatmap)
                manipulation_box = box
                region_name = region
                signals.append(f"Inconsistency localized around: {region}")

        latency = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "success",
            "prediction": "Potential Manipulation" if is_fake else "Authentic Media",
            "confidence": round(fake_prob if is_fake else real_prob, 4),
            "is_fake": is_fake,
            "suspicious_region_name": region_name,
            "face_box": face_box,
            "manipulation_box": manipulation_box,
            "signals": signals,
            "latency_ms": latency
        }