import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from typing import Dict, List, Tuple, Optional
import json
import base64
import tempfile
import os


class IDCardProcessor:
    """
    A class for processing Romanian ID cards using OCR.
    Handles image preprocessing, field extraction, and data conversion.
    """
    
    # Class constants
    TARGET_WIDTH = 1000
    TARGET_HEIGHT = 325
    
    # Default crop region (lower half of the image)
    DEFAULT_CROP_REGION = {
        'x1': 0, 'y1': 0.477,
        'x2': 1, 'y2': 0.94
    }
    
    # Default Tesseract configurations for each field
    DEFAULT_TESS_CONFIG = {
        "place_of_birth": r'--psm 13 -c tessedit_char_whitelist= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZăâîșțĂÂÎȘȚ.',
        "address": r'--psm 13 -c tessedit_char_whitelist= abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZăâîșțĂÂÎȘȚ.',
        "nume_full": r'--psm 7 -c tessedit_char_whitelist=AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ< --oem 3',
        "serie_nr": r'--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ< --oem 3',
        "cnp": r'--psm 7 -c tessedit_char_whitelist=0123456789MF --oem 3'
    }
    
    # Default crop boxes for each field (x1, y1, x2, y2)
    DEFAULT_CROP_BOXES = {
        "nume_full": (50, 190, 990, 245),
        "serie_nr": (50, 240, 265, 290),
        "place_of_birth": (300, 0, 750, 35),
        "address": (285, 52, 900, 86),
        "cnp": (395, 250, 980, 300),
    }
    
    def __init__(self, 
                 crop_boxes: Optional[Dict] = None,
                 tess_config: Optional[Dict] = None,
                 crop_region: Optional[Dict] = None):
        """
        Initialize the ID Card Processor.
        
        Args:
            crop_boxes: Dictionary of field crop boxes (x1, y1, x2, y2)
            tess_config: Dictionary of Tesseract configurations for each field
            crop_region: Dictionary defining the crop region (x1, y1, x2, y2)
        """
        self.crop_boxes = crop_boxes or self.DEFAULT_CROP_BOXES.copy()
        self.tess_config = tess_config or self.DEFAULT_TESS_CONFIG.copy()
        self.crop_region = crop_region or self.DEFAULT_CROP_REGION.copy()
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load an image from the specified path.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Loaded image as numpy array
            
        Raises:
            FileNotFoundError: If image file is not found
        """
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        return img
    
    def base64_to_image(self, base64_string: str, output_path: Optional[str] = None) -> str:
        """
        Convert a base64 string to a JPG image file.
        
        Args:
            base64_string: Base64 encoded image string
            output_path: Optional output path. If None, creates a temporary file
            
        Returns:
            Path to the created image file
            
        Raises:
            ValueError: If base64 string is invalid
        """
        try:
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64 string
            image_data = base64.b64decode(base64_string)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            
            # Decode image
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("Invalid image data in base64 string")
            
            # Generate output path if not provided
            if output_path is None:
                temp_fd, output_path = tempfile.mkstemp(suffix='.jpg')
                os.close(temp_fd)  # Close the file descriptor
            
            # Save as JPG
            cv2.imwrite(output_path, img)
            
            return output_path
            
        except Exception as e:
            raise ValueError(f"Error converting base64 to image: {e}")
    
    def image_to_base64(self, image_path: str) -> str:
        """
        Convert an image file to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string of the image
            
        Raises:
            FileNotFoundError: If image file is not found
        """
        try:
            # Read the image file
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Encode to base64
            base64_string = base64.b64encode(image_data).decode('utf-8')
            
            return base64_string
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise ValueError(f"Error converting image to base64: {e}")
    
    def process_id_card_from_base64(self, base64_string: str, cleanup_temp: bool = True) -> Dict[str, str]:
        """
        Process an ID card from a base64 string.
        
        Args:
            base64_string: Base64 encoded image string
            cleanup_temp: Whether to delete the temporary image file after processing
            
        Returns:
            Dictionary with all processed field values
            
        Raises:
            ValueError: If base64 string is invalid
        """
        temp_image_path = None
        try:
            # Convert base64 to temporary image file
            temp_image_path = self.base64_to_image(base64_string)
            
            # Process the temporary image
            result = self.process_id_card(temp_image_path)
            
            return result
            
        finally:
            # Clean up temporary file if requested
            if cleanup_temp and temp_image_path and os.path.exists(temp_image_path):
                try:
                    os.remove(temp_image_path)
                except Exception as e:
                    print(f"Warning: Could not delete temporary file {temp_image_path}: {e}")
    
    def crop_image(self, img: np.ndarray) -> np.ndarray:
        """
        Crop the image to the specified region and rotate 90 degrees counterclockwise.
        
        Args:
            img: Input image
            
        Returns:
            Cropped and rotated image
        """
        img_rotated = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        h, w = img_rotated.shape[:2]
        
        x1 = int(self.crop_region['x1'] * w)
        y1 = int(self.crop_region['y1'] * h)
        x2 = int(self.crop_region['x2'] * w)
        y2 = int(self.crop_region['y2'] * h)
        
        return img_rotated[y1:y2, x1:x2]
    
    def remove_shadows_and_binarize(self, img_bgr: np.ndarray, 
                                   ksize: int = 61, 
                                   threshold: int = 80) -> np.ndarray:
        """
        Remove shadows and binarize the image for better OCR results.
        
        Args:
            img_bgr: Input BGR image
            ksize: Kernel size for median blur (should be odd)
            threshold: Binary threshold value
            
        Returns:
            Binarized grayscale image
        """
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Estimate illumination (background)
        bg = cv2.medianBlur(gray, ksize)
        
        # Flatten illumination (division keeps text contrast)
        norm = cv2.divide(gray, bg, scale=255)
        
        # Optional: local contrast to enhance text
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(norm)
        
        # Binarize
        _, binary = cv2.threshold(enhanced, threshold, 255, cv2.THRESH_BINARY)
        
        return binary
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Complete preprocessing pipeline: load, crop, remove shadows, and resize.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Preprocessed image ready for OCR
        """
        img = self.load_image(image_path)
        cropped = self.crop_image(img)
        processed = self.remove_shadows_and_binarize(cropped)
        resized = cv2.resize(processed, (self.TARGET_WIDTH, self.TARGET_HEIGHT))
        return resized
    
    def extract_field_text(self, image: np.ndarray, field_name: str) -> str:
        """
        Extract text from a specific field using OCR.
        
        Args:
            image: Preprocessed image
            field_name: Name of the field to extract
            
        Returns:
            Extracted and cleaned text
        """
        if field_name not in self.crop_boxes:
            raise ValueError(f"Unknown field: {field_name}")
        
        x1, y1, x2, y2 = self.crop_boxes[field_name]
        roi = image[y1:y2, x1:x2]
        
        config = self.tess_config.get(field_name, "--psm 7")
        text = pytesseract.image_to_string(roi, config=config, lang='ron')
        
        return text.strip().replace("\n", " ")
    
    def extract_all_fields(self, image_path: str) -> List[Tuple[str, str]]:
        """
        Extract all configured fields from the ID card image.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            List of tuples (field_name, extracted_text)
        """
        processed_image = self.preprocess_image(image_path)
        
        results = []
        for field_name in self.crop_boxes.keys():
            text = self.extract_field_text(processed_image, field_name)
            results.append((field_name, text))
        
        return results
    
    def _process_full_name(self, text: str) -> Dict[str, str]:
        """Process the full name field to extract first and last names."""
        remaining_str = text[5:] if len(text) > 5 else text
        
        first_bracket_pos = remaining_str.find('<')
        
        if first_bracket_pos == -1:
            last_name = remaining_str
            first_name = ""
        else:
            last_name = remaining_str[:first_bracket_pos]
            first_name_part = remaining_str[first_bracket_pos:]
            first_name = first_name_part.replace('<', '-').strip('-')
        
        return {"first_name": first_name, "last_name": last_name}
    
    def _process_serie_nr(self, text: str) -> Dict[str, str]:
        """Process the series number field."""
        processed_text = "".join(text.split()).upper()
        return {
            "serie": processed_text[:2],
            "nr": processed_text[2:]
        }
    
    def _process_cnp(self, text: str) -> Dict[str, str]:
        """Process the CNP field to extract CNP and expiration date."""
        # Find gender marker (M or F)
        gender_pos = -1
        gender_char = ""
        
        for i, char in enumerate(text):
            if char in ['M', 'F']:
                gender_pos = i
                gender_char = char
                break
        
        if gender_pos == -1:
            raise ValueError("No M or F found in CNP string")
        
        # Extract first two digits
        first_two_digits = text[:2]
        first_two_number = int(first_two_digits)
        
        # Determine first digit of CNP based on gender and year
        if gender_char == 'M':
            first_digit = '1' if first_two_number > 20 else '5'
        else:  # gender_char == 'F'
            first_digit = '2' if first_two_number > 20 else '6'
        
        # Construct CNP and expiration date
        first_six = text[:6]
        last_six = text[-6:]
        cnp = first_digit + first_six + last_six
        remaining_part = text[6:-6]
        
        return {
            "cnp": cnp,
            "expiration_date": remaining_part[-6:] if remaining_part else ""
        }
    
    def convert_to_json(self, extracted_fields: List[Tuple[str, str]]) -> Dict[str, str]:
        """
        Convert extracted OCR fields to a structured JSON format.
        
        Args:
            extracted_fields: List of tuples (field_name, extracted_text)
            
        Returns:
            Dictionary with processed field values
        """
        json_result = {}
        
        for field_name, text in extracted_fields:
            if field_name == "nume_full":
                json_result.update(self._process_full_name(text))
            elif field_name == "serie_nr":
                json_result.update(self._process_serie_nr(text))
            elif field_name == "place_of_birth":
                json_result["place_of_birth"] = text
            elif field_name == "address":
                json_result["address"] = text
            elif field_name == "cnp":
                json_result.update(self._process_cnp(text))
            else:
                # Default processing for unknown fields
                json_result[field_name] = " ".join(text.split())
        
        return json_result
    
    def process_id_card(self, image_path: str) -> Dict[str, str]:
        """
        Complete processing pipeline: extract fields and convert to JSON.
        
        Args:
            image_path: Path to the ID card image
            
        Returns:
            Dictionary with all processed field values
        """
        extracted_fields = self.extract_all_fields(image_path)
        return self.convert_to_json(extracted_fields)
    
    def draw_crop_grid(self, image_path: str, output_path: str = "id_card_grid.jpg",
                      color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2):
        """
        Draw crop boxes on the image for visualization and debugging.
        
        Args:
            image_path: Path to the input image
            output_path: Path to save the output image with grid
            color: Color of the grid lines (BGR format)
            thickness: Thickness of the grid lines
        """
        processed_image = self.preprocess_image(image_path)
        
        # Convert to color for drawing
        color_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
        
        # Draw each crop box
        for label, (x1, y1, x2, y2) in self.crop_boxes.items():
            cv2.rectangle(color_image, (x1, y1), (x2, y2), color, thickness)
            cv2.putText(color_image, label, (x1, y1 - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
        
        cv2.imwrite(output_path, color_image)
        print(f"[✔] Grid saved to {output_path}")
    
    def save_processed_image(self, image_path: str, output_path: str = "processed_image.jpg"):
        """
        Save the preprocessed image for debugging purposes.
        
        Args:
            image_path: Path to the input image
            output_path: Path to save the processed image
        """
        processed_image = self.preprocess_image(image_path)
        cv2.imwrite(output_path, processed_image)
        print(f"[✔] Processed image saved to {output_path}")


# Example usage
if __name__ == "__main__":
    processor = IDCardProcessor()
    
    # Example 1: Process from file path and get JSON result
    try:
        result = processor.process_id_card("test.png")
        print("Extracted Information from file:")
        print("-" * 40)
        for field, value in result.items():
            print(f"{field.replace('_', ' ').title()}: {value}")
        
        # Get JSON string if needed
        json_string = json.dumps(result, ensure_ascii=False, indent=2)
        print("\nJSON Result:")
        print(json_string)
        
        # Convert image to base64
        base64_string = processor.image_to_base64("test.png")
        print(f"\n[✔] Image converted to base64 (length: {len(base64_string)} characters)")
        
    except Exception as e:
        print(f"Error processing ID card from file: {e}")
    
    # Example 2: Process from base64 string and get JSON result
    try:
        # First convert an existing image to base64 for demonstration
        base64_string = processor.image_to_base64("test.png")
        
        # Then process the base64 string
        result_from_base64 = processor.process_id_card_from_base64(base64_string)
        print("\n\nExtracted Information from base64:")
        print("-" * 40)
        for field, value in result_from_base64.items():
            print(f"{field.replace('_', ' ').title()}: {value}")
        
        # Get JSON string
        json_string_from_base64 = json.dumps(result_from_base64, ensure_ascii=False, indent=2)
        print("\nJSON Result from base64:")
        print(json_string_from_base64)
        
    except Exception as e:
        print(f"Error processing ID card from base64: {e}")