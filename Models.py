import json
import random
import sqlalchemy
MULTIPLE_CHOICE = 3
OPEN_ANSWER = 4
ALPLHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'W', 'X', 'Y', 'Z']
class Form:
    def __init__(self):
        self.title = ''
        self.questions = {}
        self.num_of_questions = 0

    def set_title(self,title):
        self.title = title


    def append(self, other):
        self.num_of_questions+=1
        type,data = other
        if type == OPEN_ANSWER:
            #data = "OA#~#" + str(data)
            data = [type,str(data)]
        if type == MULTIPLE_CHOICE:
            #data = "MC#~#" + "#~#".join(map(str,data))
            #data = json.dumps(other)
            data = other
        self.questions[self.num_of_questions] = data

    def __repr__(self):
        return f"Poll {self.title} : " + repr(self.questions)


    def save(self,userID):
        self.questions["userID"] = str(userID)
        self.questions["title"] = str(self.title)
        key = f"{random.choice(ALPLHABET)}{random.randint(0, 9)}{random.randint(0, 9)}" \
              f"{random.choice(ALPLHABET)}{random.randint(0, 9)}{random.randint(0, 9)}" \
              f"{random.choice(ALPLHABET)}{random.randint(0, 9)}{random.randint(0, 9)}"      ### коннект с БД

        with open(f'data/forms/{key}.json', mode='w') as js:
            json.dump(self.questions, js)

        return key


    def load(self,title):
        try:
            with open(f'data/forms/{title}.json',mode='r') as js:
                survey = json.load(js)
        except Exception as e:
            return "Load Error"
        self.questions = survey
        return survey



class Poll:
    def __init__(self):
        self.dict = {}


if __name__ == '__main__':
    a = Form()
    a.append((OPEN_ANSWER,"owkoekrf"))
    a.save()