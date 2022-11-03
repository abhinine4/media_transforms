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
        
        line = self.textUtils.cleanString(line)
        
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
            tokens[idx]: antonym,
        }
        tokens[idx] = antonym
        
        return ' '.join([t.text if not isinstance(t, str) else t for t in tokens]), replacement
    
    def replaceOCR(self, boxes):
        ocrManipulations = []
        for (topLeft, bottomRight), originalText in boxes:
            if len(originalText.split(' ')) < 3:
                continue 
            replacedText, replacement = self.replaceLine(originalText)
            if replacedText is not None:
                ocrManipulations.append({
                    'boundingBox': {
                        'topLeft': topLeft,
                        'bottomRight': bottomRight,
                    },
                    'original': originalText, 
                    'modified': replacedText,
                    'replacement': replacement,
                })
                
        return ocrManipulations
    
    def replaceText(self, textInfo, textTypes):
        textManipulations = []
        
        for textType in textTypes:
            text = textInfo.get(textType, '')
            replacedText, replacement = self.replaceLine(text)
            if replacedText is not None:
                textManipulations.append({
                    textType: {
                        'original': text,
                        'modified': replacedText,
                        'replacement': replacement,
                    }
                })
            
        return textManipulations

    
    def replacePOS(self, boxes, textInfo):
        self.cache = {}
        ocrManipulations = self.replaceOCR(boxes)
        textManipulations = self.replaceText(textInfo, textTypes=['title'])
        
        return ocrManipulations, textManipulations


    def replacePOSAll(self):
        info = FileUtils.readJson(f'{self.dataPath}/info.json')
        ocrInfo = FileUtils.readJson(f'{self.dataPath}/ocr_info.json')
        ocrObj = FileUtils.readJson(f'{self.outputPath}/pos_ocr.json')
        textObj = FileUtils.readJson(f'{self.outputPath}/pos_text.json')
        c = 0

        for imgId, boxes in ocrInfo.items():
            ocr, text = self.replacePOS(boxes, info.get(imgId, {}))
            
            if ocr:
                ocrObj[imgId] = ocr
                with open(f'{self.outputPath}/pos_ocr.json', 'w+') as fileDesc:
                    json.dump(ocrObj, fileDesc)
                    
            
            if text:
                textObj[imgId] = text
                with open(f'{self.outputPath}/pos_text.json', 'w+') as fileDesc:
                    json.dump(textObj, fileDesc)
            
            c += 1
            print(f'[{c}/{len(ocrInfo.items())}]')


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








        

        

