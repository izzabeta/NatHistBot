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
        reply_markup = types.ReplyKeyboardRemove()
    else:
        reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for button in currentStage['buttons']:
            reply_markup.add(types.KeyboardButton(button["text"]))
    
    if "order" in currentStage.keys():
        order = currentStage["order"]
    else:
        order = ["text", "photo", "audio", "circles", "poll", "poll_no_right_answer"]
    
    for key in order:
        if not key in currentStage.keys():
            continue
        if "text" in [key]:
            newText = currentStage["text"].replace("%%USERNAME%%", userInfo[id]['name'])    
            if not reply_markup is None:        
                bot.send_message(id, text=newText, reply_markup=reply_markup)
            else:
                bot.send_message(id, text=newText)
        if "photo" in [key]:
            for photo_path in currentStage["photo"]:
                with open(photo_path, 'rb') as photo_file:
                    bot.send_photo(id, photo_file, reply_markup=reply_markup)
        if "audio" in [key]:
            for audio_path in currentStage["audio"]:
                with open(audio_path, 'rb') as audio_file:
                    bot.send_voice(id, audio_file, reply_markup=reply_markup)
        if "circles" in [key]:
            for circle_path in currentStage["circles"]:
                with open(circle_path, 'rb') as circle_file:
                    bot.send_video_note(id, circle_file, reply_markup=reply_markup)
        if "poll" in [key]:
            pollInfo = currentStage['poll']
            bot.send_poll(id, pollInfo['question'], pollInfo['options'], type="quiz", correct_option_id=pollInfo['correct_option_id'], is_anonymous=False)
        if "poll_no_right_answer" in [key]:
            pollInfo = currentStage['poll_no_right_answer']
            bot.send_poll(id, pollInfo['question'], pollInfo['options'], type="regular", is_anonymous=False)

def sendNextStage(id):
    global userInfo
    userInfo[id]['stage'] += 1
    sendStage(id, userInfo[id]['content'][userInfo[id]['stage']])



@bot.message_handler(commands=['start']) 
def start_handler(message):
    global content
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
        "check_input_amount":0,
        "content":content['content']
    }


@bot.message_handler(commands=['excursion']) 
def exc_handler(message): 
    global userInfo
    if userInfo[message.from_user.id]['stage'] == -1: # блок до начала основного контента
        userInfo[message.from_user.id]['stage'] = -1         
        sendNextStage(message.from_user.id)


@bot.message_handler(commands=['block1', "block2", "block3", "block4", "block5", "block6", "block7", "block8", "fork"]) 
def map_handler(message):
    map_ = {
        'block1':0, 
        "block2":15, 
        "block3":15+22, 
        "block4":15+22+17, 
        "block5":15+22+17+16, 
        "block6":15+22+17+16+14, 
        "block7":15+22+17+16+14+17, 
        "block8":15+22+17+16+14+17+16,
        "fork":15+22+17+16+14-2
    }
    global userInfo
    userInfo[message.from_user.id]['stage'] = map_[message.text.replace("/",'')]-1        
    sendNextStage(message.from_user.id)


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


def check_for_fork(message, currentStage):
    if not "buttons" in currentStage.keys() or len(currentStage['buttons'])==0:
        return True
    
    for button in currentStage['buttons']:
        if message.text == button['text']:
            if button["type"]=="fork_continue":
                return True
            elif button["type"]=="fork_skip_next":
                return False
    return None


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
            sendNextStage(message.from_user.id)                   
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
                sendNextStage(message.from_user.id)
            elif res is False:
                skip_steps = 1
                if "term_skip_steps" in currentStage.keys():
                    skip_steps = int(currentStage["term_skip_steps"])
                userInfo[message.from_user.id]['stage'] += skip_steps
                sendNextStage(message.from_user.id)
            else:
                bot.send_message(message.from_user.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок') 
            return
        elif "actions" in currentStage.keys() and "fork" in currentStage['actions']:
            res = check_for_fork(message, currentStage) 
            if res is True: # fork_continue
                sendNextStage(message.from_user.id)
            elif res is False: # fork_skip_next
                skip_steps = 1
                if "fork_skip_steps" in currentStage.keys():
                    skip_steps = int(currentStage["fork_skip_steps"])
                userInfo[message.from_user.id]['stage'] += skip_steps
                for el in currentStage['fork_substitution'][::-1]:
                    userInfo[message.from_user.id]['content'].insert(userInfo[message.from_user.id]['stage'], el)
                userInfo[message.from_user.id]['stage'] -= 1
                sendNextStage(message.from_user.id)
                return
            else:
                bot.send_message(message.from_user.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок')
        # проверка на ввода при загадке
        elif "actions" in currentStage.keys() and "check_input" in currentStage['actions']:
            res = check_for_input(message, currentStage) 
            if userInfo[message.from_user.id]["check_input_started"] is False:
                userInfo[message.from_user.id]["check_input_started"] = True
                userInfo[message.from_user.id]["check_input_amout"] = 0
            if res is True or userInfo[message.from_user.id]["check_input_amout"] >= currentStage["try_amount"]: # если правильный ответ, следующий блок
                userInfo[message.from_user.id]["check_input_started"] = False
                sendNextStage(message.from_user.id)
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
            sendNextStage(message.from_user.id)
        else:
            bot.send_message(message.from_user.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок') 


@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    sendNextStage(pollAnswer.user.id)
    


bot.polling(none_stop=True)