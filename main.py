import psycopg2
import telegram
import configparser
import telegramcalendar

from datetime import datetime
from telegram import ReplyKeyboardRemove
from psycopg2._psycopg import OperationalError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# Configuring bot
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

# Connecting to Telegram API
# Updater retrieves information and dispatcher connects commands
updater = Updater(token=config['DEFAULT']['token'])
dispatcher = updater.dispatcher


# Creating database connection
def create_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            database=config['DB']['db'],
            user=config['DB']['user'],
            password=config['DB']['password'],
            host=config['DB']['host'],
            port=config['DB']['port'],
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print("The error '{e}' occurred", e)
    return conn


def insert_query(query):
    try:
        conn = create_connection()
        conn.autocommit = True
        conn.cursor().execute(query)
        print("Query executed successfully")
        return True
    except Exception as e:
        print("The error '{0}' occurred".format(e))
        return False


def find_query(query):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(query)
        print("Query executed successfully")
        return cursor.fetchall()
    except Exception as e:
        print("The error '{0}' occurred".format(e))


def start(bot, update):
    print(bot, update)
    me = bot.get_me()
    print(me)

    # Welcome message
    msg = "Olá\n"
    msg += "Eu sou {0} e tamo aqui para ajudar.\n".format(me.first_name)
    msg += "O que gostaria?\n\n"
    msg += "/find_reservations - Buscar suas reservas\n"
    msg += "/ask_reservation - Criar nova reserva\n\n"
    msg += "/support - Falar com suporte\n\n"
    print(msg)

    try:
        # Commands menu
        main_menu_keyboard = [
            [telegram.KeyboardButton('/find_reservations')],
            [telegram.KeyboardButton('/ask_reservation')],
            [telegram.KeyboardButton('/support')]
        ]
        reply_kb_markup = telegram.ReplyKeyboardMarkup(
            keyboard=main_menu_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        # Send the message with menu
        bot.send_message(
            chat_id=update.message.chat_id,
            text=msg,
            reply_markup=reply_kb_markup
        )
    except Exception as e:
        print("Error")
        print(e)


def support(bot, update):
    print(bot, update)
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Como posso te ajudar? :)"
    )


def find_reservations(bot, update):
    print(bot)
    print(update)
    print(update.message.from_user.id)
    query = "SELECT * FROM reservation WHERE user_id = {0}".format(update.message.from_user.id)
    print(query)
    reservations = find_query(query)
    print(reservations)
    if reservations is None:
        msg = 'Você não tem reservas!'
    else:
        msg = 'Reserva encontrada {0}'.format(reservations)

    bot.send_message(
        chat_id=update.message.chat_id,
        text=msg
    )


def ask_reservation(bot, update):
    print(bot, update)
    update.message.reply_text(
        "Por favor, informe a data: ",
        reply_markup=telegramcalendar.create_calendar()
    )


def calendar_handler(bot, update):
    print("\n", update)
    selected, date = telegramcalendar.process_calendar_selection(bot, update)
    print("Selected", selected)
    print("Date", date)
    if selected:
        insert = """INSERT INTO reservation VALUES ({0}, '{1}', {2}, {3}, '{4}')""".format(
            1, date, update.callback_query.from_user.id, "nextval('reservation_seq')", datetime.today()
        )
        print("Insert query", insert)
        result = insert_query(insert)
        if result:
            bot.send_message(
                chat_id=update.callback_query.from_user.id,
                text="Reserva para o dia {0} efetuada com sucesso!".format(date.strftime("%d/%m/%Y")),
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            bot.send_message(
                chat_id=update.callback_query.from_user.id,
                text="Não foi possível fazer reserva para o dia {0}, tente novamente em outra data".format(
                    date.strftime("%d/%m/%Y")
                ),
            )


def unknown(bot, update):
    print(bot, update)
    msg = "Desculpe, não entendi."
    bot.send_message(
        chat_id=update.message.chat_id,
        text=msg
    )


# creating handlers
start_handler = CommandHandler('start', start)
support_handler = CommandHandler('support', support)
find_reservations_handler = CommandHandler('find_reservations', find_reservations)
ask_reservation_handler = CommandHandler('ask_reservation', ask_reservation)

# adding handlers
dispatcher.add_handler(start_handler)
dispatcher.add_handler(support_handler)
dispatcher.add_handler(find_reservations_handler)
dispatcher.add_handler(ask_reservation_handler)
dispatcher.add_handler(CallbackQueryHandler(calendar_handler))

if __name__ == "__main__":
    updater.start_polling()
