import cv2
import torch
import numpy as np
from torchvision import transforms
from model import DeepfakeDetector, get_device

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register forward and backward hooks to capture activation maps and gradients
        self.target_layer.register_forward_hook(self._save_activations)
        self.target_layer.register_full_backward_hook(self._save_gradients)

    def _save_activations(self, module, input, output):
        self.activations = output.detach()

    def _save_gradients(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate_heatmap(self, input_tensor, target_class=0):
        """
        Generates a 2D normalized heatmap (0.0 to 1.0) for the target class.
        Class 0 = Fake, Class 1 = Real.
        """
        self.model.zero_grad()
        output = self.model(input_tensor)
        
        # Backpropagate only the score of the target class
        score = output[0, target_class]
        score.backward()

        # Global average pooling over gradients
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        activations = self.activations[0]

        # Weight the channels by corresponding gradients
        for i in range(activations.shape[0]):
            activations[i, :, :] *= pooled_gradients[i]

        heatmap = torch.mean(activations, dim=0).cpu().numpy()
        heatmap = np.maximum(heatmap, 0) # ReLU to retain positive influence
        
        if np.max(heatmap) > 0:
            heatmap /= np.max(heatmap)
            
        return heatmap

    def locate_suspicious_region(self, heatmap, threshold=0.6):
        """
        Identifies the high-activation bounding box and maps it to a facial region.
        """
        heatmap_resized = cv2.resize(heatmap, (224, 224))
        mask = (heatmap_resized > threshold).astype(np.uint8)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None, "General Face"

        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        center_y = y + (h / 2)
        # Vertical heuristic relative to 224x224 face alignment
        if center_y < 80:
            region = "Forehead / Eyes"
        elif center_y < 140:
            region = "Nose / Cheek Area"
        else:
            region = "Mouth / Jawline"

        return {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}, region

if __name__ == "__main__":
    device = get_device()
    checkpoint = torch.load("models/deepfake_detector.pt", map_location=device)
    
    model = DeepfakeDetector(num_classes=2, pretrained=False).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    # Hook into layer4 (the final conv block of ResNet-18)
    cam = GradCAM(model, model.backbone.layer4)
    print("✅ GradCAM module initialized and hooked to ResNet-18 layer4.")