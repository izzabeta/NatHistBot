import telebot
from telebot import types # для указание типов
import json

with open("text.json", "r", encoding='utf-8') as f:
    content = json.load(f)

bot = telebot.TeleBot(content['telegramToken'], parse_mode='MARKDOWN')
userInfo = dict()


def sendStage(message, currentStage):
    global userInfo
    if not "buttons" in currentStage.keys() or len(currentStage['buttons'])==0:
        reply_markup = None
    else:
        reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for button in currentStage['buttons']:
            reply_markup.add(types.KeyboardButton(button["text"]))
    if "text" in currentStage.keys():
        newText = currentStage["text"].replace("%%USERNAME%%", userInfo[message.chat.id]['name'])    
        if not reply_markup is None:        
            bot.send_message(message.chat.id, text=newText, reply_markup=reply_markup)
        else:
            bot.send_message(message.chat.id, text=newText)
    if "photo" in currentStage.keys():
        for photo_path in currentStage["photo"]:
            with open(photo_path, 'rb') as photo_file:
                bot.send_photo(message.chat.id, photo_file, reply_markup=reply_markup)
    if "audio" in currentStage.keys():
        for audio_path in currentStage["audio"]:
            with open(audio_path, 'rb') as audio_file:
                bot.send_voice(message.chat.id, audio_file, reply_markup=reply_markup)
    if "circles" in currentStage.keys():
        for circle_path in currentStage["circles"]:
            with open(circle_path, 'rb') as circle_file:
                bot.send_video_note(message.chat.id, circle_file, reply_markup=reply_markup)
    if "poll" in currentStage.keys():
        pollInfo = currentStage['poll']
        bot.send_poll(message.chat.id, pollInfo['question'], pollInfo['options'], type="quiz", correct_option_id=pollInfo['correct_option_id'])
    

@bot.message_handler(commands=['start']) 
def start_handler(message):
    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # btn1 = types.KeyboardButton("")
    # btn2 = types.KeyboardButton("Информация для родителей")
    # btn3 = types.KeyboardButton("Об экскурсии")
    # markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, text="Привет, друг! Начать экскурсию /excursion \n Информация для родителей - /parents \n Об экскурсии - /about ".format(message.from_user))
    userInfo[message.chat.id] = {
        'stage':-1,
        'answeredTerms':[], 
        "nameAnswered":False,
        "needName":False,
        'name':message.from_user.first_name
    }


@bot.message_handler(commands=['excursion']) 
def exc_handler(message):
    global userInfo
    if userInfo[message.chat.id]['stage'] == -1: # блок до начала основного контента
        userInfo[message.chat.id]['stage'] = 0         
        sendStage(message, content['content'][userInfo[message.chat.id]['stage']])   
    

@bot.message_handler(commands=['parents']) 
def parents_handler(message):
    global userInfo
    if userInfo[message.chat.id]['stage'] == -1: # блок до начала основного контента
        bot.send_message(message.chat.id, text='Информация для родителей')


@bot.message_handler(commands=['about']) 
def about_handler(message):
    global userInfo
    if userInfo[message.chat.id]['stage'] == -1: # блок до начала основного контента
        bot.send_message(message.chat.id, text='Об экскурсии')


def check_for_term(message, currentStage):
    if not "buttons" in currentStage.keys() or len(currentStage['buttons'])==0:
        return True
    
    for button in currentStage['buttons']:
        if message.text == button['text']:
            if button["type"]=="term_positive":
                return True
            elif button["type"]=="term_skip_next":
                return False
    return None

def check_for_right_answer(message, currentStage):
    if not "buttons" in currentStage.keys() or len(currentStage['buttons'])==0:
        return True
    
    for button in currentStage['buttons']:
        if message.text == button['text']:
            return True
    return False
    
@bot.message_handler(content_types=['text'])
def general_message_handler(message):
    global userInfo
    if userInfo[message.chat.id]['stage'] == -1: # блок до начала основного контента
        if (message.text == 'Начать экскурсию'):
            userInfo[message.chat.id]['stage'] = 0         
            sendStage(message, content['content'][userInfo[message.chat.id]['stage']])                       
        elif (message.text == "Информация для родителей"): 
            bot.send_message(message.chat.id, text='Информация для родителей')
        elif (message.text == "Об экскурсии"): 
            bot.send_message(message.chat.id, text='Об экскурсии') 
        return      
    else: # основной контент
        currentStage = content['content'][userInfo[message.chat.id]['stage']]
        if "actions" in currentStage.keys() and "term" in currentStage['actions']:
            res = check_for_term(message, currentStage) 
            if res is True:
                userInfo[message.chat.id]['stage'] += 1
                sendStage(message, content['content'][userInfo[message.chat.id]['stage']])
            elif res is False:
                userInfo[message.chat.id]['stage'] += 2
                sendStage(message, content['content'][userInfo[message.chat.id]['stage']])
            else:
                bot.send_message(message.chat.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок') 
            return
        # проверка на ввод имени
        if "actions" in currentStage.keys() and "checkName" in currentStage['actions']:
            userInfo[message.chat.id]['name'] = message.text
            userInfo[message.chat.id]['nameAnswered'] = True
        # check for right answer 
        if check_for_right_answer(message, currentStage): # ответ согласно кнопкам
            userInfo[message.chat.id]['stage'] += 1
            sendStage(message, content['content'][userInfo[message.chat.id]['stage']])
        else:
            bot.send_message(message.chat.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок') 


@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    print(pollAnswer)

bot.polling(none_stop=True)