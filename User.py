import pickle
from pathlib import Path
import os

class User:
    def __init__(self, id, name, content):
        self.stage = -1
        self.user_id = id
        self.answered_terms = []
        self.name_answered = False
        self.need_name = False
        self.name = name
        self.check_input_started = False
        self.check_input_amount = 0
        self.content = content
        self.orig_content = content
        self.misinput=0
        self.dumpToFile()
    
    def reset(self):
        self.stage = -1
        self.answered_terms = []
        self.name_answered = False
        self.need_name = False
        self.check_input_started = False
        self.check_input_amount = 0
        self.content = self.orig_content
        self.misinput=0
        self.dumpToFile()
    
    def atNegativeStage(self)->bool:
        return self.stage==-1

    def addStage(self, steps):
        self.stage += steps
        self.dumpToFile()

    def setStage(self, stage):
        self.stage = stage
        self.dumpToFile()

    def nextStage(self):
       self.addStage(1) 
       if self.stage >= len(self.content):
           self.reset()

    def currentStage(self)->dict:
        return self.content[self.stage]
    
    def insertMany(self, elements:list):
        for el in elements[::-1]:
            self.content.insert(self.stage, el)
        self.stage -= 1
        self.dumpToFile()

    def dumpToFile(self):
        Path("dumps/").mkdir(parents=True, exist_ok=True)
        with open(f"dumps/{str(self.user_id)}.pkl", 'wb') as file:
            pickle.dump(self, file)

    def getDumps()->dict:
        dumps = {}
        if Path("dumps/").exists():
            for f in os.listdir("dumps/"):
                with open(f'dumps/{f}', 'rb') as file:
                    u = pickle.load(file)
                    dumps[u.user_id]=u
        return dumps