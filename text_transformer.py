import argparse
import json

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from helpers.file_utils import FileUtils
from helpers.text_utils import TextUtils

class TTransform:
    def __init__(self, dataPath, outputPath, cachePath):
        self.textUtils = TextUtils(cachePath=cachePath) 
        self.dataPath = dataPath
        self.outputPath = outputPath

    def replacePOS(self, line, posList=None):
        replaced = False
        if not posList:
            posList = set(['NOUN', 'VERB', 'ADJ', 'ADV'])

        res = []

        for token in self.textUtils.getPOS(line):
            word = token.text
            if token.pos_ in posList:
                antonym = self.textUtils.getAntonym(word)
                # print(word, token.pos_, antonym)
                if antonym:
                    replaced = True 
                    res.append(antonym)
                else:
                    res.append(word)
            else:
                res.append(word)

        return ' '.join(res) if replaced else None 

    
    def replacePOSBoxesAll(self, boxes):
        manipulations = {}
        for (topLeft, bottomRight), originalText in boxes:
            if len(originalText.split(' ')) < 3:
                continue 
            replacedText = self.replacePOS(originalText)
            if replacedText is not None:
                manipulations[f'{topLeft[0]}, {topLeft[1]}, {bottomRight[0]}, {bottomRight[1]}'] = {
                    'truth': originalText, 
                    'inconsistent': replacedText
                }

        return manipulations


    def replacePOSAll(self):
        ocrInfo = FileUtils.readJson(f'{self.dataPath}/ocr_info.json')
        obj = FileUtils.readJson(f'{self.outputPath}/text_manipulations.json')
        c = 0

        for imgId, boxes in ocrInfo.items():
            manipulations = self.replacePOSBoxesAll(boxes)
            if manipulations:
                obj[imgId] = manipulations
                c += 1

            print('.', end=' ')

            if c > 50:
                with open(f'{self.outputPath}/text_manipulations.json', 'w+') as fileDesc:
                    json.dump(obj, fileDesc)

        with open(f'{self.outputPath}/text_manipulations.json', 'w+') as fileDesc:
            json.dump(obj, fileDesc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='Path to data')
    parser.add_argument('-o', help='Path to output directory')
    parser.add_argument('-c', help='Path to cache directory')
    args = parser.parse_args()

    dataPath, outputPath, cachePath = args.d, args.o, args.c

    if dataPath and dataPath[-1] == '/':
        dataPath = dataPath[:-1]

    if outputPath and outputPath[-1] == '/':
        outputPath = outputPath[:-1]

    if cachePath and cachePath[-1] == '/':
        cachePath = cachePath[:-1]

    transformer = TTransform(dataPath, outputPath, cachePath)
    transformer.replacePOSAll()
    # res = transformer.replacePOS('The stock prices are increasing')
    # print(res)








        

        

