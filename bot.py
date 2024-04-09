# Импортируем необходимые классы.
import logging

from telegram.constants import MessageEntityType
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler

from Models import Form, Poll
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    InlineKeyboardButton, PollOption,MessageEntity

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

MULTIPLE_CHOICE = 3
OPEN_ANSWER = 4


async def echo(update, context):
    print(repr(update.message))


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    keyboard = ReplyKeyboardMarkup([['/create_poll', '/vote'], ['/statistics', '/help']], one_time_keyboard=True,
                                   resize_keyboard=True)
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я помогаю проводить опросы и собирать по ним статистику. Поработаем?) ",
        reply_markup=keyboard
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.")


async def okd(update, context):
    keyboard = ReplyKeyboardMarkup([[InlineKeyboardButton("First Option!", ), InlineKeyboardButton("Second option🏆")]])
    await update.message.reply_text(
        "Ok",
        reply_markup=keyboard
    )


async def close_keyboard(update, context):
    await update.message.reply_text(
        "Заркываю клаву",
        reply_markup=ReplyKeyboardRemove()
    )


async def create_poll(update, context):
    await update.message.reply_text(
        "Давайте создадим новый опрос, введите его тему: ",
        reply_markup=ReplyKeyboardRemove()
    )

    form = Form()
    context.user_data['poll'] = form
    return 1


async def title_response(update, context):
    poll = context.user_data['poll']
    poll.set_title(update.message.text)
    await update.message.reply_text(
        "Отлично,теперь приступим к добавлению вопросов!\nДобавляй вопросы с помощью кнопок внизу, когда закончишь, думаю, очевидно что нажимать 😄",
        reply_markup=ReplyKeyboardMarkup(
            [['Вопрос с вариантами ответа'], ['Вопрос с открытым ответом'], ['На этом всё']], one_time_keyboard=True,
            resize_keyboard=True)
    )
    return 2


async def question_response(update, context):
    reply = update.message.text
    if reply == 'Вопрос с вариантами ответа':
        await update.message.reply_text(
            "Пришли мне тг-опрос: ",
            reply_markup=ReplyKeyboardRemove()
        )
        return MULTIPLE_CHOICE

    elif reply == 'Вопрос с открытым ответом':
        await update.message.reply_text(
            "Введи текст вопроса..",
            reply_markup=ReplyKeyboardRemove()
        )
        return OPEN_ANSWER

    elif reply == 'На этом всё':
        poll = context.user_data['poll']
        key = poll.save()
        if key == "ERROR":
            await update.message.reply_text("Что-то пошло не так :(")
        else:
            await update.message.reply_text(
                f"Спасибо за составление опроса!\n"
                f"Идентификатор опроса: {key} \n"
                f"Делись им с друзьями, чтобы они могли пройти твой опрос",
                entities=(MessageEntity(type=MessageEntityType.CODE,offset=53,length=11),)
            )
        context.user_data['poll'] = None
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            "Такб не по тексту!\nДобавляй вопросы с помощью кнопок внизу, когда закончишь, думаю, очевидно что нажимать 😄",
            reply_markup=ReplyKeyboardMarkup(
                [['Вопрос с вариантами ответа'], ['Вопрос с открытым ответом'], ['На этом всё']],
                one_time_keyboard=True, resize_keyboard=True)
        )
        return 2


async def multiple_choice_init(update, context):
    poll = update.message.poll
    # print(poll.question, repr(poll.options), poll.type, poll.allows_multiple_answers)
    questions = list(map(lambda x: x.text, poll.options))
    # message = await context.bot.send_poll(
    #     chat_id=update.effective_chat.id,
    #     question=poll.question,
    #     type=poll.type,
    #     allows_multiple_answers=poll.allows_multiple_answers,
    #     is_anonymous= False,
    #     options=questions)

    poll_dict = {
        'chat_id': update.effective_chat.id,
        'question': poll.question,
        'type': poll.type,
        'allows_multiple_answers': poll.allows_multiple_answers,
        'is_anonymous': poll.is_anonymous,
        'options': questions
    }

    form = context.user_data['poll']

    form.append((MULTIPLE_CHOICE, poll_dict))

    await update.message.reply_text(
        "Вопрос добавлен",
        reply_markup=ReplyKeyboardMarkup(
            [['Вопрос с вариантами ответа'], ['Вопрос с открытым ответом'], ['На этом всё']],
            one_time_keyboard=True, resize_keyboard=True)
    )

    return 2


async def open_answer_init(update, context):
    text = update.message.text
    form = context.user_data['poll']
    form.append((OPEN_ANSWER, text))

    await update.message.reply_text(
        "Вопрос добавлен",
        reply_markup=ReplyKeyboardMarkup(
            [['Вопрос с вариантами ответа'], ['Вопрос с открытым ответом'], ['На этом всё']],
            one_time_keyboard=True, resize_keyboard=True)
    )

    return 2


async def vote(update, context):
    await update.message.reply_text(
        "Пришли мне идентификатор опроса"
    )
    return 1

async def open_survey(update,context):
    title = update.message.text
    poll = Form()
    reply = poll.load(title)
    if reply == "Load Error":
        await update.message.reply_text("Не удалось загрузить опрос, проверьте корректность кода и введите его ещё раз:")
        return 1
    context.user_data['poll'] = poll
    print(poll)


async def get_statistics(update, context):
    pass


# async def poll_handler(update, context):
#     poll = update.message.poll
#     #print(poll.question, repr(poll.options), poll.type, poll.allows_multiple_answers)
#     questions = list(map(lambda x : x.text,poll.options))
#     # message = await context.bot.send_poll(
#     #     chat_id=update.effective_chat.id,
#     #     question=poll.question,
#     #     type=poll.type,
#     #     allows_multiple_answers=poll.allows_multiple_answers,
#     #     is_anonymous= False,
#     #     options=questions)
#
#     poll_dict = {
#         'chat_id':update.effective_chat.id,
#         'question':poll.question,
#         'type':poll.type,
#         'allows_multiple_answers':poll.allows_multiple_answers,
#         'is_anonymous': False,
#         'options':questions
#     }
#
#     form = context.user_data['poll']
#
#     form.append((MULTIPLE_CHOICE,poll_dict))
#
#     return 2


def main():
    # Создаём объект Application.

    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    # добавили обработчик команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("okd", okd))
    application.add_handler(CommandHandler("close_keyboard", close_keyboard))
    #application.add_handler(CommandHandler("vote", vote))
    # Регистрируем обработчик в приложении.

    form_creation = ConversationHandler(
        entry_points=[CommandHandler('create_poll', create_poll)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, title_response)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_response)],
            MULTIPLE_CHOICE: [MessageHandler(filters.POLL & ~filters.COMMAND, multiple_choice_init)],
            OPEN_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, open_answer_init)]
        },

        fallbacks=[CommandHandler("close_keyboard", close_keyboard)]

    )
    application.add_handler(form_creation)


    form_voting = ConversationHandler(
        entry_points=[CommandHandler('vote', vote)],

        states={
            1 : [MessageHandler(filters.TEXT & ~filters.COMMAND,open_survey)]
        },

        fallbacks=[CommandHandler("close_keyboard", close_keyboard)]
    )
    application.add_handler(form_voting)

    application.add_handler(text_handler)

    #application.add_handler(MessageHandler(filters.POLL, poll_handler))

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
