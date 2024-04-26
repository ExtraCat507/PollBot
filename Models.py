import json
import random

import sqlalchemy as sa
from data import db_session
from data.models.form import FormSQL
from data.models.users import UserSQL


MULTIPLE_CHOICE = 3
OPEN_ANSWER = 4
ALPLHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'W', 'X', 'Y', 'Z']
class Form:
    def __init__(self):

        self.title = ''
        self.questions = {}
        self.num_of_questions = 0
        self.answers = {}
        self.id = -1

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
        #self.questions["userID"] = str(userID)
        #self.questions["title"] = str(self.title)

        while True:
            key = f"{random.choice(ALPLHABET)}{random.randint(0, 9)}{random.randint(0, 9)}" \
                  f"{random.choice(ALPLHABET)}{random.randint(0, 9)}{random.randint(0, 9)}" \
                  f"{random.choice(ALPLHABET)}{random.randint(0, 9)}{random.randint(0, 9)}"
            db_sess = db_session.create_session()
            form = db_sess.query(FormSQL).filter(FormSQL.id == key).first()
            if form is None:
                break

        with open(f'data/forms/{key}.json', mode='w') as js:
            json.dump(self.questions, js)

        with open(f'data/answers/{key}_answers.json', mode='w') as js:
            answ = {}
            for i,el in self.questions.items():
                type = el[0]
                if type == OPEN_ANSWER:
                    answ[i] = []
                else:
                    answ[i] = {}
                    for q in el[1]['options']:
                        answ[i][q] = 0
            self.answers = answ
            self.id = key
            json.dump(answ,js)



        form = FormSQL()

        form.id = key
        form.title = self.title
        form.user_id = userID
        form.file = f'data/forms/{key}.json'
        form.answers = f"data/answers/{key}_answers.json"

        user = db_sess.query(UserSQL).filter(UserSQL.id == userID).first()
        if not user.polls_list:
            user.polls_list = key
        else:
            user.polls_list = user.polls_list + "," + key
        print(user)
        print(user.polls_list)

        db_sess.add(form)
        db_sess.commit()


        return key


    def load(self,id):

        db_sess = db_session.create_session()
        poll = db_sess.query(FormSQL).filter(FormSQL.id == id).first()
        if poll is None:
            return "Load Error"

        self.title = poll.title
        self.id = id
        #self.answers


        with open(f'data/forms/{id}.json',mode='r') as js:
            survey = json.load(js)

        self.questions = survey

        return self

    def save_answers(self,user_answers):
        #self.answers = answers

        with open(f"data/answers/{self.id}_answers.json",mode='r') as js:
            answers = json.load(js)

        for i,el in answers.items():
            if type(el) is list: #open answer
                answers[i].append(user_answers[i])
            else: #dict - Multiple Choice
                answers[i][user_answers[i]] +=1

        with open(f'data/answers/{self.id}_answers.json', mode='w') as js:
            json.dump(answers,js)


    def return_answers(self):
        with open(f"data/answers/{self.id}_answers.json",mode='r') as js:
            answers = json.load(js)
        return answers

    def return_questions(self):
        with open(f"data/forms/{self.id}.json",mode='r') as js:
            answers = json.load(js)
        return answers



if __name__ == '__main__':
    a = Form()
    a.append((OPEN_ANSWER,"owkoekrf"))
    a.save()