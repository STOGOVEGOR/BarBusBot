# use the https://uptimerobot.com/dashboard#mainDashboard for keep flask server alive
import os
from background import keep_alive
# import pip

# pip.main(['install', 'pytelegrambotapi'])
import telebot
import time
import pytz
from datetime import date, timedelta, datetime, time, timezone
# from replit import db

API_KEY = os.environ['BARBUS_BOT_API_KEY']
GOOGLE_MAP = 'https://wikiroutes.info/bar?routes=53424'
bot = telebot.TeleBot(API_KEY)
bot_enabled = 1
delay = 10

# correction by direction in minutes
# [0, 1] - 0 to Bar, 1 to Chan
BUSBASE = {
    'BusBar': {
        'Chan': [0, 'end'],
        'Mishichi': [3, 41],
        'Durmani': [5, 38],
        'Haj-Nehaj': [7, 36],
        'Sutomore': [10, 33],
        'Sv.Andrija': [12, 30],
        'Shusanj': [16, 27],
        'Stadion': [18, 25],
        'Hram': [20, 22],
        'Bulevar Revolucije': [22, 20],
        'Jovana Tomashevicha': [25, 18],
        'Novi bulevar': [27, 16],
        'Zeljeznichka stanica': [30, 12],
        'Distribucija': [33, 10],
        'Popovichi': [36, 7],
        'Rena': [38, 5],
        'Opshta bolnica': [41, 3],
        'Stari Bar': ['end', 0],
    },
}

BUSSCHEDULE = (
600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 600,
700, 800, 900, 1000
)

# ======== CALC SECTION ==========
def get_current_time() -> datetime:
    # CHANGE DELTA TO '1' FOR WINTER TIME AND '2' FOR SUMMER
    delta = timedelta(hours=1, minutes=0)
    and_now = datetime.now(timezone.utc) + delta
    return and_now


def when_next(bus_stop, bus_num, direction):
    cur_time = get_current_time()
    cur_hour = int(cur_time.strftime("%H") + '00')
    if cur_hour == 0:
        cur_hour = 2400
    cur_minute = cur_time.strftime("%M")
    day_of_week = cur_time.weekday()
    arrive_on_stop = []
    if bus_stop in BUSBASE[bus_num]:
        correction = BUSBASE[bus_num][bus_stop]
        if direction == 'Bar':
            correction = correction[0]
            if correction == 'end':
                arrive_on_stop.append('вы на конечной остановке.')
                return arrive_on_stop
        if direction == 'Chan':
            correction = correction[1]
            if correction == 'end':
                arrive_on_stop.append('вы на конечной остановке.')
                return arrive_on_stop
    else:
        return False

    # get a list of nearest bus starting time
    cur_t = 0
    for t in BUSSCHEDULE:
        if t >= cur_hour:
            x = BUSSCHEDULE.index(t)
            time_start_list = [str(BUSSCHEDULE[i]) for i in range(x, x + 5)]
            break
        cur_t += 1
        if cur_t == len(BUSSCHEDULE):
            time_start_list = [str(BUSSCHEDULE[i]) for i in range(-5, 0)]
            break
    # print(bus_num, direction, time_start_list)
    # calculate an arriwal time
    for i in time_start_list:
        hour = int(i[:-2])
        if hour == 24:
            hour = 00
        minute = "{:02d}".format(int(i[-2:]))
        i = time(hour=hour, minute=int(minute))
        arrive_on_busstop_full = datetime.combine(date.today(), i, pytz.UTC) + timedelta(minutes=correction)
        if arrive_on_busstop_full.time().strftime('%H') == '00':
            arrive_on_busstop_full = arrive_on_busstop_full + timedelta(days=1)
        if cur_hour >= 21 and arrive_on_busstop_full.time().strftime('%H') in ['05', '06', '07', '08', '09']:
            arrive_on_busstop_full = arrive_on_busstop_full + timedelta(days=1)
        if arrive_on_busstop_full >= cur_time:
            x = arrive_on_busstop_full.time().strftime('%H:%M')
            arrive_on_stop.append(x)

    return arrive_on_stop[:3]


# ========= BOT LOGIC ===========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, """\
Привет, я автобусный бот.
Я здесь чтобы рассказать, когда ожидается следующий автобус (никаких гарантий!)
Обо всех замечаниях пишите @EgoriiSt.

Поддерживаемые команды:
/stops - выбрать остановку;

Давайте начнем!\
""")
    print('user_id: ' + str(message.from_user.id))
    print('new user name: ' + str(message.from_user.username))
    lets_start(message)


@bot.message_handler(commands=['stops'])
def lets_start(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Свериться с картой:', url=GOOGLE_MAP))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Čanj️ (Чань) 🏘️', callback_data='Chan'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Mišići', callback_data='Mishichi'),
        telebot.types.InlineKeyboardButton('Đurmani', callback_data='Durmani'),
        telebot.types.InlineKeyboardButton('Haj-Nehaj', callback_data='Haj-Nehaj'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Sutomore', callback_data='Sutomore'),
        telebot.types.InlineKeyboardButton('Sv.Andrija', callback_data='Sv.Andrija'),
        telebot.types.InlineKeyboardButton('Šusanj', callback_data='Shusanj'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Stadion', callback_data='Stadion'),
        telebot.types.InlineKeyboardButton('Hram', callback_data='Hram'),
        telebot.types.InlineKeyboardButton('b-r Revolucije', callback_data='Bulevar Revolucije'))
    keyboard.row(
        telebot.types.InlineKeyboardButton(text=f'Jovana Tomaševića', callback_data='Jovana Tomashevicha'),
        telebot.types.InlineKeyboardButton('Novi bulevar', callback_data='Novi bulevar'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Željeznička stanica', callback_data='Zeljeznichka stanica'),
        telebot.types.InlineKeyboardButton(text=f'Distribucija', callback_data='Distribucija'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Popovići', callback_data='Popovichi'),
        telebot.types.InlineKeyboardButton('Rena', callback_data='Rena'),
        telebot.types.InlineKeyboardButton('Opšta bolnica', callback_data='Opshta bolnica'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Stari Bar (Старый Бар) 🏰', callback_data='Stari Bar'))
    print('query from: ' + str(message.from_user.username))
    bot.send_message(message.chat.id,
                     'Где вы сейчас?',
                     reply_markup=keyboard)


# def Group1(message):
#     keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
#     btn1 = telebot.types.InlineKeyboardButton('Bijela Hotel Park', callback_data='BijelaHTLPark')
#     btn2 = telebot.types.InlineKeyboardButton('Bijela Idea', callback_data='BijelaIdea')
#     btn3 = telebot.types.InlineKeyboardButton('Bijela Voli', callback_data='BijelaVoli')
#     btn4 = telebot.types.InlineKeyboardButton('Bijela HDL', callback_data='BijelaHDL')
#     btn5 = telebot.types.InlineKeyboardButton('Bijela Zager', callback_data='BijelaZager')
#     btn6 = telebot.types.InlineKeyboardButton('Bijela Dječiji Dom', callback_data='BijelaDetDom')
#     keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)
#     bot.send_message(message.chat.id,
#                      'Уточните остановку',
#                      reply_markup=keyboard)



@bot.message_handler(commands=['menu'])
def mainmenu(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn1 = telebot.types.InlineKeyboardButton('Выберите ваше местоположение:', callback_data='new_call')
    btn2 = telebot.types.InlineKeyboardButton('Посмотрите карту:', url=GOOGLE_MAP)
    keyboard.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     'Новый запрос?',
                     reply_markup=keyboard)


# ========== reply to buttons ============
@bot.callback_query_handler(func=lambda call: True)
def dialogue(call):
    if call.data == 'new_call':
        lets_start(call.message)
    # elif call.data == 'Group1':
    #     Group1(call.message)
    else:
        user = call.from_user.username
        cur_time = get_current_time()

        route1 = when_next(call.data, 'BusBar', 'Bar')
        if route1:
            route1_msg = f'🚌:  {",  ".join(route1)}\n'
        else:
            route1_msg = 'no data'

        route2 = when_next(call.data, 'BusBar', 'Chan')
        if route2:
            route2_msg = f'🚌:  {",  ".join(route2)}\n'
        else:
            route2_msg = 'no data'

        msg_tmplt = f'В сторону Старого Бара 🏰:\n' \
                    f'{route1_msg}' \
                    f'\n' \
                    f'В сторону Чаня 🏘️:\n' \
                    f'{route2_msg}'

        bot.send_message(call.message.chat.id, text=msg_tmplt)
        mainmenu(call.message)


keep_alive()  # load flask-server
bot.polling(non_stop=True, interval=0)  # load bot
