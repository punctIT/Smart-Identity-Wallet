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
    Enhanced ID card processor that handles various orientations and image qualities.
    No aggressive cropping - works with full images.
    """
    
    def __init__(self):
        """Initialize the ID Card Processor with adaptive settings."""
        pass
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load an image from the specified path."""
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
        """
        try:
            # Remove data URL prefix if present
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
                os.close(temp_fd)
            
            # Save as JPG
            cv2.imwrite(output_path, img)
            
            return output_path
            
        except Exception as e:
            raise ValueError(f"Error converting base64 to image: {e}")
    
    def image_to_base64(self, image_path: str) -> str:
        """Convert an image file to base64 string."""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            base64_string = base64.b64encode(image_data).decode('utf-8')
            return base64_string
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise ValueError(f"Error converting image to base64: {e}")
    
    def detect_orientation(self, img: np.ndarray) -> int:
        """
        Detect the orientation of the ID card and return rotation angle.
        
        Returns:
            0, 90, 180, or 270 degrees
        """
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Try OCR on all 4 orientations and pick the one with most confident text
            best_confidence = 0
            best_rotation = 0
            
            for angle in [0, 90, 180, 270]:
                try:
                    if angle == 0:
                        rotated = gray
                    elif angle == 90:
                        rotated = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
                    elif angle == 180:
                        rotated = cv2.rotate(gray, cv2.ROTATE_180)
                    else:  # 270
                        rotated = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    
                    # Simple text detection approach
                    text = pytesseract.image_to_string(rotated, lang='ron', config='--psm 3')
                    text_length = len(text.strip())
                    
                    if text_length > best_confidence:
                        best_confidence = text_length
                        best_rotation = angle
                except Exception as e:
                    print(f"Warning: Failed to check orientation {angle}: {e}")
                    continue
            
            return best_rotation
        except Exception as e:
            print(f"Warning: Orientation detection failed, using 0 degrees: {e}")
            return 0
    
    def auto_rotate_image(self, img: np.ndarray) -> np.ndarray:
        """Automatically rotate image to correct orientation."""
        try:
            angle = self.detect_orientation(img)
            
            if angle == 0:
                return img
            elif angle == 90:
                return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            elif angle == 180:
                return cv2.rotate(img, cv2.ROTATE_180)
            else:  # 270
                return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        except Exception as e:
            print(f"Warning: Auto-rotation failed, using original image: {e}")
            return img
    
    def enhance_image(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Enhanced preprocessing without aggressive cropping.
        Handles shadows, glare, and poor lighting.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Adaptive histogram equalization for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
        
        # Adaptive thresholding (better than global threshold)
        binary = cv2.adaptiveThreshold(
            denoised, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            21, 
            10
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return morph
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Complete preprocessing pipeline without cropping.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Preprocessed image ready for OCR
        """
        # Load image
        img = self.load_image(image_path)
        
        # Auto-rotate to correct orientation
        rotated = self.auto_rotate_image(img)
        
        # Enhance image quality
        processed = self.enhance_image(rotated)
        
        return processed
    
    def extract_text_full_page(self, image: np.ndarray) -> str:
        """
        Extract all text from the full image using optimal OCR settings.
        
        Args:
            image: Preprocessed image
            
        Returns:
            Extracted text
        """
        try:
            # Try multiple PSM modes for better results
            configs = [
                '--psm 3 --oem 3',  # Automatic page segmentation
                '--psm 6 --oem 3',  # Assume uniform block of text
                '--psm 4 --oem 3',  # Assume single column
            ]
            
            best_text = ""
            for config in configs:
                try:
                    text = pytesseract.image_to_string(image, config=config, lang='ron')
                    if len(text.strip()) > len(best_text):
                        best_text = text
                except Exception as e:
                    print(f"Warning: OCR with config '{config}' failed: {e}")
                    continue
            
            return best_text.strip() if best_text else ""
        except Exception as e:
            print(f"Error: All OCR attempts failed: {e}")
            return ""
    
    def extract_structured_data(self, image: np.ndarray) -> Dict:
        """
        Extract structured data from ID card using pytesseract's data output.
        
        Returns:
            Dictionary with bounding boxes and text
        """
        data = pytesseract.image_to_data(
            image, 
            output_type=pytesseract.Output.DICT,
            lang='ron',
            config='--psm 3 --oem 3'
        )
        
        return data
    
    def parse_romanian_id_card(self, text: str) -> Dict[str, str]:
        """
        Parse Romanian ID card text and extract key fields.
        Uses pattern matching instead of hardcoded positions.
        """
        import re
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        result = {
            "first_name": "",
            "last_name": "",
            "serie": "",
            "nr": "",
            "cnp": "",
            "place_of_birth": "",
            "address": "",
            "expiration_date": "",
            "success": False
        }
        
        try:
            # Combine all text for pattern matching
            full_text = ' '.join(lines)
            full_text_upper = full_text.upper()
            
            # Extract patterns
            for i, line in enumerate(lines):
                line_clean = line.strip()
                line_upper = line_clean.upper()
                
                # Look for name (usually has < symbols or all caps)
                if '<' in line_clean:
                    if not result["last_name"]:
                        parts = line_clean.split('<')
                        result["last_name"] = parts[0].strip()
                        first_parts = [p.strip() for p in parts[1:] if p.strip()]
                        result["first_name"] = ' '.join(first_parts)
                        result["success"] = True
                
                # Look for serie + number - more flexible patterns
                # Pattern: 2-3 letters followed by 6-7 digits
                serie_match = re.search(r'\b([A-Z]{2,3})\s*(\d{6,7})\b', line_upper)
                if serie_match and not result["serie"]:
                    result["serie"] = serie_match.group(1)
                    result["nr"] = serie_match.group(2)
                    result["success"] = True
                
                # Look for CNP - 13 consecutive digits
                cnp_match = re.search(r'\b([1-9]\d{12})\b', line_clean)
                if cnp_match and not result["cnp"]:
                    result["cnp"] = cnp_match.group(1)
                    result["success"] = True
                    
                    # Try to find expiration date nearby (6 digits)
                    exp_match = re.search(r'\b(\d{2}\.\d{2}\.\d{2,4})\b', full_text)
                    if exp_match:
                        result["expiration_date"] = exp_match.group(1)
                
                # Look for address keywords
                address_keywords = ['STR.', 'STRADA', 'BD.', 'BULEVARDUL', 'NR.', 'BL.', 'BLOC', 'AP.']
                if any(kw in line_upper for kw in address_keywords):
                    if not result["address"]:
                        result["address"] = line_clean
                        result["success"] = True
                
                # Look for place of birth
                birth_keywords = ['JUD.', 'JUDET', 'MUN.', 'MUNICIPIUL', 'LOC.', 'COM.', 'COMUNA']
                if any(kw in line_upper for kw in birth_keywords):
                    if not result["place_of_birth"]:
                        result["place_of_birth"] = line_clean
                        result["success"] = True
            
            # If still no name found, try alternative approaches
            if not result["last_name"]:
                # Look for lines with mostly uppercase letters
                for line in lines:
                    if len(line) > 5 and sum(1 for c in line if c.isupper()) > len(line) * 0.7:
                        words = line.split()
                        if len(words) >= 2:
                            result["last_name"] = words[0]
                            result["first_name"] = ' '.join(words[1:])
                            result["success"] = True
                            break
            
            # Clean up empty strings
            result = {k: v.strip() if isinstance(v, str) else v for k, v in result.items()}
            
            return result
            
        except Exception as e:
            print(f"Error parsing ID card data: {e}")
            result["success"] = False
            result["error"] = str(e)
            return result
    
    def process_id_card(self, image_path: str) -> Dict[str, str]:
        """
        Complete processing pipeline: preprocess, extract, and parse.
        
        Args:
            image_path: Path to the ID card image
            
        Returns:
            Dictionary with all processed field values
        """
        # Preprocess image
        processed_image = self.preprocess_image(image_path)
        
        # Extract all text
        full_text = self.extract_text_full_page(processed_image)
        
        # Parse structured data
        result = self.parse_romanian_id_card(full_text)
        
        # Store raw text for debugging
        result["_raw_text"] = full_text
        
        return result
    
    def process_id_card_from_base64(self, base64_string: str, cleanup_temp: bool = True) -> Dict[str, str]:
        """
        Process an ID card from a base64 string.
        
        Args:
            base64_string: Base64 encoded image string
            cleanup_temp: Whether to delete the temporary image file after processing
            
        Returns:
            Dictionary with all processed field values
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
    
    def save_processed_image(self, image_path: str, output_path: str = "processed_image.jpg"):
        """Save the preprocessed image for debugging."""
        processed_image = self.preprocess_image(image_path)
        cv2.imwrite(output_path, processed_image)
        print(f"[✔] Processed image saved to {output_path}")
    
    def visualize_text_regions(self, image_path: str, output_path: str = "text_regions.jpg"):
        """
        Visualize detected text regions on the image.
        Useful for debugging.
        """
        img = self.load_image(image_path)
        rotated = self.auto_rotate_image(img)
        processed = self.enhance_image(rotated)
        
        # Get structured data with bounding boxes
        data = self.extract_structured_data(processed)
        
        # Convert back to color for visualization
        color_img = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
        
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 30:  # Only show confident detections
                (x, y, w, h) = (data['left'][i], data['top'][i], 
                               data['width'][i], data['height'][i])
                color_img = cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Add text label
                text = data['text'][i]
                if text.strip():
                    cv2.putText(color_img, text[:20], (x, y - 5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        cv2.imwrite(output_path, color_img)
        print(f"[✔] Text regions visualization saved to {output_path}")


# Example usage
if __name__ == "__main__":
    processor = IDCardProcessor()
    
    # Example 1: Process from file path
    try:
        print("Processing ID card from file...")
        result = processor.process_id_card("test.png")
        
        print("\n" + "="*50)
        print("EXTRACTED INFORMATION")
        print("="*50)
        
        for field, value in result.items():
            if field != "_raw_text":
                print(f"{field.replace('_', ' ').title()}: {value}")
        
        # Show raw text for debugging
        print("\n" + "-"*50)
        print("RAW OCR TEXT:")
        print("-"*50)
        print(result.get("_raw_text", ""))
        
        # Convert to JSON
        json_output = {k: v for k, v in result.items() if k != "_raw_text"}
        json_string = json.dumps(json_output, ensure_ascii=False, indent=2)
        print("\n" + "-"*50)
        print("JSON OUTPUT:")
        print("-"*50)
        print(json_string)
        
    except Exception as e:
        print(f"Error processing ID card: {e}")
        import traceback
        traceback.print_exc()
    
    # Example 2: Process from base64
    try:
        print("\n\nProcessing from base64...")
        base64_string = processor.image_to_base64("test.png")
        result_base64 = processor.process_id_card_from_base64(base64_string)
        
        json_output = {k: v for k, v in result_base64.items() if k != "_raw_text"}
        print("Base64 result:")
        print(json.dumps(json_output, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"Error processing from base64: {e}")
    
    # Example 3: Debug visualizations
    try:
        print("\n\nCreating debug visualizations...")
        processor.save_processed_image("test.png", "debug_processed.jpg")
        processor.visualize_text_regions("test.png", "debug_text_regions.jpg")
        print("[✔] Debug images created successfully")
    except Exception as e:
        print(f"Error creating visualizations: {e}")