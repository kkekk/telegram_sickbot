import time
import re
import telepot
import json
import urllib
import requests
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '407199402:AAFE_gnKipSaF-a6NFIHeiPoIjH4RbEJ94A'
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

registered = [line.strip().split(",") for line in open('registered.txt')]
highestQ = 0 if not registered else int(max(registered, key=lambda x:x[1])[1])
checkingForMatric = False

def queuenum(nums):
    for i in nums:
        yield(i)

patientqueue = queuenum(range(100))

def read_input(filename):
    '''
    Returns the last 3 digits of each row in registered.txt, each being the queue number.
    '''
    to_return = []
    with open(filename,'r') as f:
        for row in f:
            if '\n' in row:
                row = row.replace('\n','')
            if row != '' and len(row) == 13:
                to_return.append(row)
    print(to_return)
    for i in to_return:
        y = i[-3:]
        print(y)
    queue = [(j[-3:]) for j in to_return]
    return queue

def checkForMatric(matric):
    '''
    Returns the queue number of the person registering, assigning it to his/hers matric number.
    '''
    global checkingForMatric
    global highestQ
    checkingForMatric = False
    if not re.match(r'[uU]\d{7}[a-zA-Z]', matric):
        checkingForMatric = True
        return 'That\'s not a valid matric number, can you try again?'
    if matric in registered:
        return 'You have already registered!'
    registered.append(matric)
    highestQ = highestQ +1
    q = next(patientqueue)
    with open("registered.txt", "a") as f:
        if highestQ < 10:
            f.write(matric + ",00" + str(highestQ) + "\n")
            zeroes = "00" + str(highestQ)
        elif highestQ >= 10 and highestQ < 100:
            f.write(matric + ",0" + str(highestQ) + "\n")
            zeroes = "0" + str(highestQ)
        elif highestQ >= 100:
            f.write(matric + str(highestQ) + "\n")
            zeroes = str(highestQ)
    patientqueuenum = 'Registered Sucessfully! Please note that your queue number is: \n\n' + zeroes + '\n\nPlease arrive to the clinic in 30 minutes' 
    f = open('registered.txt', 'r')
    file_contents = f.read()
    print (file_contents)
    return (patientqueuenum)

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':

        msg_text = msg['text']

        response = ''
        if (msg_text.startswith('/')):
            # parse the command excluding the '/'
            command = msg_text[1:].lower()

            if command == 'start':
                # prepare confirm keyboard
                confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Confirm', callback_data='confirm')],
                [InlineKeyboardButton(text='Cancel', callback_data='cancel')],
                ])

                # send response with keyboard
                response += 'I can offer you a queue number in advance so that you may minimise your waiting time at the clinic.\n \nHowever, this is ONLY for general consultation.\
 For other services, please contact the clinic directly. \n\nOnce registered, you will be issued a queue number. You have to be an NTU student/staff to register. \n \nWould you like to register?'
                bot.sendMessage(chat_id, response, reply_markup = confirm_keyboard)

                return
            elif command == 'check':
                #prepare check
                response = 'The current numbers in queue are: ' + str(read_input('registered.txt'))
            else:
                response = "That is not a valid command, please enter /start to begin registration or /check to display queue numbers."

        elif checkingForMatric:
            response = checkForMatric(msg_text)
        else:
            response = "Hi! I\'m Sickbot, service provider to Fullerton Medical Centre @ NTU. Type /start to begin registration! "
    bot.sendMessage(chat_id, response)

def on_callback_query(msg):
    global checkingForMatric
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    #close the keyboard
    inline_message_id = msg['message']['chat']['id'], msg['message']['message_id']
    bot.editMessageReplyMarkup(inline_message_id, reply_markup=None)
    
    if (query_data == 'confirm'):
        bot.sendMessage(from_id, 'Please enter your Matriculation Number:')
        checkingForMatric = True
        
    else:
        bot.sendMessage(from_id, 'Have a nice day!')

    bot.answerCallbackQuery(query_id)


bot = telepot.Bot(TOKEN)


MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
    



##if __name__ == '__main__':
##        f = open('registered.txt', 'r')
##        file_contents = f.read()
##        print (file_contents)

while 1:
    time.sleep(10)
