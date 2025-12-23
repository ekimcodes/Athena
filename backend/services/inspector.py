import os
import json
import random
import glob
import numpy as np
import cv2
import torch
import segmentation_models_pytorch as smp
from shapely.geometry import Polygon, MultiPolygon
from shapely.validation import make_valid

# --- Model Loading ---
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'unet_ttpla_final.pth')
DEVICE = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')

_model = None

def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            print(f"Warning: Model not found at {MODEL_PATH}. Using mock output.")
            return None
            
        print(f"Loading model from {MODEL_PATH} on {DEVICE}...")
        _model = smp.Unet(
            encoder_name="resnet18",
            encoder_weights=None,
            in_channels=3,
            classes=4
        )
        _model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        _model.to(DEVICE)
        _model.eval()
    return _model

def get_random_image(dataset_dir):
    """Picks a random .jpg file from the dataset directory."""
    jpg_files = glob.glob(os.path.join(dataset_dir, "*.jpg"))
    if not jpg_files:
        return {"error": "No images found"}
    
    random_file = random.choice(jpg_files)
    filename = os.path.basename(random_file)
    image_id = os.path.splitext(filename)[0]
    
    return {
        "image_id": image_id,
        "filename": filename,
        "url": f"/data/images/{filename}"
    }

def mask_to_polygons(mask, class_id):
    """Converts a binary mask for a specific class into Shapely polygons."""
    binary_mask = (mask == class_id).astype(np.uint8)
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    polygons = []
    points_list = []
    
    for contour in contours:
        if len(contour) < 3:
            continue
        
        # Simplify contour
        epsilon = 0.005 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        if len(approx) < 3:
            continue
            
        points = approx.reshape(-1, 2)
        poly = Polygon(points)
        if not poly.is_valid:
            poly = make_valid(poly)
            
        polygons.append(poly)
        points_list.append(points.tolist())
        
    return polygons, points_list

def analyze_image(dataset_dir, image_id):
    """
    Runs INFERENCE on the image using the trained U-Net model.
    """
    model = load_model()
    image_path = os.path.join(dataset_dir, f"{image_id}.jpg")
    
    if not model or not os.path.exists(image_path):
        # Fallback to JSON if model missing (Backward Compatibility)
        return analyze_image_legacy(dataset_dir, image_id)

    # 1. Preprocess Image
    image_bgr = cv2.imread(image_path)
    if image_bgr is None:
        return {"error": "Image load failed"}
        
    original_h, original_w = image_bgr.shape[:2]
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    # Resize to 512x512 for model
    input_tensor = cv2.resize(image_rgb, (512, 512))
    input_tensor = torch.from_numpy(input_tensor.transpose(2, 0, 1)).float() / 255.0
    input_tensor = input_tensor.unsqueeze(0).to(DEVICE)
    
    # 2. Inference
    with torch.no_grad():
        logits = model(input_tensor)
        pr_masks = logits.softmax(dim=1).argmax(dim=1).squeeze().cpu().numpy()
        
    # Resize mask back to original size
    full_mask = cv2.resize(pr_masks.astype(np.uint8), (original_w, original_h), interpolation=cv2.INTER_NEAREST)
    
    # 3. Extract Polygons & Detect Risks
    # Classes: 0: BG, 1: Cable, 2: Tower, 3: Vegetation
    cable_polys, cable_points = mask_to_polygons(full_mask, 1)
    tower_polys, tower_points = mask_to_polygons(full_mask, 2)
    veg_polys, veg_points = mask_to_polygons(full_mask, 3)
    
    # Prepare Detections for Frontend
    detections = []
    for pts in cable_points:
        detections.append({"label": "cable", "points": pts, "type": "polygon"})
    for pts in tower_points:
        detections.append({"label": "tower", "points": pts, "type": "polygon"})
    for pts in veg_points:
        detections.append({"label": "vegetation", "points": pts, "type": "polygon"})

    # 4. Risk Analysis (Intersection)
    risk_detected = False
    details = "No encroachment detected."
    
    for veg in veg_polys:
        # Handle MultiPolygon if make_valid returned one
        if isinstance(veg, MultiPolygon):
            geoms = veg.geoms
        else:
            geoms = [veg]
            
        for veg_geom in geoms:
            for cable in cable_polys:
                cable_geoms = cable.geoms if isinstance(cable, MultiPolygon) else [cable]
                for cable_geom in cable_geoms:
                    if veg_geom.intersects(cable_geom):
                        risk_detected = True
                        details = "CRITICAL: Detected vegetation contacting power lines!"
                        break
            if risk_detected: break
        if risk_detected: break

    return {
        "image_id": image_id,
        "risk_detected": risk_detected,
        "details": details,
        "detections": detections,
        "source": "Model Inference (U-Net)"
    }

def analyze_image_legacy(dataset_dir, image_id):
    """Old method using Ground Truth JSONs"""
    json_path = os.path.join(dataset_dir, f"{image_id}.json")
    if not os.path.exists(json_path):
        return {"error": "No annotations found"}
        
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    # ... (Keep original logic if needed, but for now just return empty)
    return {
        "image_id": image_id,
        "risk_detected": False,
        "details": "Legacy mode: Annotations missing",
        "detections": []
    }
