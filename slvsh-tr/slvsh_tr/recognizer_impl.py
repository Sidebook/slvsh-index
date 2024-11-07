from slvsh_tr.recognizer import Recognizer
import cv2
import numpy as np
import pytesseract

class RegionalTesseractRecognizer(Recognizer):
    TESSERACT_CONFIG = '--psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,. /"'

    def __init__(self):
        pass

    def whiten_red_and_green(self, image: cv2.typing.MatLike) -> cv2.typing.MatLike:
        # BGRからHSV色空間に変換
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 緑色の範囲を定義（HSV色空間）
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        
        # 赤色の範囲を定義（HSV色空間）- 明るい赤のみ
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # マスクの作成
        mask_green = cv2.inRange(hsv_image, lower_green, upper_green)
        mask_red2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask_green, mask_red2)
        # 結果画像の作成
        result = image.copy()
        result[mask > 0] = [255, 255, 255]
        
        return result

    def find_text_region(self, image: cv2.typing.MatLike) -> tuple:
        height, width = image.shape[:2]
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY) #真っ白の四角を対象にする
        
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > width * 0.05 and h > height * 0.9:
                # 右端または左端にアラインされているか確認
                if x < width * 0.05 or x + w > width * 0.95:
                    text_regions.append((x, y, w, h))
        
        if text_regions:
            # 幅が最大のものを2つ返す(Revengeの場合があるので)
            return sorted(text_regions, key=lambda r: r[2], reverse=True)[:2]
        
        return None

    def infer(self, image: cv2.typing.MatLike) -> str:
        height, width = image.shape[:2]
        original_roi = image[int(height * 0.87):int(height * 0.93), int(width * 0.035):int(width * 0.965)]
        whiten_roi = self.whiten_red_and_green(original_roi)    
        text_regions = self.find_text_region(whiten_roi)

        if text_regions is None or len(text_regions) == 0:
            extracted_text = ""
        else:
            x, y, w, h = text_regions[0]
            target_image = original_roi[y:y+h, x:x+w]
            extracted_text = pytesseract.image_to_string(target_image, config=self.TESSERACT_CONFIG).strip()

            if "REVENGE" in extracted_text and len(text_regions) >= 2:
                x, y, w, h = text_regions[1]
                target_image = original_roi[y:y+h, x:x+w]
                extracted_text = pytesseract.image_to_string(target_image, config=self.TESSERACT_CONFIG).strip()

        return extracted_text