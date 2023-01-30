import sqlite3
import os
import re
from telegram.ext import Updater
from telegram.ext import (CommandHandler,MessageHandler,ConversationHandler,CallbackQueryHandler,Filters)
from telegram import (ReplyKeyboardMarkup,InlineKeyboardMarkup,InlineKeyboardButton)
import logging
import datetime as dt
import pandas as pd
import numpy as np

conn=sqlite3.connect('Database.sqlite',check_same_thread=False)
cur=conn.cursor()

#database code
#    cur.execute('''CREATE TABLE IF NOT EXISTS Data(
#    id INTEGER PRIMARY KEY AUTOINCREMENT,
#    user_id TEXT UNIQUE,
#    username TEXT UNIQUE,
#    contact_id TEXT UNIQUE,
#    gender TEXT NULL,
#    age TEXT NULL,
#    chat_request TEXT NULL
#    )''')


#bot id : @privatechat_2021bot

updater=Updater(token='1853991623:AAFNPvIhm0RiYUuRqNeiNVHnKNNgAlpflGs',use_context=True)

dispatcher=updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

NEWUSERNAME=range(1)

def start_function(update,context) :
    already_join=False

    cur.execute('SELECT user_id FROM Data')

    users_list=[item[0] for item in cur]

    if str(update.message.chat.id) in users_list :
        starttext='You are currently a member of this bot'
        already_join=True
    else :

        try :
            username=update.message.chat.username
            username=username+''
        except :
            try :
                first_name=(update.message.chat.first_name).strip()
            except : first_name=''
            try :
                last_name=(update.message.chat.last_name).strip()
            except : last_name=''
            username=first_name+last_name
            if len(username)>=3 :
                username=username+str(dt.datetime.now()).split('.')[1]
            else :
                username='user_'+str(dt.datetime.now()).split('.')[1]
        cur.execute('SELECT username FROM Data')
        usernames_list=[item[0] for item in cur]
        while username in usernames_list :
            username='user_'+str(dt.datetime.now()).split('.')[1]

        cur.execute('INSERT INTO Data (user_id,username) VALUES (?,?)',(update.message.chat.id,username))
        conn.commit()
        starttext=f'''Welcome to private chat bot
your username is : {username}
you can change it via menu whenever you want
Please set your gender if you want'''

        keyboard=[[InlineKeyboardButton('Male',callback_data='Gmale_'+str(update.message.chat.id)),
                InlineKeyboardButton('Female',callback_data='Gfemale_'+str(update.message.chat.id))],
                [InlineKeyboardButton('Others',callback_data='Gothers_'+str(update.message.chat.id)),
                InlineKeyboardButton('Skip',callback_data='Gskip_'+str(update.message.chat.id))]]

        inline_markup=InlineKeyboardMarkup(keyboard)

    if already_join==False :
        context.bot.send_message(chat_id=update.message.chat.id,text=starttext,reply_markup=inline_markup)
    else :
        context.bot.send_message(chat_id=update.message.chat.id,text=starttext)

def myusername_function(update,context) :
    cur.execute('SELECT username FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    username=cur.fetchone()[0]
    text=f'Your username is : {username}'
    context.bot.send_message(chat_id=update.message.chat.id,text=text)

def chusername_function(update,context) :
    text='''Enter your new username with the prefix changeun-
example : changeun-myname2020'''
    context.bot.send_message(chat_id=update.message.chat.id,text=text)

def newchat_function(update,context) :
    text='''Enter your contact username after @
example : @myfriend'''
    context.bot.send_message(chat_id=update.message.chat.id,text=text)

def message_function(update,context) :
    ordinary_message=False
    message=update.message.text

    if re.search('^@\S+',message) :
        username=message.replace('@','')
        cur.execute('SELECT user_id FROM Data WHERE username=?',(username,))
        try :
            contact_id=cur.fetchone()[0]

            cur.execute('UPDATE Data SET contact_id=? WHERE user_id=?',(contact_id,str(update.message.chat.id)))
            conn.commit()
            text=f"You can now chat with {message}"
            keyboard=[[InlineKeyboardButton('Yes',callback_data='connaccept_'+str(update.message.chat.id)),
                InlineKeyboardButton('Block',callback_data='connreject_'+str(update.message.chat.id))]]
            cur.execute('SELECT username FROM Data WHERE user_id=?',(str(update.message.chat.id),))
            contact_username=cur.fetchone()[0]
            inline_markup=InlineKeyboardMarkup(keyboard)
            keyboardtext=f'{contact_username} made connection with you, Do you also want to make connection?'
            context.bot.send_message(chat_id=int(contact_id),text=keyboardtext,reply_markup=inline_markup)
        except :
            text="This username wasn't found"
        #context.bot.send_message(chat_id=update.message.chat.id,text=text)
    elif re.search('changeun-.+',message) or re.search('Changeun-.+',message):
        try :
            new_username=message.split('changeun-')[1].replace(' ','')
        except :
            new_username=message.split('Changeun-')[1].replace(' ','')
        cur.execute('SELECT username FROM Data')
        usernames=[item[0] for item in cur]
        if len(new_username)<4 :
            text='username should at least contain 4 characters'

        elif new_username in usernames :
            text='This username is taken by someone else'
        else :
            cur.execute('UPDATE Data SET username=? WHERE user_id=?',(new_username,str(update.message.chat.id)))
            conn.commit()
            text='username was successfully changed'

    else :
        cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
        try :
            contact_id=cur.fetchone()[0]
            context.bot.send_message(chat_id=int(contact_id),text=message)
            ordinary_message=True
        except :
            text='You need to fist make a connection with someone'
    if ordinary_message==False :
        context.bot.send_message(chat_id=update.message.chat.id,text=text)

def stopchat_function(update,context) :
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    contact_id=cur.fetchone()[0]
    if contact_id!=None :
        cur.execute('UPDATE Data SET contact_id=NULL WHERE user_id=?',(str(update.message.chat.id),))
        cur.execute('UPDATE Data SET contact_id=NULL WHERE user_id=?',(contact_id,))
        conn.commit()
        context.bot.send_message(chat_id=update.message.chat.id,text='Connection closed')
        context.bot.send_message(chat_id=int(contact_id),text='Connection closed by the other user')
    else :
        context.bot.send_message(chat_id=update.message.chat.id,text="You don't have an active connection")

def button(update,context) :

    query = update.callback_query
    query.answer()
    message=query.data

    contact_id=re.findall('^conn\S+_(\S+)',message)[0]

    if message.startswith('connaccept_') :
        cur.execute('UPDATE Data SET contact_id=? WHERE user_id=?',(contact_id,str(update.callback_query.message.chat.id)))
        conn.commit()
        reptext='Connection made'
    else :
        contact_id=message.split('_')[1]
        cur.execute('UPDATE Data SET contact_id=NULL WHERE user_id=?',(contact_id,))
        reptext="Connection was closed on both ends"
        context.bot.send_message(chat_id=int(contact_id),text='Connection was closed by the other end')
    query.edit_message_text(text=reptext)

def media_function(update,context) :
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    try :
        contact_id=cur.fetchone()[0]
        photo_file=update.message.photo[-1].get_file()
        filename='img_'+str(dt.datetime.now()).split('.')[1]+'.png'
        photo_file.download(filename)
        context.bot.send_photo(chat_id=int(contact_id),photo=open(filename,'rb'))
        os.remove(filename)
    except :
        context.bot.send_message(chat_id=update.message.chat.id,text='You first need to make a connection')

def voice_function(update,context) :
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    try :
        contact_id=cur.fetchone()[0]
        voice_id=update.message.voice.file_id
        voice_file=context.bot.get_file(voice_id)
        filename='voice_'+str(dt.datetime.now()).split('.')[1]+'.ogg'
        voice_file.download(filename)
        context.bot.send_voice(chat_id=int(contact_id),voice=open(filename,'rb'))
        os.remove(filename)
    except :
        context.bot.send_message(chat_id=update.message.chat.id,text='You first need to make a connection')

def gif_function(update,context) :
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    try :
        contact_id=cur.fetchone()[0]
        gif_id=update.message.animation.file_id
        gif_file=context.bot.get_file(gif_id)
        filename='gif_'+str(dt.datetime.now()).split('.')[1]+'.mp4'
        gif_file.download(filename)
        context.bot.send_animation(chat_id=int(contact_id),animation=open(filename,'rb'))
        os.remove(filename)
    except :
        context.bot.send_message(chat_id=update.message.chat.id,text='You first need to make a connection')

def zip_function(update,context) :
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    try :
        contact_id=cur.fetchone()[0]
        zip_id=update.message.document.file_id
        zip_file=context.bot.get_file(zip_id)
        filename='zip_'+str(dt.datetime.now()).split('.')[1]+'.zip'
        zip_file.download(filename)
        context.bot.send_document(chat_id=int(contact_id),document=open(filename,'rb'))
        os.remove(filename)
    except :
        context.bot.send_message(chat_id=update.message.chat.id,text='You first need to make a connection')

def pdf_function(update,context) :
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    try :
        contact_id=cur.fetchone()[0]
        pdf_id=update.message.document.file_id
        pdf_file=context.bot.get_file(pdf_id)
        filename='pdf_'+str(dt.datetime.now()).split('.')[1]+'.pdf'
        pdf_file.download(filename)
        context.bot.send_document(chat_id=int(contact_id),document=open(filename,'rb'))
        os.remove(filename)
    except :
        context.bot.send_message(chat_id=update.message.chat.id,text='You first need to make a connection')

def dice_function(update,context) :
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    try :
        contact_id=cur.fetchone()[0]
        context.bot.send_dice(chat_id=int(contact_id),emoji=update.message.dice.emoji)
    except :
        context.bot.send_message(chat_id=update.message.chat.id,text='You first need to make a connection')

def video_function(update,context) :
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    try :
        contact_id=cur.fetchone()[0]
        video_id=update.message.video.file_id
        video_file=context.bot.get_file(video_id)
        filename='mp4_'+str(dt.datetime.now()).split('.')[1]+'.mp4'
        video_file.download(filename)
        context.bot.send_video(chat_id=int(contact_id),video=open(filename,'rb'))
        os.remove(filename)
    except :
        context.bot.send_message(chat_id=update.message.chat.id,text='You first need to make a connection')

def image_function(update,context) :
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    try :
        contact_id=cur.fetchone()[0]
        image_id=update.message.document.file_id
        image_suffix=(update.message.document.file_name).split('.')[1]
        image_file=context.bot.get_file(image_id)
        filename='image_'+str(dt.datetime.now()).split('.')[1]+'.'+image_suffix
        image_file.download(filename)
        context.bot.send_document(chat_id=int(contact_id),document=open(filename,'rb'))
        os.remove(filename)
    except :
        context.bot.send_message(chat_id=update.message.chat.id,text='You first need to make a connection')

def gender_button(update,context) :
    query = update.callback_query
    query.answer()
    message=(query.data)[1:]
    gender=message.split('_')[0]
    user_id=message.split('_')[1]
    if gender!='skip' :
        cur.execute('UPDATE Data SET gender=? WHERE user_id=?',(gender,user_id))
        conn.commit()

    keyboard=[[InlineKeyboardButton('-20',callback_data='Ag-20_'+user_id),
        InlineKeyboardButton('20-30',callback_data='Ag20-30_'+user_id),
        InlineKeyboardButton('30-40',callback_data='Ag30-40_'+user_id)],
        [InlineKeyboardButton('40-50',callback_data='Ag40-50_'+user_id),
        InlineKeyboardButton('50-60',callback_data='Ag50-60_'+user_id),
        InlineKeyboardButton('+60',callback_data='Ag+60_'+user_id)],
        [InlineKeyboardButton('Skip',callback_data='Agskip_'+user_id)]]

    inline_markup=InlineKeyboardMarkup(keyboard)

    replytext='All right, Now set your age range if you want'
    query.edit_message_text(text=replytext,reply_markup=inline_markup)


def age_button(update,context) :
    query = update.callback_query
    query.answer()
    message=(query.data)[2:]
    age_range=message.split('_')[0]
    user_id=message.split('_')[1]
    if age_range!='skip' :
        cur.execute('UPDATE Data SET age=? WHERE user_id=?',(age_range,user_id))
        conn.commit()
    replytext='All set and done, You can use the bot'
    query.edit_message_text(text=replytext)

def anonymous_function(update,context) :
    user_id=str(update.message.chat.id)
    cur.execute('SELECT contact_id FROM Data WHERE user_id=?',(user_id,))

    contact_id=cur.fetchone()[0]
    if contact_id!=None :

        context.bot.send_message(chat_id=int(user_id),text='You are currently in a chat, stop it via menu bar and try again')
    else :
        cur.execute('SELECT age,gender FROM Data WHERE user_id=?',(user_id,))
        for item in cur :
            user_age=item[0]
            user_gender=item[1]
        if user_age!=None and user_gender!=None :
            replytext='Select the gender of the user'
            keyboard=[[InlineKeyboardButton('Male',callback_data='ANmale_'+user_id),
                    InlineKeyboardButton('Female',callback_data='ANfemale_'+user_id),
                    InlineKeyboardButton('Others',callback_data='ANothers_'+user_id)]]

            inline_markup=InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=int(user_id),text=replytext,reply_markup=inline_markup)
        else :
            context.bot.send_message(chat_id=update.message.chat.id,text='You need to first specify your age and gender in order to start an anonymous conversation')

def anonymous_button(update,context) :
    query = update.callback_query
    query.answer()
    message=(query.data)[2:]
    contact_gender=message.split('_')[0]
    user_id=message.split('_')[1]
    cur.execute('UPDATE Data SET chat_request=? WHERE user_id=?',(contact_gender,user_id))
    conn.commit()
    cur.execute('SELECT age FROM Data WHERE user_id=?',(user_id,))

    user_age=cur.fetchone()[0]


    cur.execute('SELECT gender FROM Data WHERE user_id=?',(user_id,))

    user_gender=cur.fetchone()[0]


    cur.execute('SELECT user_id FROM Data WHERE contact_id ISNULL and gender=? and age=? and chat_request=?',(contact_gender,user_age,user_gender))
    contact_ids=[item[0] for item in cur]
    try :
        contact_ids.remove(user_id)
    except : pass


    if len(contact_ids)==0 :
        respondtext='You will be connected to a user as soon as we found someone with the information you mentioned'
        query.edit_message_text(text=respondtext)
    else :
        contact_id=contact_ids[np.random.randint(0,len(contact_ids),1)[0]]
        cur.execute('UPDATE Data SET contact_id=? WHERE user_id=?',(int(contact_id),int(user_id)))
        cur.execute('UPDATE Data SET contact_id=? WHERE user_id=?',(int(user_id),int(contact_id)))
        cur.execute('UPDATE Data SET chat_request=NULL WHERE user_id=?',(int(user_id),))
        cur.execute('UPDATE Data SET chat_request=NULL WHERE user_id=?',(int(contact_id),))
        conn.commit()
        txt='Your connection with an anonymous user is made, You can now chat with each other'
        #context.bot.send_message(chat_id=int(user_id),text=txt)
        query.edit_message_text(text=txt)
        context.bot.send_message(chat_id=int(contact_id),text=txt)

def gender_function(update,context) :
    cur.execute('SELECT gender FROM Data WHERE user_id=?',(str(update.message.chat.id),))
    gender=cur.fetchone()[0]
    if gender==None :
        keyboard=[[InlineKeyboardButton('Male',callback_data='setGmale_'+str(update.message.chat.id)),
                InlineKeyboardButton('Female',callback_data='setGfemale_'+str(update.message.chat.id)),
                InlineKeyboardButton('Others',callback_data='setGothers_'+str(update.message.chat.id))]]

        inline_markup=InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.message.chat.id,text='Choose your gender',reply_markup=inline_markup)
    else :
        context.bot.send_message(chat_id=update.message.chat.id,text='You can not change your gender!')

def setgender_button(update,context) :
    query = update.callback_query
    query.answer()
    gender=(query.data)[4:].split('_')[0]
    user_id=(query.data)[4:].split('_')[1]
    cur.execute('UPDATE Data SET gender=? WHERE user_id=?',(gender,user_id))
    conn.commit()
    query.edit_message_text(text='Your gender was successfully set')

def age_function(update,context) :
    user_id=str(update.message.chat.id)
    keyboard=[[InlineKeyboardButton('-20',callback_data='setA-20_'+user_id),
        InlineKeyboardButton('20-30',callback_data='setA20-30_'+user_id),
        InlineKeyboardButton('30-40',callback_data='setA30-40_'+user_id)],
        [InlineKeyboardButton('40-50',callback_data='setA40-50_'+user_id),
        InlineKeyboardButton('50-60',callback_data='setA50-60_'+user_id),
        InlineKeyboardButton('+60',callback_data='setA+60_'+user_id)]]

    inline_markup=InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=update.message.chat.id,text='Choose your age',reply_markup=inline_markup)

def setage_button(update,context) :
    query = update.callback_query
    query.answer()
    age=(query.data)[4:].split('_')[0]
    user_id=(query.data)[4:].split('_')[1]
    cur.execute('UPDATE Data SET age=? WHERE user_id=?',(age,user_id))
    conn.commit()
    query.edit_message_text(text='Your age was successfully set')



start_handler=CommandHandler('start',start_function)
stop_handler=CommandHandler('stop',stop_function)
gender_handler=CommandHandler('setgender',gender_function)
age_handler=CommandHandler('setage',age_function)
myusername_handler=CommandHandler('myusername',myusername_function)
chusername_handler=CommandHandler('chusername',chusername_function)
newchat_handler=CommandHandler('chat',newchat_function)
anonymous_handler=CommandHandler('connectme',anonymous_function)
stopchat_handler=CommandHandler('stopchat',stopchat_function)
message_handler=MessageHandler(Filters.text,message_function)
media_handler=MessageHandler(Filters.photo,media_function)
voice_handler=MessageHandler(Filters.voice,voice_function)
gif_handler=MessageHandler(Filters.document.mime_type("video/mp4"),gif_function)
zip_handler=MessageHandler(Filters.document.mime_type("application/zip"),zip_function)
pdf_handler=MessageHandler(Filters.document.mime_type("application/pdf"),pdf_function)
dice_handler=MessageHandler(Filters.dice,dice_function)
video_handler=MessageHandler(Filters.video,video_function)
image_handler=MessageHandler(Filters.document.category("image"),image_function)
callback_handler=CallbackQueryHandler(button,pattern='conn[ar].*')
callback_genderhandler=CallbackQueryHandler(gender_button,pattern='G[mfos].*')
callback_agehandler=CallbackQueryHandler(age_button,pattern='^Ag.+')
callback_anonymoushandler=CallbackQueryHandler(anonymous_button,pattern='^AN.+')
callback_setgender=CallbackQueryHandler(setgender_button,pattern='^setG.*')
callback_setage=CallbackQueryHandler(setage_button,pattern='^setA.*')


dispatcher.add_handler(start_handler)
dispatcher.add_handler(stop_handler)
dispatcher.add_handler(myusername_handler)
dispatcher.add_handler(chusername_handler)
dispatcher.add_handler(gender_handler)
dispatcher.add_handler(age_handler)
dispatcher.add_handler(newchat_handler)
dispatcher.add_handler(anonymous_handler)
dispatcher.add_handler(stopchat_handler)
dispatcher.add_handler(message_handler)
dispatcher.add_handler(media_handler)
dispatcher.add_handler(voice_handler)
dispatcher.add_handler(gif_handler)
dispatcher.add_handler(zip_handler)
dispatcher.add_handler(pdf_handler)
dispatcher.add_handler(dice_handler)
dispatcher.add_handler(video_handler)
dispatcher.add_handler(image_handler)
dispatcher.add_handler(callback_handler)
dispatcher.add_handler(callback_genderhandler)
dispatcher.add_handler(callback_agehandler)
dispatcher.add_handler(callback_anonymoushandler)

dispatcher.add_handler(callback_setgender)

dispatcher.add_handler(callback_setage)

updater.start_polling()