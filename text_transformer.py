import argparse
import json
import random
import pandas as pd
import numpy as np
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
            tokens[idx].text: antonym,
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
                print(ocr)
                ocrObj[imgId] = ocr
                with open(f'{self.outputPath}/pos_ocr.json', 'w+') as fileDesc:
                    json.dump(ocrObj, fileDesc)
                    
            
            if text:
                textObj[imgId] = text
                with open(f'{self.outputPath}/pos_text.json', 'w+') as fileDesc:
                    json.dump(textObj, fileDesc)
            
            c += 1
            print(f'[{c}/{len(ocrInfo.items())}]')

    ### Abhishek: NER functions
    def replaceNERLine(self, text):
        ent_list = ['DATE','GPE','MONEY','TIME','QUANTITY','PERCENT','LOC','NORP','ORG','ORDINAL','LAW','FAC','PRODUCT', 'PERSON']

        tokens = []
        interested = []
        replacements = []
    
        for index,token in enumerate(self.textUtils.getNER(text)):
            tokens.append(token)
            if token.ent_type_ in ent_list:
                if token.text not in self.cache:
                    ner_entity = self.textUtils.getRandomEntity(token.text, token.ent_type_)
                    if ner_entity:
                        self.cache[token.text] = ner_entity

                if self.cache.get(token.text, None):
                    interested.append((index, self.cache[token.text]))

        if len(interested) == 0:
            return None, None

        k = random.randint(0, len(interested)-1)
        index, entity = interested[k]

        org = text
        or_term = tokens[index].text
        or_start = mod_start = tokens[index].idx
        or_end = tokens[index].idx + len(tokens[index].text)-1

        tokens[index] = entity

        mod = ' '.join([t.text if not isinstance(t, str) else t for t in tokens ])
        mod_term = tokens[index]
        mod_end = mod_start + len(mod_term)-1 

        replacement = {or_term:mod_term}
        # replacements.append(replacement)
        return mod, replacement

    def replaceNER_OCR(self, boxes):
        ocrManipulations = []
        for (topLeft, bottomRight), originalText in boxes:
            if len(originalText.split(' ')) < 3:
                continue 
            replacedText, replacement = self.replaceNERLine(originalText)
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
    
    def replaceNER_Text(self, textInfo, textTypes):
        textManipulations = []
        
        for textType in textTypes:
            text = textInfo.get(textType, '')
            replacedText, replacement = self.replaceNERLine(text)
            if replacedText is not None:
                textManipulations = {
                    textType: {
                        'original': text,
                        'modified': replacedText,
                        'replacement': replacement,
                    }
                }
            print(textManipulations)
            
        return textManipulations, replacedText

    def replaceNER(self, boxes, textInfo):
        self.cache = {}
        ocrManipulations_log = self.replaceNER_OCR(boxes)
        textManipulations_log, replacedText = self.replaceNER_Text(textInfo, textTypes=['title'])
        
        return textManipulations_log, replacedText, ocrManipulations_log

    ### TODO: change paths / function similar to replacePOSALL
    def replaceNERAll(self):
        info = FileUtils.readJson(f'{self.datapath}/info.json')
        ocrInfo = FileUtils.readJson(f'{self.datapath}/ocr_info.json')
        text_obj = FileUtils.readJson(f'{self.datapath}/info.json')
        text_log_obj = FileUtils.readJson(f'{self.outputpath}/ner_info_log.json')
        
        for imgId, boxes in ocrInfo.items():
            text_log, replaced_text, ocr_log = self.replaceNER(boxes, info.get(imgId, {}))
            if text_log:
                text_obj[imgId]["title"] = replaced_text
                text_log_obj[imgId] = text_log
                
            if ocr_log:
                ocrInfo[imgId] = ocr_log


        with open('../for_eval/ner_info_log.json', 'w+') as fileDesc:
            json.dump(text_log_obj, fileDesc)

        with open('../for_eval/ner_ocr.json', 'w+') as fileDesc:
            json.dump(ocrInfo, fileDesc)

        with open('../for_eval/ner_info.json', 'w+') as fileDesc:
            json.dump(text_obj, fileDesc)


    def random_replacement(self):
        ### TODO: chenage datapath here
        info_dir = self.datapath+'info.json'
        f = open(info_dir)
        random_mani = json.load(f)

        or_data = pd.read_json(info_dir).T
        ran_data = pd.DataFrame()
        ran_data = or_data.copy(deep=True)

        random_index = np.random.permutation(ran_data.index)
        random_index_title = ran_data["title"].loc[random_index]
        random_data = (random_index, random_index_title)
        random ={}
        for i in range(len(ran_data)):
            image = ran_data["graphic"].iloc[i][11:-5]

            original_title = ran_data["title"].iloc[i]
            random_title = random_index_title.iloc[i]
            original_index = image
            random_idx = str(random_index[i])
            # ran_data["title"].iloc[i] = random_title
            random_mani[image]["title"] = random_title
            replacement = {'original': original_title,
                            'modified' : random_title,
                            'replacement': {original_index : random_idx}}
            random[image] = replacement

        with open('../for_eval/random_info.json', 'w+') as fileDesc:
            json.dump(random_mani, fileDesc)

        with open('../for_eval/random_info_log.json', 'w+') as fileDesc:
            json.dump(random, fileDesc)



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
    transformer.replaceNERAll()
    transformer.random_replacement()








        

        

