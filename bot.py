import telebot # type: ignore
from telebot import types # type: ignore # для указание типов
import json
from User import User
with open("text.json", "r", encoding='utf-8') as f:
    content = json.load(f)

bot = telebot.TeleBot(content['telegramToken'], parse_mode='MARKDOWN')
userInfo = User.getDumps()



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
            newText = currentStage["text"].replace("%%USERNAME%%", userInfo[id].name)    
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
    userInfo[id].nextStage()
    userInfo[id].misinput=0
    sendStage(id, userInfo[id].currentStage())
    



@bot.message_handler(commands=['start']) 
def start_handler(message):
    global content
    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # btn1 = types.KeyboardButton("")
    # btn2 = types.KeyboardButton("Информация для родителей")
    # btn3 = types.KeyboardButton("Об экскурсии")
    # markup.add(btn1, btn2, btn3)
    bot.send_message(message.from_user.id, text="Привет, друг! \nНачать экскурcию 👉 /excursion \nОб экскурсии 👉 /about \nДля родителей 👉  /parents ".format(message.from_user))
    if not message.from_user.id in userInfo.keys():
        userInfo[message.from_user.id] = User(message.from_user.id, message.from_user.first_name, content['content'])
    else:
        userInfo[message.from_user.id].reset()



@bot.message_handler(commands=['excursion']) 
def exc_handler(message): 
    global userInfo
    userInfo[message.from_user.id].reset() 
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
    userInfo[message.from_user.id].setStage(map_[message.text.replace("/",'')]-1)    
    sendNextStage(message.from_user.id)


@bot.message_handler(commands=['parents']) 
def parents_handler(message):
    global userInfo
    if userInfo[message.from_user.id].atNegativeStage(): # блок до начала основного контента
        bot.send_message(message.from_user.id, text='*Если вы планируете участвовать в экскурсии совместно с маленькими исследователями, советуем прежде ознакомиться с рекомендациями ниже:*\n1) Если у ребенка есть сложности с чтением, можете помочь прочитать задание, но не отвечайте за него.\n2) Если у ребенка есть сложности с пониманием задания или выражения, помогите понять, объясните своими словами на знакомых аналогиях.\n3) Если есть сложности с навигацией, попробуйте дать подсказку, как пользоваться картой и понимать условные обозначения.\n4) Не отмечайте ответы за ребёнка, он должен держать телефон в своих руках всю экскурсию, это важно для ощущения самостоятельности.\n5) Если ребенок задаёт вопрос, на который нет ответа в чат-боте, предложите ребенку порассуждать совместно с вами, чтобы ребёнок сам попытался дать осмысленный ответ.\n6) Если у вас нет ответа на вопрос, не спешите гуглить. Предложите ребёнку провести совместное мини-исследование дома. Из этого может получится отличная совместная активность.')


@bot.message_handler(commands=['about']) 
def about_handler(message):
    global userInfo
    if userInfo[message.from_user.id].atNegativeStage(): # блок до начала основного контента
        bot.send_message(message.from_user.id, text="🌳 *Цифровое приключение по Таврическому саду для младших школьников*\n\n👋 *Приветствуем вас!*\nМы рады пригласить вас на увлекательную интерактивную экскурсию по чудесным уголкам Таврического сада! Обратите внимание, что мы будем исследовать только небольшую область, но это точно будет незабываемо!\n\n💚 *Кому понравится?*  \nЭта экскурсия подходит для школьников 7-11 лет и предполагает самостоятельное прохождение. Если вы планируете участвовать в экскурсии совместно с маленькими исследователями, советуем прежде ознакомиться с рекомендациями в блоке «Для родителей». \n\n🤷 *Кто мы?*\nЭкскурсия создана с любовью командой студенток DH-центра ИТМО, Шапошниковой Оксаной и Сороколетовой Елизаветой. Мы надеемся, что вам понравится!\n\n⌚*Сколько времени займет?*  \nПриготовьтесь провести с нами около часа. Время экскурсии зависит от темпа её прохождения, скорости чтения ребёнка и выборов внутри самого приключения. Вы можете прервать экскурсию и возобновить её, когда снова будете в саду. Мы постараемся сделать это время максимально интересным и насыщенным!\n\n🗺 *Где все это происходит?*  \nЭкскурсия начинается со входа в Таврический сад со стороны Шпалерной улицы и проходит от дорожки у входа до ближайшего моста вдоль ограды. Мы выбрали самое уединённое место парка, чтобы никто не помешал вам насладиться природой!\n\n🌱*Что в основе?*  \nНаше путешествие вдохновлено естественно-историческими экскурсиями XX века, предполагающими изучение природы в непосредственном контакте с ней. Подробнее о феномене этих экскурсий можете почитать в [статье](https://vk.com/@smo_spbu-estestvenno-istoricheskie-ekskursii-po-petrogradu-be-raikova) Шапошниковой Оксаны. Вы не только увидите красивые места, но и в буквальном смысле прикоснётесь к природе!")
        #bot.send_message(message.from_user.id, text="⌚*Сколько времени займет?*  \nПриготовьтесь провести с нами около часа. Время экскурсии зависит от темпа её прохождения, скорости чтения ребёнка и выборов внутри самого приключения. Вы можете прервать экскурсию и возобновить её, когда снова будете в саду. Мы постараемся сделать это время максимально интересным и насыщенным!\n\n🗺 *Где все это происходит?*  \nЭкскурсия начинается со входа в Таврический сад со стороны Шпалерной улицы и проходит от дорожки у входа до ближайшего моста вдоль ограды. Мы выбрали самое уединённое место парка, чтобы никто не помешал вам насладиться природой!\n\n🌱*Что в основе?*  \nНаше путешествие вдохновлено естественно-историческими экскурсиями XX века, предполагающими изучение природы в непосредственном контакте с ней. Подробнее о феномене этих экскурсий можете почитать в [статье](https://vk.com/@smo_spbu-estestvenno-istoricheskie-ekskursii-po-petrogradu-be-raikova) Шапошниковой Оксаны. Вы не только увидите красивые места, но и в буквальном смысле прикоснётесь к природе!")

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
    if userInfo[message.from_user.id].atNegativeStage(): # блок до начала основного контента
        if (message.text == 'Начать экскурсию'):
            sendNextStage(message.from_user.id)                   
        elif (message.text == "Информация для родителей"): 
            bot.send_message(message.from_user.id, text='Информация для родителей')
        elif (message.text == "Об экскурсии"): 
            bot.send_message(message.from_user.id, text='Об экскурсии') 
        return      
    else: # основной контент
        currentStage = userInfo[message.from_user.id].currentStage()
        if "actions" in currentStage.keys() and "term" in currentStage['actions']:
            res = check_for_term(message, currentStage) 
            if res is True:
                sendNextStage(message.from_user.id)
            elif res is False:
                skip_steps = 1
                if "term_skip_steps" in currentStage.keys():
                    skip_steps = int(currentStage["term_skip_steps"])
                userInfo[message.from_user.id].addStage(skip_steps)
                sendNextStage(message.from_user.id)
            else:
                if userInfo[message.from_user.id].misinput < 2:
                    bot.send_message(message.from_user.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок')
                    userInfo[message.from_user.id].misinput += 1
                else:
                    sendNextStage(message.from_user.id)
            return
        elif "actions" in currentStage.keys() and "fork" in currentStage['actions']:
            res = check_for_fork(message, currentStage) 
            if res is True: # fork_continue
                sendNextStage(message.from_user.id)
            elif res is False: # fork_skip_next
                skip_steps = 1
                if "fork_skip_steps" in currentStage.keys():
                    skip_steps = int(currentStage["fork_skip_steps"])
                userInfo[message.from_user.id].addStage(skip_steps)                
                userInfo[message.from_user.id].insertMany(currentStage['fork_substitution'])  
                sendNextStage(message.from_user.id)
                return
            else:
                if userInfo[message.from_user.id].misinput < 2:
                    bot.send_message(message.from_user.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок')
                    userInfo[message.from_user.id].misinput += 1
                else:
                    sendNextStage(message.from_user.id)
                
        # проверка на ввода при загадке
        elif "actions" in currentStage.keys() and "check_input" in currentStage['actions']:
            res = check_for_input(message, currentStage) 
            if userInfo[message.from_user.id].check_input_started is False:
                userInfo[message.from_user.id].check_input_started = True
                userInfo[message.from_user.id].check_input_amout = 0
            if res is True or userInfo[message.from_user.id].check_input_amout >= currentStage["try_amount"]: # если правильный ответ, следующий блок
                userInfo[message.from_user.id].check_input_started = False
                sendNextStage(message.from_user.id)
                return
            elif res is False: # если не правильно, увеличиваем число попыток, присылаем секцию wrong
                userInfo[message.from_user.id].check_input_amout += 1
                sendStage(message.from_user.id, userInfo[message.from_user.id].currentStage()['if_wrong'])
                return
             
        # проверка на ввод имени
        elif "actions" in currentStage.keys() and "checkName" in currentStage['actions']:
            print(message.text)
            userInfo[message.from_user.id].name = message.text
            userInfo[message.from_user.id].nameAnswered = True
            
        # check for right answer 
        if check_for_right_answer(message, currentStage): # ответ согласно кнопкам
            sendNextStage(message.from_user.id)
        else:
            if userInfo[message.from_user.id].misinput < 2:
                bot.send_message(message.from_user.id, text='Не понял ответ 🤔. Пожалуйста, нажми на одну из кнопок')
                userInfo[message.from_user.id].misinput += 1
            else:
                sendNextStage(message.from_user.id)


@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    sendNextStage(pollAnswer.user.id)
    


bot.polling(none_stop=True)