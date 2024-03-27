# Импортируем необходимые классы.
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler,ConversationHandler

from Models import Poll
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup,InlineKeyboardMarkup, ReplyKeyboardRemove,KeyboardButton,InlineKeyboardButton

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


MULTIPLE_CHOICE = 3
OPEN_ANSWER = 4

async def echo(update, context):
    await update.message.reply_text(update.message.text)

async def start(update,context):
    """Отправляет сообщение когда получена команда /start"""
    keyboard = ReplyKeyboardMarkup([['/create_poll', '/vote'],['/statistics','/help']], one_time_keyboard=True,resize_keyboard=True)
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я помогаю проводить опросы и собирать по ним статистику. Поработаем?) ",
        reply_markup=keyboard
    )



async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.")


async def okd(update, context):
    keyboard = ReplyKeyboardMarkup([[InlineKeyboardButton("First Option!",),InlineKeyboardButton("Second option🏆")]])
    await update.message.reply_text(
        "Ok",
        reply_markup=keyboard
    )

async def close_keyboard(update,context):
    await update.message.reply_text(
        "Заркываю клаву",
        reply_markup=ReplyKeyboardRemove()
    )


async def create_poll(update,context):
    await update.message.reply_text(
        "Давайте создадим новый опрос, введите его тему: ",
        reply_markup=ReplyKeyboardRemove()
    )

    poll = Poll()
    context.user_data['poll'] = poll
    return 1



async def title_response(update,context):
    poll = context.user_data['poll']
    poll.set_title(update.message.text)
    await update.message.reply_text(
        "Отлично,теперь приступим к добавлению вопросов!\nДобавляй вопросы с помощью кнопок внизу, когда закончишь, думаю, очевидно что нажимать 😄",
        reply_markup = ReplyKeyboardMarkup([['Вопрос с вариантами ответа'],['Вопрос с открытым ответом'],['На этом всё']],one_time_keyboard=True,resize_keyboard=True)
    )
    return 2

async def question_response(update,context):
    reply = update.message.text
    if reply == 'Вопрос с вариантами ответа':
        pass

    elif reply == 'Вопрос с открытым ответом':
        await update.message.reply_text(
            "Введи текст вопроса..",
            reply_markup=ReplyKeyboardRemove()
        )
        return OPEN_ANSWER

    elif reply == 'На этом всё':
        await update.message.reply_text(
            "Спасибо за составление опроса!"
        )
        print(context.user_data['poll'])
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            "Такб не по тексту!\nДобавляй вопросы с помощью кнопок внизу, когда закончишь, думаю, очевидно что нажимать 😄",
            reply_markup=ReplyKeyboardMarkup(
                [['Вопрос с вариантами ответа'], ['Вопрос с открытым ответом'], ['На этом всё']],
                one_time_keyboard=True, resize_keyboard=True)
        )
        return 2


async def multiple_choice_init(update,context):
    pass

async def open_answer_init(update,context):
    text = update.message.text
    poll = context.user_data['poll']
    poll.append((OPEN_ANSWER,text))

    await update.message.reply_text(
        "Вопрос добавлен",
        reply_markup=ReplyKeyboardMarkup(
            [['Вопрос с вариантами ответа'], ['Вопрос с открытым ответом'], ['На этом всё']],
            one_time_keyboard=True, resize_keyboard=True)
    )

    return 2




async def vote(update,context):
    pass

async def get_statistics(update,context):
    pass

def main():
    # Создаём объект Application.

    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    #text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    #добавили обработчик команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("okd", okd))
    application.add_handler(CommandHandler("close_keyboard", close_keyboard))
    application.add_handler(CommandHandler("vote", vote))
    # Регистрируем обработчик в приложении.

    form_creation = ConversationHandler(
        entry_points=[CommandHandler('create_poll', create_poll)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, title_response)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_response)],
            MULTIPLE_CHOICE : [MessageHandler(filters.TEXT & ~filters.COMMAND, multiple_choice_init)],
            OPEN_ANSWER : [MessageHandler(filters.TEXT & ~filters.COMMAND, open_answer_init)]
        },

        fallbacks=[CommandHandler("close_keyboard", close_keyboard)]

    )
    application.add_handler(form_creation)

   # application.add_handler(text_handler)



    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()