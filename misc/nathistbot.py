import telebot
from telebot import types # для указание типов
import json

with open("text.json", "r", encoding='utf-8') as f:
    content = json.load(f)

bot = telebot.TeleBot(content['telegramToken'])
userInfo = dict()


def sendStage(message, currentStage, reply_markup=None):
    global userInfo
    
    if not reply_markup is None:
        newText = currentStage["text"].replace("%%USERNAME%%", userInfo[message.chat.id]['name'])
        bot.send_message(message.chat.id, text=newText, reply_markup=reply_markup)
    else:
        bot.send_message(message.chat.id, text=newText)
    if "photo" in currentStage.keys():
        for photo_path in currentStage["photo"]:
            with open(photo_path, 'rb') as photo_file:
                bot.send_photo(message.chat.id, photo_file)
    if "audio" in currentStage.keys():
        for audio_path in currentStage["audio"]:
            with open(audio_path, 'rb') as audio_file:
                bot.send_voice(message.chat.id, audio_file)
    if "circles" in currentStage.keys():
        for circle_path in currentStage["circles"]:
            with open(circle_path, 'rb') as circle_file:
                bot.send_video_note(message.chat.id, circle_file)
    if "poll" in currentStage.keys():
        pollInfo = currentStage['poll']
        bot.send_poll(message.chat.id, pollInfo['question'], pollInfo['options'], type="quiz", correct_option_id=pollInfo['correct_option_id'])
    

@bot.message_handler(commands=['start']) 
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Начать экскурсию")
    btn2 = types.KeyboardButton("Информация для родителей")
    btn3 = types.KeyboardButton("Об экскурсии")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, text="Привет, друг!".format(message.from_user), reply_markup=markup)
    
    
@bot.message_handler(content_types=['text'])
def func(message):
    global userInfo
    if (message.text == 'Начать экскурсию'):
        userInfo[message.chat.id] = {
            'stage':0,
            'answeredTerms':[], 
            "nameAnswered":False,
            'name':message.from_user.first_name
        }
        bot.send_message(message.chat.id, text="Как тебя зовут?", reply_markup=types.ReplyKeyboardRemove())
        return
        
    if (message.text == "Нет, продолжить" or message.text == "ДАЛЬШЕ"):
        userInfo[message.chat.id]['stage'] += 1
    if (message.text == "ДАЛЬШЕ" or message.text == "Начать экскурсию" or message.text == "Нет, продолжить"):        
        currentStage = content['content'][userInfo[message.chat.id]['stage']]
        # последнее сообщение
        if userInfo[message.chat.id]['stage'] >= len(content['content']) - 1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Обратная связь")
            btn2 = types.KeyboardButton("Связаться с нами")
            markup.add(btn1, btn2)
            bot.send_message(message.chat.id, text=currentStage["text"], reply_markup=markup)
            return
        # обычное сообщение
        if not "knowMore" in currentStage.keys():
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("ДАЛЬШЕ"))
            if "terms" in currentStage.keys():
                for t in currentStage['terms']:
                    markup.add(types.KeyboardButton(t['name']))
            sendStage(message, currentStage, reply_markup=markup)  
            
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Нет, продолжить"))
            markup.add(types.KeyboardButton("Да, хочу"))
            sendStage(message, currentStage, reply_markup=markup)
    elif (message.text == "Да, хочу"):
        currentStage = content['content'][userInfo[message.chat.id]['stage']]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("ДАЛЬШЕ"))
        sendStage(message, currentStage['knowMore'], reply_markup=markup)
        userInfo[message.chat.id]['stage'] += 1
    elif (message.text == "Информация для родителей"): 
        bot.send_message(message.chat.id, text='Информация для родителей')
    elif (message.text == "Об экскурсии"): 
        bot.send_message(message.chat.id, text='Об экскурсии')       
    else:        
        if userInfo[message.chat.id]['nameAnswered'] is False:
            userInfo[message.chat.id]['name'] = message.text
            userInfo[message.chat.id]['nameAnswered'] = True

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("ДАЛЬШЕ"))
            sendStage(message, content['content'][userInfo[message.chat.id]['stage']], reply_markup=markup)  

            return
        currentStage = content['content'][userInfo[message.chat.id]['stage']]
        if "terms" in currentStage.keys():
            for t in currentStage['terms']:
                if (message.text == t['name']):
                    userInfo[message.chat.id]['answeredTerms'].append(t['name'])
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add(types.KeyboardButton("ДАЛЬШЕ"))
                    if "terms" in currentStage.keys():
                        for t2 in currentStage['terms']:
                            if not t2['name'] in userInfo[message.chat.id]['answeredTerms']:
                                markup.add(types.KeyboardButton(t2['name']))
                    sendStage(message, t['description'], reply_markup=markup)                   
                    
                    return
        bot.send_message(message.chat.id, text="На такую команду я не запрограммировал..")

@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    print(pollAnswer)

bot.polling(none_stop=True)