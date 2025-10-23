import cv2
import numpy as np
import pytesseract
TARGET_WIDTH = 1000
TARGET_HEIGHT = 325
# imi trebuie numai informatiile din jumatatea inferioara a pozei
X1,Y1 = 0,0.5
X2,Y2 = 1,0.94
tess_config = {
    "place_of_birth": r'--psm 13 -c tessedit_char_whitelist= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZăâîșțĂÂÎȘȚ.',
    "address": r'--psm 13 -c tessedit_char_whitelist= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZăâîșțĂÂÎȘȚ.',
    "nume_full": r'--psm 7 -c tessedit_char_whitelist=AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ< --oem 3',
    "serie_nr":  r'--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ< --oem 3',
    "cnp": r'--psm 7 -c tessedit_char_whitelist=0123456789MF --oem 3'
}
crop_boxes = {
    "nume_full": (300,94,490,115),
    # "serie_nr": (26,120,132,145),
    # "place_of_birth": (0,0, 250,15 ),
    # "address": (0,35,270,50),
    # "cnp": (390,596,970,650),
}


def crop(img_np,first_corner_x=X1,first_corner_y=Y1,second_corner_x=X2,second_corner_y=Y2):
    h,w = img_np.shape[:2]
    x1,y1 = int(first_corner_x*w),int(first_corner_y*h)
    x2,y2 = int(second_corner_x*w),int(second_corner_y*h)
    result = img_np[y1:y2,x1:x2]
    return result

def remove_shadows_and_binarize(img_bgr, ksize=61,threshold=140):
    """
    Fast shadow removal for documents.
    ksize: odd, large blur (51–151). Larger = smoother illumination model.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # estimate illumination (background)
    bg = cv2.medianBlur(gray, ksize)

    # flatten illumination (division keeps text contrast)
    norm = cv2.divide(gray, bg, scale=255)

    # optional: local contrast to pop text
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    out = clahe.apply(norm)


    _, binary = cv2.threshold(out, threshold, 255, cv2.THRESH_BINARY)

    return binary  # single-channel, perfect for OCR

def draw_crop_grid(
    image_path: str,
    crop_boxes_pct: dict = crop_boxes,
    output_path: str = "id_card_grid.jpg",
    color=(0, 255, 0),
    thickness=2
):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    imag = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    im = crop(imag)
    imag = remove_shadows_and_binarize(im)
    # cv2.imwrite("save.jpg",imag)   
    resized = cv2.resize(imag,(TARGET_WIDTH,TARGET_HEIGHT))
    cv2.imwrite("save.jpg",resized)

    # Draw each crop box as a rectangle
    for label, (x1p, y1p, x2p, y2p) in crop_boxes_pct.items():
        x1, y1 = int(x1p), int(y1p)
        x2, y2 = int(x2p), int(y2p)
        cv2.rectangle(resized, (x1, y1), (x2, y2), color, thickness)
        # Label text (optional)
        cv2.putText(resized, label, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

    # Save output
    cv2.imwrite(output_path, resized)
    print(f"[✔] Grid saved to {output_path}")

def extract_id_fields(image_path: str,crop_boxes_pct:dict = crop_boxes,tess_config:dict = tess_config):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"{image_path} not found.")
    im = crop(img)
    imag = remove_shadows_and_binarize(im)
    
    thresh = cv2.resize(imag,(TARGET_WIDTH,TARGET_HEIGHT))
    # Resize image to fixed width
    # cv2.imwrite("proba.jpg",thresh)

    results = []
    for label, (x1p, y1p, x2p, y2p) in crop_boxes_pct.items():
        x1, y1 = int(x1p), int(y1p)
        x2, y2 = int(x2p), int(y2p)
        roi = thresh[y1:y2, x1:x2]
        config = tess_config.get(label, "--psm 7")
        text = pytesseract.image_to_string(roi, config=config, lang='ron')
        cleaned = text.strip().replace("\n", " ")
        results.append((label, cleaned))

    return results

    def convert_to_json(extracted_fields):
        json_result = {}
        for label, text in extracted_fields:
            json_result[label] = text
        return json_result


# draw_crop_grid("buletin.jpg")
# rez = extract_id_fields("buletin2.jpg")
# for label,text in rez:
#     print(f"{label.title()} : {text}")
# image = cv2.imread("buletin2.jpg")
# img = remove_shadows_and_binarize(image)
img = draw_crop_grid("buletin2.jpg")
# cv2.imwrite("b2_save.jpg",img)