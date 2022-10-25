import argparse
import json
import random

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from helpers.file_utils import FileUtils
from helpers.text_utils import TextUtils

class TTransform:
    def __init__(self, dataPath, outputPath, cachePath):
        self.textUtils = TextUtils(cachePath=cachePath) 
        self.dataPath = dataPath
        self.outputPath = outputPath
        self.cache = {}

    def replaceLine(self, line, posList=None):
        if not posList:
            posList = set(['ADJ', 'ADV', 'NOUN', 'VERB'])
            
        tokens = []
        interested = []
        replacements = []
        
        for idx, token in enumerate(self.textUtils.getPOS(line)):
            tokens.append(token)
            if token.pos_ in posList:
                if token.text not in self.cache:
                    antonym = self.textUtils.getAntonym(token.text)
                    if antonym: 
                        self.cache[token.text] = antonym
                if self.cache.get(token.text, None):
                    interested.append((idx, self.cache[token.text]))
                
        if len(interested) == 0:
            return None, None
        
        k = random.randint(0, len(interested)-1)
        idx, antonym = interested[k]
        
        replacement = {
            'word': tokens[idx].text,
            'replacement': antonym,
            'startIdx': tokens[idx].idx,
            'endIdx': tokens[idx].idx + len(tokens[idx].text)-1,
        }
        replacements.append(replacement)
        tokens[idx] = antonym
        
        return ' '.join([t.text if not isinstance(t, str) else t for t in tokens ]), replacements
    
    def replaceOCR(self, boxes):
        ocrManipulations = []
        for (topLeft, bottomRight), originalText in boxes:
            if len(originalText.split(' ')) < 3:
                continue 
            replacedText, replacements = self.replaceLine(originalText)
            if replacedText is not None:
                ocrManipulations.append({
                    'boundingBox': {
                        'topLeft': topLeft,
                        'bottomRight': bottomRight,
                    },
                    'truth': originalText, 
                    'modified': replacedText,
                    'replacements': replacements,
                })
                
        return ocrManipulations
    
    def replaceText(self, textInfo, textTypes):
        textManipulations = []
        
        for textType in textTypes:
            text = textInfo.get(textType, '')
            replacedText, replacements = self.replaceLine(text)
            if replacedText is not None:
                textManipulations.append({
                    textType: {
                        'original': text,
                        'modified': replacedText,
                        'replacements': replacements,
                    }
                })
            
        return textManipulations

    
    def replacePOS(self, boxes, textInfo):
        self.cache = {}
        ocrManipulations = self.replaceOCR(boxes)
        textManipulations = self.replaceText(textInfo, textTypes=['title'])
        res = {
            'type': {
                'text': textManipulations,
                'ocr': ocrManipulations,
            }
        }
        
        return res


    def replacePOSAll(self):
        info = FileUtils.readJson(f'{self.dataPath}/info.json')
        ocrInfo = FileUtils.readJson(f'{self.dataPath}/ocr_info.json')
        obj = FileUtils.readJson(f'{self.outputPath}/text_manipulations.json')
        c = 0

        for imgId, boxes in ocrInfo.items():
            manipulations = self.replacePOS(boxes, info.get(imgId, {}))
            if manipulations:
                obj[imgId] = manipulations
                c += 1

            print(imgId, end=' ')

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








        

        

