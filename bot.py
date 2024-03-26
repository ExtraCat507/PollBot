# Импортируем необходимые классы.
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def echo(update, context):
    await update.message.reply_text(update.message.text)

async def start(update,context):
    """Отправляет сообщение когда получена команда /start"""
    keyboard = ReplyKeyboardMarkup([['/create_poll', '/vote'],['/statistics','/help']], one_time_keyboard=True)
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я помогаю проводить опросы и собирать по ним статистику. Поработаем?) ",
        reply_markup=keyboard
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.")


async def open_keyboard(update, context):
    keyboard = ReplyKeyboardMarkup([['/help','/help']],one_time_keyboard=False)
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
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    #добавили обработчик команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("open_keyboard", open_keyboard))
    application.add_handler(CommandHandler("close_keyboard", close_keyboard))
    application.add_handler(CommandHandler("create_poll", create_poll))
    application.add_handler(CommandHandler("vote", vote))
    # Регистрируем обработчик в приложении.
    application.add_handler(text_handler)



    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()