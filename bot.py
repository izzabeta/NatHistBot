import telebot # type: ignore
from telebot import types # type: ignore # для указание типов
import json

with open("text.json", "r", encoding='utf-8') as f:
    content = json.load(f)

bot = telebot.TeleBot(content['telegramToken'], parse_mode='MARKDOWN')
userInfo = dict()


def sendStage(id, currentStage):
    global userInfo
    if not "buttons" in currentStage.keys() or len(currentStage['buttons'])==0:
        reply_markup = None
    else:
        reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for button in currentStage['buttons']:
            reply_markup.add(types.KeyboardButton(button["text"]))
    if "text" in currentStage.keys():
        newText = currentStage["text"].replace("%%USERNAME%%", userInfo[id]['name'])    
        if not reply_markup is None:        
            bot.send_message(id, text=newText, reply_markup=reply_markup)
        else:
            bot.send_message(id, text=newText)
    if "photo" in currentStage.keys():
        for photo_path in currentStage["photo"]:
            with open(photo_path, 'rb') as photo_file:
                bot.send_photo(id, photo_file, reply_markup=reply_markup)
    if "audio" in currentStage.keys():
        for audio_path in currentStage["audio"]:
            with open(audio_path, 'rb') as audio_file:
                bot.send_voice(id, audio_file, reply_markup=reply_markup)
    if "circles" in currentStage.keys():
        for circle_path in currentStage["circles"]:
            with open(circle_path, 'rb') as circle_file:
                bot.send_video_note(id, circle_file, reply_markup=reply_markup)
    if "poll" in currentStage.keys():
        pollInfo = currentStage['poll']
        bot.send_poll(id, pollInfo['question'], pollInfo['options'], type="quiz", correct_option_id=pollInfo['correct_option_id'], is_anonymous=False)
    

@bot.message_handler(commands=['start']) 
def start_handler(message):
    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # btn1 = types.KeyboardButton("")
    # btn2 = types.KeyboardButton("Информация для родителей")
    # btn3 = types.KeyboardButton("Об экскурсии")
    # markup.add(btn1, btn2, btn3)
    bot.send_message(message.from_user.id, text="Привет, друг! Начать экскурсию /excursion \n Информация для родителей - /parents \n Об экскурсии - /about ".format(message.from_user))
    userInfo[message.from_user.id] = {
        'stage':-1,
        'answeredTerms':[], 
        "nameAnswered":False,
        "needName":False,
        'name':message.from_user.first_name,
        "check_input_started":False,
        "check_input_amount":0
    }


@bot.message_handler(commands=['excursion']) 
def exc_handler(message):
    global userInfo
    if userInfo[message.from_user.id]['stage'] == -1: # блок до начала основного контента
        userInfo[message.from_user.id]['stage'] = 0         
        sendStage(message.from_user.id, content['content'][userInfo[message.from_user.id]['stage']])   
    

@bot.message_handler(commands=['parents']) 
def parents_handler(message):
    global userInfo
    if userInfo[message.from_user.id]['stage'] == -1: # блок до начала основного контента
        bot.send_message(message.from_user.id, text='Информация для родителей')


@bot.message_handler(commands=['about']) 
def about_handler(message):
    global userInfo
    if userInfo[message.from_user.id]['stage'] == -1: # блок до начала основного контента
        bot.send_message(message.from_user.id, text='Об экскурсии')


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

def check_for_input(message, currentStage):
    if not "check_options" in currentStage.keys() or len(currentStage['check_options'])==0:
        return True
    
    text = str(message.text).lower().strip()

    for option in currentStage['check_options']:
        if text == option:
            return True
    return False

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
    if userInfo[message.from_user.id]['stage'] == -1: # блок до начала основного контента
        if (message.text == 'Начать экскурсию'):
            userInfo[message.from_user.id]['stage'] = 0         
            sendStage(message.from_user.id, content['content'][userInfo[message.from_user.id]['stage']])                       
        elif (message.text == "Информация для родителей"): 
            bot.send_message(message.from_user.id, text='Информация для родителей')
        elif (message.text == "Об экскурсии"): 
            bot.send_message(message.from_user.id, text='Об экскурсии') 
        return      
    else: # основной контент
        currentStage = content['content'][userInfo[message.from_user.id]['stage']]
        if "actions" in currentStage.keys() and "term" in currentStage['actions']:
            res = check_for_term(message, currentStage) 
            if res is True:
                userInfo[message.from_user.id]['stage'] += 1
                sendStage(message.from_user.id, content['content'][userInfo[message.from_user.id]['stage']])
            elif res is False:
                skip_steps = 1+1
                if "term_skip_steps" in currentStage.keys():
                    skip_steps = int(currentStage["term_skip_steps"])+1
                userInfo[message.from_user.id]['stage'] += skip_steps
                sendStage(message.from_user.id, content['content'][userInfo[message.from_user.id]['stage']])
            else:
                bot.send_message(message.from_user.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок') 
            return
        # проверка на ввода при загадке
        elif "actions" in currentStage.keys() and "check_input" in currentStage['actions']:
            res = check_for_input(message, currentStage) 
            if userInfo[message.from_user.id]["check_input_started"] is False:
                userInfo[message.from_user.id]["check_input_started"] = True
                userInfo[message.from_user.id]["check_input_amout"] = 0
            if res is True or userInfo[message.from_user.id]["check_input_amout"] >= currentStage["try_amount"]: # если правильный ответ, следующий блок
                userInfo[message.from_user.id]['stage'] += 1
                userInfo[message.from_user.id]["check_input_started"] = False
                sendStage(message.from_user.id, content['content'][userInfo[message.from_user.id]['stage']])
                return
            elif res is False: # если не правильно, увеличиваем число попыток, присылаем секцию wrong
                userInfo[message.from_user.id]["check_input_amout"] += 1
                sendStage(message.from_user.id, content['content'][userInfo[message.from_user.id]['stage']]['if_wrong'])
                return
             
        # проверка на ввод имени
        elif "actions" in currentStage.keys() and "checkName" in currentStage['actions']:
            userInfo[message.from_user.id]['name'] = message.text
            userInfo[message.from_user.id]['nameAnswered'] = True
            
        # check for right answer 
        if check_for_right_answer(message, currentStage): # ответ согласно кнопкам
            userInfo[message.from_user.id]['stage'] += 1
            sendStage(message.from_user.id, content['content'][userInfo[message.from_user.id]['stage']])
        else:
            bot.send_message(message.from_user.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок') 


@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    userInfo[pollAnswer.user.id]['stage'] += 1
    sendStage(pollAnswer.user.id, content['content'][userInfo[pollAnswer.user.id]['stage']])

    


bot.polling(none_stop=True)