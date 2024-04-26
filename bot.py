# Импортируем необходимые классы.
import logging

from telegram.constants import MessageEntityType
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler,CallbackQueryHandler

from Models import Form
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    InlineKeyboardButton, PollOption,MessageEntity,Update

from data import db_session
from data.models.form import FormSQL
from data.models.users import UserSQL

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

MULTIPLE_CHOICE = 3
OPEN_ANSWER = 4

counter = 0

async def echo(update, context):
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data="1"),
            InlineKeyboardButton("Option 2", callback_data="2"),
        ],
        [InlineKeyboardButton("Option 3", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)



async def button(update: Update, context) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")












async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    keyboard = ReplyKeyboardMarkup([['/create_poll', '/vote'], ['/statistics', '/help']], one_time_keyboard=True,
                                   resize_keyboard=True)
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я помогаю проводить опросы и собирать по ним статистику. Поработаем?) ",
        #reply_markup=keyboard
    )
    db_sess = db_session.create_session()
    userObject = db_sess.query(UserSQL).filter(UserSQL.id == user.id).first()
    if userObject is None:
        userObject = UserSQL()
        userObject.id = user.id
        userObject.reference = user.mention_html()
        userObject.first_name = user.first_name
        userObject.last_name = user.last_name
        userObject.polls_list = ""
        db_sess.add(userObject)
        db_sess.commit()

    context.user_data['user'] = userObject
    global counter
    if not counter:
        counter=1
        return 1
    else:
        return ConversationHandler.END

async def stop(update,context):
    await update.message.reply_text(
        "Текущая беседа завершена",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text(
        "Привет, давай покажу как у меня тут всё работает.\n"
        "Я - бот для создания и обработки опросов и форм. Пользоваться мной очень просто!\n"
        "\n"
        "/create_poll - Создай свой опрос по шагам, затем делись его ID-кодом, чтобы другие смогли его пройти\n"
        "\n"
        "/vote - Отправь мне ID формы и проголосуй\n"
        "\n"
        "/get_statistics - Посмотри ответы пользователей на созданные тобой опросы\n"
        "\n"
        "/stop - Во время диалога с ботом жми сюда как на большую красную кнопку и кричи хелпсос\n(если хочешь завершить его конечно)\n"
        "\n"
        "/help - Ещё раз прослушать это всё",
        entities=[MessageEntity(type=MessageEntityType.BOT_COMMAND,offset=129,length=12),
                  MessageEntity(type=MessageEntityType.BOT_COMMAND,offset=229,length=5),
                  MessageEntity(type=MessageEntityType.BOT_COMMAND,offset=270,length=15),
                  MessageEntity(type=MessageEntityType.BOT_COMMAND, offset=343, length=5),
                  MessageEntity(type=MessageEntityType.BOT_COMMAND, offset=465, length=5)
                  ]
    )
    #return ConversationHandler.END


async def getting_started(update,context):
    await help_command(update,context)
    return ConversationHandler.END


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
        user = context.user_data['user']
        key = poll.save(user.id)
        if key == "ERROR":
            await update.message.reply_text("Что-то пошло не так :(")
        else:
            await update.message.reply_text(
                f"Спасибо за составление опроса!\n"
                f"Идентификатор опроса: {key} \n"
                f"Делись им с друзьями, чтобы они могли пройти твой опрос",
                entities=(MessageEntity(type=MessageEntityType.CODE,offset=53,length=11),),
                reply_markup = ReplyKeyboardRemove()
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

async def open_survey(update,context):      #Повторное открытие опроса не сохраняет прошлые ответы, надо переработать poll.load()
    title = update.message.text
    poll = Form()
    poll = poll.load(title)
    if poll == "Load Error":
        await update.message.reply_text("Не удалось загрузить опрос, проверьте корректность кода и введите его ещё раз:")
        return 1

    context.user_data['poll'] = poll
    context.user_data['pollID'] = title
    context.user_data['answers'] = poll.answers
    context.user_data['chat_id'] = update.effective_message.chat_id
    await print_form(context)

    return "collect_answers"


async def print_form(context):
    if context.user_data['poll'] is None:
        print("No poll")
        return

    poll = context.user_data['poll']
    pollID = context.user_data['pollID']
    poll = poll.load(pollID)
    survey = poll.questions
    questions = []
    textentities = []

    userReference = context.user_data['user'].reference
    PollTitle = poll.title
    sumLen = 10 + len(str(userReference)) + 34 + len(str(PollTitle))
    for k in sorted(survey):
        ans = survey[k][1]
        if survey[k][0] == OPEN_ANSWER:
            questions.append([f"/ans{k} (🗒) " + ans + "\n"])
            textentities.append(MessageEntity(type=MessageEntityType.BOT_COMMAND,offset=sumLen,length=len(str(k))+4))
            sumLen+=len(str(k))+4 + 1 + len(ans) + 4
        elif survey[k][0] == MULTIPLE_CHOICE:
            questions.append([f"/ans{k} (🔡) " + ans['question']])
            textentities.append(
                MessageEntity(type=MessageEntityType.BOT_COMMAND, offset=sumLen, length=len(str(k)) + 4))
            sumLen += len(str(k)) + 4 + 1 + len(ans) + 4
            options = ans['options']
            for opt in options:
                questions.append([f"- {opt}"])
                sumLen += 2 + len(opt)
            questions.append([""])


    # await update.message.reply_html(
    #     f"Опрос от {userID}. Тема опроса: <b>{PollTitle}</b>\n"
    #     f"Вот список вопросов:\n"+
    #     '\n'.join(map(lambda x : x[0],questions)),
    #     entities=textentities
    # )
    await context.bot.send_message(
        text=f"Опрос от {userReference}. Тема опроса: <b>{PollTitle}</b>\n"
             f"Вот список вопросов:\n"+
             '\n'.join(map(lambda x : x[0],questions))+"\n"+
            f"Когда будете готовы отправить форму введите /done",
        entities=textentities + [MessageEntity(type=MessageEntityType.CODE,offset=sumLen+44,length=5)],
        parse_mode='HTML',
        chat_id=context.user_data['chat_id']
    )


async def ans_handler(update,context):
    text = update.message.text
    if text[:5] == "/stop":
        await stop(update,context)
        return ConversationHandler.END
    if text[:5] == "/done":
        await done(update,context)
        return ConversationHandler.END

    if text[:4] != "/ans":
        await update.message.reply_text("Не угадал, надо нажать на /ans{номер вопроса} чтобы ответить на вопрос")
        return "collect_answers"
    try:
        number = str(int(text[4:]))
    except Exception as e:
        await update.message.reply_text("Не угадал, надо нажать на /ans{номер вопроса} чтобы ответить на вопрос")
        return "collect_answers"

    poll = context.user_data['poll']
    question = poll.questions.get(number,None)
    answers = context.user_data['answers']
    if question is None:
        await update.message.reply_text("Не угадал, надо нажать на /ans{номер вопроса} чтобы ответить на вопрос")
        return "collect_answers"

    if question[0] == OPEN_ANSWER:
        await update.message.reply_text(
            f"Вопрос №{number},\n"
            f"Текст вопроса: {question[1]}\n"
            f"Ваш предыдущий ответ: {answers.get(number,'Пусто')}\n"
            f"Введите ваш новый ответ: ",
            entities=[MessageEntity(type=MessageEntityType.CODE,offset=9+len(number)+15+len(question[1]) + 22 + 2,length=len(answers.get(number,'Пусто'))),
                      MessageEntity(type=MessageEntityType.BOLD,offset=9+len(number)+15,length=len(question[1]))]
        )
        context.user_data['last_question'] = number
        return "open_answer_save"

    if question[0] == MULTIPLE_CHOICE:
        options = question[1]['options']
        keyboard = []
        for opt in options:
            key = [InlineKeyboardButton(text=opt,callback_data=opt)]
            keyboard.append(key)

        await update.message.reply_text(
            f"Вопрос №{number},\n"
            f"Текст вопроса: {question[1]['question']}\n"
            f"Варианты ответа:\n"+
            "\n".join(["-" + el for el in options])+"\n"+
            f"Ваш предыдущий ответ: {answers.get(number, 'Пусто')}\n"
            f"Выберите ваш новый ответ: ",
            entities=[
                MessageEntity(type=MessageEntityType.BOLD, offset=9 + len(number) + 16, length=len(question[1]['question'])),
                MessageEntity(type=MessageEntityType.CODE,
                              offset=2 + 9 + len(number) + 16 + len(question[1]['question']) + 16 + sum(
                                  [len(a) + 2 for a in options]) + 22,
                              length=len(answers.get(number, 'Пусто')))
            ],
            reply_markup= InlineKeyboardMarkup(keyboard)
        )
        context.user_data['last_question'] = number
        return "collect_answers"

async def open_answer_save(update,context):
    text = update.message.text
    number = context.user_data['last_question']
    context.user_data['answers'][number] = text
    await update.message.reply_text(
        "Ответ сохранён"
    )
    await print_form(context)
    return "collect_answers"



async def multiple_options_save(update,context):
    query = update.callback_query
    await query.answer()
    data = query.data
    number = context.user_data['last_question']
    await query.edit_message_text(
        text = query.message.text[:len(query.message.text) - 26 - 22 - len(context.user_data['answers'].get(number,"Пусто"))],
        entities=query.message.entities[0:1],
        reply_markup=InlineKeyboardMarkup([]))
    await query.message.reply_text(
        f"В вопросе №{number} выбран ответ: {data}",
        entities=[MessageEntity(type=MessageEntityType.BOLD,offset=26+len(number),length=len(data))]
    )
    await print_form(context)
    context.user_data['answers'][number] = data


async def done(update,context):
    poll = context.user_data.get("poll",None)
    answers = context.user_data.get("answers",None)
    if poll is None:
        print("No Poll")
        return ConversationHandler.END
    if answers is None:
        print("No answers")
        return ConversationHandler.END

    poll.save_answers(answers)

    await update.message.reply_text(
        "Ваши ответы успешно сохранены"
    )

    return ConversationHandler.END

async def get_statistics(update, context):
    #user = context.user_data['user']
    polls_info = []
    entities = []
    #offset = 25
    offset=0
    db_sess = db_session.create_session()
    user = db_sess.query(UserSQL).filter(UserSQL.id == update.effective_user.id).first()
   # print(user.polls_list.split(','))
    for poll in user.polls_list.split(','):

        title = db_sess.query(FormSQL).filter(FormSQL.id == poll).first().title
        polls_info.append(poll + " " + "Тема: " + title)
        entities.append(MessageEntity(type = MessageEntityType.CODE,offset=offset,length=9))
        offset+=7+len(title)+10

    await update.message.reply_text(
        #f"Вот список твоих опросов:\n"
        "\n".join(polls_info),
        entities=entities
    )
    await update.message.reply_text(
        "Пришли мне идентификатор опроса, статистику по которому хочешь посмотреть"
    )
    return 4

async def print_statistics(update,context):

    db_sess = db_session.create_session()
    key = update.message.text
    form = db_sess.query(FormSQL).filter(FormSQL.id == key).first()
    tt = Form()
    form = tt.load(form.id)
    if form is None:
        await update.message.reply_text(
            "Ошибочка вышла, пришли ещё раз"
        )
        return 4

    print(form)
    answers = form.return_answers()
    questions = form.return_questions()
    message = []
    for i, el in answers.items():
        if type(el) is list:  # open answer
            t = f"Вопрос № {i}: " + questions[i][1] + "\n"
            message.append(t)
            t = "Ответы пользователей\n"
            message.append(t)
            message+=list(map(lambda x: str(x) + "\n",el))

        else:  # dict - Multiple Choice
            t = f"Вопрос № {i}: " + questions[i][1]["question"] + "\n"
            message.append(t)
            t = "Ответы пользователей\n"
            for ans in el:
                message.append(str(ans) + ' : ' + str(el[ans]) + "\n")

    print(message)
    await update.message.reply_text(
        ''.join(message)
    )

    return ConversationHandler.END


def main():
    db_session.global_init("dp/bot.db")

    # Создаём объект Application.

    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    # добавили обработчик команд
    #application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("okd", okd))
    application.add_handler(CommandHandler("close_keyboard", close_keyboard))
    #application.add_handler(CommandHandler("get_statistics",get_statistics))
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

        fallbacks=[CommandHandler("stop", stop)]

    )
    application.add_handler(form_creation)


    form_voting = ConversationHandler(
        entry_points=[CommandHandler('vote', vote)],

        states={
            1 : [MessageHandler(filters.TEXT & ~filters.COMMAND,open_survey)],
            "collect_answers": [MessageHandler(filters.TEXT,ans_handler)],
            "open_answer_save":[MessageHandler(filters.TEXT & ~filters.COMMAND,open_answer_save)]
        },

        fallbacks=[CommandHandler("stop", stop),CommandHandler("done",done)]
    )
    application.add_handler(form_voting)


    start_handler = ConversationHandler(
        entry_points=[CommandHandler("start",start)],
        states = {
            1: [MessageHandler(filters.TEXT & ~ filters.COMMAND,getting_started)]
        },
        fallbacks=[CommandHandler("stop", stop),CommandHandler("help", help_command),CommandHandler("create_poll",create_poll),CommandHandler("vote",vote),CommandHandler("get_statistics",get_statistics)]
    )
    application.add_handler(start_handler)

    statistics_handler = ConversationHandler(
        entry_points=[CommandHandler("get_statistics",get_statistics)],
        states={
            4: [MessageHandler(filters.TEXT,print_statistics)]
        },
        fallbacks=[CommandHandler("stop",stop)]
    )
    application.add_handler(statistics_handler)

    application.add_handler(text_handler)

    application.add_handler(CallbackQueryHandler(multiple_options_save))


    # Запускаем приложение.
    application.run_polling(allowed_updates=Update.ALL_TYPES)


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':

    main()
