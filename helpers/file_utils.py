import os


class FileUtils:
    @staticmethod
    def getAllFiles(path):
        for (dirPath, _, fileNames) in os.walk(path):
            for fileName in fileNames:
                yield dirPath, fileName


