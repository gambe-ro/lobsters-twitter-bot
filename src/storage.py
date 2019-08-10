import pickle
from os import path
class Storage():
    def save(self, story):
        pickle.dump(story,open(self.file_path,"wb"))

    def load(self):
        if not path.exists(self.file_path):
            return None

        return pickle.load(open(self.file_path,"rb"))