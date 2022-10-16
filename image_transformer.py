import argparse
import json
import cv2

from helpers.file_utils import FileUtils
from helpers.utils import OCR


class ITransformer(OCR, FileUtils):
    def __init__(self, dataPath, outputPath):
        super().__init__()
        self.dataPath = dataPath
        self.outputPath = outputPath

    def toJson(self, imgPath):
        img = cv2.imread(imgPath)
        boxes = self.getTextBoxes(img)
        return boxes

    def allToJson(self):
        mediaPath = f'{self.dataPath}/media'
        try:
            with open(f'{self.outputPath}/ocr_info.json', 'r') as fileDesc:
                data = fileDesc.read()
        except Exception as e:
            data = '{}'

        obj = json.loads(data)

        for dirPath, fileName in self.getAllFiles(mediaPath):
            imgPath = f'{dirPath}/{fileName}'
            imgId = fileName.split('.')[0]
            try:
                if imgId not in obj:
                    imgInfo = self.toJson(imgPath)
                    obj[imgId] = imgInfo
                
                l = len(obj.keys())

                if l % 100 == 0:
                    with open(f'{self.outputPath}/ocr_info.json', 'w+') as fileDesc:
                        json.dump(obj, fileDesc)

            except Exception as e:
                print(f'Failed: {fileName}; E: {e}')

        with open(f'{self.outputPath}/ocr_info.json', 'w+') as fileDesc:
            json.dump(obj, fileDesc)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='Path to data')
    parser.add_argument('-o', help='Path to output directory')
    args = parser.parse_args()

    dataPath, outputPath = args.d, args.o

    if dataPath and dataPath[-1] == '/':
        dataPath = dataPath[:-1]

    if outputPath and outputPath[-1] == '/':
        outputPath = outputPath[:-1]

    transformer = ITransformer(dataPath, outputPath)
    transformer.allToJson()
