from telegram.ext import Application, MessageHandler, filters, CommandHandler,ConversationHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup,InlineKeyboardMarkup, ReplyKeyboardRemove,KeyboardButton,InlineKeyboardButton
MULTIPLE_CHOICE = 3
OPEN_ANSWER = 4
class Poll:
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
            data = "OA#~#" + str(data)
        if type == MULTIPLE_CHOICE:
            data = "MC#~#" + "#~#".join(map(str,data))
        self.questions[self.num_of_questions] = data

    def __repr__(self):
        return f"Poll {self.title} : " + repr(self.questions)
