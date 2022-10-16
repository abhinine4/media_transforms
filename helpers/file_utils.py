import os
import json

class FileUtils:
    @staticmethod
    def getAllFiles(path):
        for (dirPath, _, fileNames) in os.walk(path):
            for fileName in fileNames:
                yield dirPath, fileName

    @classmethod
    def readJson(cls, path):
        try:
            with open(path, 'r') as fileDesc:
                data = fileDesc.read()
                dataDict = json.loads(data)
        except Exception as e:
            dataDict = {}
        
        return dataDict



