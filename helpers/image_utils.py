import cv2


class ImageUtils:
    @staticmethod
    def binarizeImage(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binarized = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 85, 11)

        return binarized