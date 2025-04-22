import cv2
import numpy as np
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from PIL import Image

router = APIRouter()

def extract_finger_regions_and_lines(image_bytes: bytes, min_contour_area=1500):
    # Read image from bytes
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    finger_imgs = []
    finger_line_imgs = []
    contour_draw = img.copy()
    cv2.drawContours(contour_draw, contours, -1, (0, 255, 0), 2)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_contour_area:
            x, y, w, h = cv2.boundingRect(cnt)
            finger_crop = img[y:y+h, x:x+w]
            # Try to detect fingerprint-like lines using edge detection
            finger_gray = cv2.cvtColor(finger_crop, cv2.COLOR_BGR2GRAY)
            finger_blur = cv2.GaussianBlur(finger_gray, (3, 3), 0)
            edges = cv2.Canny(finger_blur, 50, 150)
            # Overlay detected edges in red on the finger crop
            finger_lines = cv2.cvtColor(finger_gray, cv2.COLOR_GRAY2BGR)
            finger_lines[edges > 0] = [0, 0, 255]
            _, buf1 = cv2.imencode('.jpg', finger_crop)
            _, buf2 = cv2.imencode('.jpg', finger_lines)
            finger_imgs.append(buf1.tobytes())
            finger_line_imgs.append(buf2.tobytes())
    # Also return the overall contour image
    _, contour_buf = cv2.imencode('.jpg', contour_draw)
    return finger_imgs, finger_line_imgs, contour_buf.tobytes()

@router.post("/fingerprint/extract-fingers")
async def extract_fingers_api(image: UploadFile = File(...)):
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    image_bytes = await image.read()
    try:
        fingers, finger_lines, contour_img = extract_finger_regions_and_lines(image_bytes)
        import base64
        fingers_b64 = [base64.b64encode(f).decode('utf-8') for f in fingers]
        finger_lines_b64 = [base64.b64encode(f).decode('utf-8') for f in finger_lines]
        contour_b64 = base64.b64encode(contour_img).decode('utf-8')
        return {
            "num_fingers": len(fingers_b64),
            "fingers": fingers_b64,
            "finger_lines": finger_lines_b64,
            "contour_img": contour_b64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting fingers: {str(e)}")
