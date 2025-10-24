import cv2
import numpy as np
import pytesseract
TARGET_WIDTH = 1000
TARGET_HEIGHT = 325
# imi trebuie numai informatiile din jumatatea inferioara a pozei
X1,Y1 = 0,0.477
X2,Y2 = 1,0.94
tess_config = {
    "place_of_birth": r'--psm 13 -c tessedit_char_whitelist= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZăâîșțĂÂÎȘȚ.',
    "address": r'--psm 13 -c tessedit_char_whitelist= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZăâîșțĂÂÎȘȚ.',
    "nume_full": r'--psm 7 -c tessedit_char_whitelist=AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ< --oem 3',
    "serie_nr":  r'--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ< --oem 3',
    "cnp": r'--psm 7 -c tessedit_char_whitelist=0123456789MF --oem 3'
}
crop_boxes = {
    "nume_full": (50,190,990,245),
    "serie_nr": (50,240,265,290),
    "place_of_birth": (300,0,750,35 ),
    "address": (285,52,900,86),
    "cnp": (395,250,980,300),
}


def crop(img,first_corner_x=X1,first_corner_y=Y1,second_corner_x=X2,second_corner_y=Y2):
    img_np = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    h,w = img_np.shape[:2]
    x1,y1 = int(first_corner_x*w),int(first_corner_y*h)
    x2,y2 = int(second_corner_x*w),int(second_corner_y*h)
    result = img_np[y1:y2,x1:x2]
    return result

def remove_shadows_and_binarize(img_bgr, ksize=61,threshold=80):
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
    im = crop(img)
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
    """
    Convert extracted OCR fields to JSON format with individual processing for each field.
    
    Args:
        extracted_fields: List of tuples (label, text) from OCR extraction
        
    Returns:
        dict: JSON object with processed field values
    """
    json_result = {}
    
    for label, text in extracted_fields:
        # Process each field individually based on its name
        if label == "nume_full":
            input_str = text
            remaining_str = input_str[5:]
            
            first_bracket_pos = remaining_str.find('<')
            
            if first_bracket_pos == -1:
                last_name = remaining_str
                first_name = ""
            else:
                # Last name is from start until first '<'
                last_name = remaining_str[:first_bracket_pos]
                
                # First name part is from first '<' onwards
                first_name_part = remaining_str[first_bracket_pos:]
                
                # Replace '<' with '-' and clean up
                first_name = first_name_part.replace('<', '-')
                
                # Remove trailing '-' characters
                first_name = first_name.rstrip('-')
                
                # Remove leading '-' if present
                first_name = first_name.lstrip('-')
            json_result["first_name"] = first_name
            json_result["last_name"] = last_name

        elif label == "serie_nr":
            # Process series number - remove spaces, keep only alphanumeric
            processed_text = "".join(text.split()).upper()
            json_result["serie"] = processed_text[:2]
            json_result["nr"] = processed_text[2:]
            
        elif label == "place_of_birth":
            # Process place of birth - capitalize first letter of each word
            processed_text = text
            json_result["place_of_birth"] = processed_text
            
        elif label == "address":
            # Process address - capitalize first letter of each word
            processed_text = text
            json_result["address"] = processed_text
            
        elif label == "cnp":
            # Process CNP - keep only digits
            input_string = text 
    
            # Find the M or F in the string
            gender_pos = -1
            gender_char = ""
            
            for i, char in enumerate(input_string):
                if char in ['M', 'F']:
                    gender_pos = i
                    gender_char = char
                    break
            
            if gender_pos == -1:
                raise ValueError("No M or F found in string")
            
            # Extract the first 2 digits after M/F
            first_two_digits = input_string[:2]
            first_two_number = int(first_two_digits)
            
            # Determine the first digit of CNP based on rules
            if gender_char == 'M':
                if first_two_number > 20:
                    first_digit = '1'
                else:
                    first_digit = '5'
            else:  # gender_char == 'F'
                if first_two_number > 20:
                    first_digit = '2'
                else:
                    first_digit = '6'
            
            # Get first 6 characters of the original string
            first_six = input_string[:6]
            
            # Get last 6 characters of the original string
            last_six = input_string[-6:]
            
            # Construct CNP
            cnp = first_digit + first_six + last_six
            
            # The remaining part would be everything else
            remaining_part = input_string[6:-6]  # Middle part excluding first 6 and last 6

            json_result["cnp"] = cnp
            json_result["expiration_date"] = remaining_part[-6:]
            
        else:
            # Default processing for unknown fields - just clean whitespace
            processed_text = " ".join(text.split())
            json_result[label] = processed_text
    
    return json_result


# draw_crop_grid("buletin.jpg")
res = extract_id_fields("buletin2.jpg")
rez =convert_to_json(res)
for label,text in rez.items():
    print(f"{label.title()} : {text}")
# image = cv2.imread("buletin2.jpg")
# img = remove_shadows_and_binarize(image)
# img = draw_crop_grid("buletin2.jpg")
# cv2.imwrite("b2_save.jpg",img)