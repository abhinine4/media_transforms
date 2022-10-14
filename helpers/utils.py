import easyocr

from helpers.image_utils import ImageUtils


class OCR(ImageUtils):
    def __init__(self, languages=None, gpu=True):
        if languages is None:
            languages = ['en']
        self.reader = easyocr.Reader(languages, gpu=gpu)

    def getTextBlobs(self, img):
        result = self.reader.readtext(img, paragraph=False)
        textBoxes = []

        for detection in result:
            topLeft = int(detection[0][0][0]), int(detection[0][0][1])
            bottomRight = int(detection[0][2][0]), int(detection[0][2][1])
            box = topLeft, bottomRight
            textBoxes.append([box, detection[1]])

        return textBoxes

    def getTextBoxes(self, img):
        binImg = self.binarizeImage(img)
        textBoxes = self.getTextBlobs(binImg)
        return textBoxes
