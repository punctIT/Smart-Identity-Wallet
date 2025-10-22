from PIL import Image, ImageEnhance,ImageDraw
import pytesseract
import time

# Load and preprocess image
# add in this dir a file named buletin.jpg with a cropped ID card
start = time.perf_counter()

image = Image.open("buletin.jpg")
width,height = image.size

roi_percent =   (0.0,0.49,1.0,1.0)
x1 = int(roi_percent[0] * width)
y1 = int(roi_percent[1] * height)
x2 = int(roi_percent[2] * width)
y2 = int(roi_percent[3] * height)
roi = image.crop((x1, y1, x2, y2)).resize((500,165)).convert("L")
bw1 = roi.crop((int(0.31*500),int(0.01*165),int(1*500),int(0.6*165))).resize((300,80)).point(lambda x: 0 if x < 86 else 255, '1')
crop_boxes = {
    "nume_full": (26,94,490,115),
    "serie_nr": (26,120,132,145),
    "cnp": (194,120,485,145)
}
crop_boxes_bw1 = {
    "place_of_birth": (0,0, 250,15 ),
    "address": (0,35,270,50)
}
# # COD PENTRU SETAT BINE CHENARELE
# overlay = bw1.copy()
# draw = ImageDraw.Draw(overlay)
# for field, box in crop_boxes_bw1.items():
#     draw.rectangle(box, outline="red", width=2)
# overlay.save("ci_front_with_boxes.jpg")
# Config per field
config_map = {
    "place_of_birth": r'--psm 13 -c tessedit_char_whitelist= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZăâîșțĂÂÎȘȚ.',
    "address": r'--psm 13 -c tessedit_char_whitelist= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZăâîșțĂÂÎȘȚ.',
    "nume_full": r'--psm 7 -c tessedit_char_whitelist=AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ< --oem 3',
    "serie_nr":  r'--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ< --oem 3',
    "cnp": r'--psm 7 -c tessedit_char_whitelist=0123456789MF --oem 3'
}
# OCR language (Romanian)
lang = "ron"
data = []
# Perform OCR for each field ___METHOD_1_________
# print("📄 Extracted fields from Romanian ID:")
for field, box in crop_boxes_bw1.items():
    region = bw1.crop(box)
    config = config_map.get(field, "--psm 7")
    text = pytesseract.image_to_string(region, config=config, lang=lang)
    cleaned = text.strip().replace("\n", " ")
    data.append((field.title(),cleaned))
    # print(f"{field.title().replace('_', ' ')}: {cleaned}")
for field, box in crop_boxes.items():
    region = roi.crop(box)
    config = config_map.get(field, "--psm 7")
    text = pytesseract.image_to_string(region, config=config, lang=lang)
    cleaned = text.strip().replace("\n", " ")
    data.append((field.title(),cleaned))
    # print(f"{field.title().replace('_', ' ')}: {cleaned}")
print(time.perf_counter() - start)
