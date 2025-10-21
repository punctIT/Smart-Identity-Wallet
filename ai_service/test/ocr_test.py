from PIL import Image, ImageEnhance,ImageDraw
import pytesseract
import time

# Load and preprocess image
# add in this dir a file named buletin.jpg with a cropped ID card
image = Image.open("buletin.jpg")
image = image.resize((1000, 650))  # normalize size
gray = image.convert("L")  # grayscale
bw = gray.point(lambda x: 0 if x < 85 else 255, '1')  # binarize

#bw.save("ci.jpg")

crop_boxes = {
    "series":      (608, 96, 645, 125),
    "number":      (690, 96, 800, 125),
    "cnp":         (375, 118, 605, 150),
    "last_name":   (326, 170, 550, 200),
    "first_name":  (326, 217, 680, 247),
    "nationality": (326, 265, 540, 297),
    "place of birth": (326, 359, 650, 395),

}


# # COD PENTRU SETAT BINE CHENARELE
# overlay = image.copy()
# draw = ImageDraw.Draw(overlay)

# for field, box in crop_boxes.items():
#     draw.rectangle(box, outline="red", width=3)
#     draw.text((box[0], box[1] - 15), field, fill="red")  # label field

# overlay.save("ci_front_with_boxes.jpg")

# Config per field
config_map = {
    "series":      r'--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    "number":      r'--psm 8 -c tessedit_char_whitelist=0123456789',
    "cnp":         r'--psm 7 -c tessedit_char_whitelist=0123456789',
    "last_name":   r'--psm 7 -c tessedit_char_whitelist=AĂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ',
    "first_name":  r'--psm 7 -c tessedit_char_whitelist=AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ-',
    "nationality": r'--psm 7',
    "place of birth": r'--psm 7'
}

# OCR language (Romanian)
lang = "ron"

# Perform OCR for each field ___METHOD_1_________
print("📄 Extracted fields from Romanian ID:")
times = []
for _ in range(10):
    start = time.perf_counter()
    for field, box in crop_boxes.items():
        region = bw.crop(box)
        config = config_map.get(field, "--psm 6")
        text = pytesseract.image_to_string(region, config=config, lang=lang)
        cleaned = text.strip().replace("\n", " ")
    times.append(time.perf_counter() - start)
        #print(f"{field.title().replace('_', ' ')}: {cleaned}")