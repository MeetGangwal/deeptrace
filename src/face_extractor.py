import cv2
import numpy as np
import os

class FaceExtractor:
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        
        # Build an absolute path to the local XML file in the models/ directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cascade_path = os.path.join(base_dir, 'models', 'haarcascade_frontalface_default.xml')
        
        # Load OpenCV's built-in face detector using the local file
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            raise FileNotFoundError(f"Failed to load cascade from {cascade_path}")

    def extract_face(self, image_bgr: np.ndarray):
        if image_bgr is None:
            return None, None

        h, w, _ = image_bgr.shape
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        if len(faces) == 0:
            return None, None

        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, box_w, box_h = largest_face

        margin_x = int(box_w * 0.15)
        margin_y = int(box_h * 0.15)

        x1 = max(0, x - margin_x)
        y1 = max(0, y - margin_y)
        x2 = min(w, x + box_w + margin_x)
        y2 = min(h, y + box_h + margin_y)

        cropped_face = image_bgr[y1:y2, x1:x2]
        if cropped_face.size == 0:
            return None, None

        resized_face = cv2.resize(cropped_face, self.target_size, interpolation=cv2.INTER_AREA)
        bbox_dict = {"x": x1, "y": y1, "width": x2 - x1, "height": y2 - y1}

        return resized_face, bbox_dict