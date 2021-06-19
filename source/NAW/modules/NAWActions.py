import telebot

from source.NAW.modules.NAWDataBase import NAWDataBase as DBData
from source.NAW.modules.NAWFilesControl import NAWFilesControl as FileData
from source.NAW.modules.NAWStory import NAWStory as Story

db = DBData()


class NAWActions:
    def __init__(self, bot):
        self.__machine__ = bot

    def start_game(self, user_id):
        db.create_user(user_id, Story.get_all_path())
        self.send_text_message(user_id, FileData.get_node(0)[0]['text'], {'step': 0, 'position': 0})

    def shortcut(self,user_id, part):
        if part:
            parts = {1: 0, 2: 16, 3: 39}
            db.create_user(user_id, Story.get_all_path())
            db.upd_data(user_id, {"path":Story.get_all_path().split('|'),'step': parts[int(part)], 'position': 0})
            self.send_text_message(user_id, FileData.get_node(parts[int(part)])[0]['text'], {'step': parts[int(part)], 'position': 0})

    def handle_message(self, user_id, user_message=None, user_data=None):
        if not user_data:
            user_data = db.get_user_data(user_id)
            if user_data == {}:
                self.__machine__.send_message(user_id, 'Для старта игры введите \'/start\'',disable_notification=True,parse_mode='Markdown')
                return
        user_story = Story(user_data['step'], user_data['path'], user_data['position'])
        next_step_data = user_story.user_reaction(user_message)
        if next_step_data != {}:
            if next_step_data['step']==0:
                self.__machine__.send_message(user_id, 'Продолжение следует...',disable_notification=True,
                                              parse_mode='Markdown')
                return

            # dialog handle

            try:
                if next_step_data['text-position']>=0:
                    keymap = telebot.types.ReplyKeyboardMarkup(False, True)
                    dialog_texts = FileData.get_node(str(next_step_data['step']))[0]['text']
                    if next_step_data['text-position']==0:
                        keymap.row(dialog_texts[1])
                        text = dialog_texts[0]
                        db.upd_data(user_id, next_step_data)
                    else:
                        keymap.row(dialog_texts[next_step_data['text-position']+2])
                        text = dialog_texts[next_step_data['text-position']+1]
                    self.__machine__.send_message(user_id,text, reply_markup=keymap, disable_notification=True,parse_mode='Markdown')
                    return
            except KeyError:
                pass

            # main history handle

            db.upd_data(user_id, next_step_data)
            text_step = user_story.get_send_text()
            if text_step == '0':
                self.callback_next(user_id, str(next_step_data['step']) + '.' + str(next_step_data['position']))
            else:
                self.send_text_message(user_id, text_step, next_step_data)
        else:
            self.__machine__.send_sticker(user_id,
                                          'CAACAgIAAxkBAAL51l710Kuq94vM8hLcU3U4hk7vPnWVAAKZAAOVwmUXN_WaFPb-jwUaBA')

    def send_text_message(self, user_id, texts, next_step_data):
        markup = telebot.types.InlineKeyboardMarkup()
        if type(texts) != str:
            markup.add(telebot.types.InlineKeyboardButton(text='←', callback_data='-1'),
                       telebot.types.InlineKeyboardButton(text='1/' + str(len(texts)), callback_data='-1'),
                       telebot.types.InlineKeyboardButton(text='→',
                                                          callback_data=str(next_step_data['step']) + '.' + str(
                                                              next_step_data['position']) + '.1'))
            markup.add(telebot.types.InlineKeyboardButton(text='Далее',
                                                          callback_data=str(next_step_data['step']) + '.' + str(
                                                              next_step_data['position'])))
            self.__machine__.send_message(user_id, text=texts[0], reply_markup=markup,disable_notification=True,parse_mode='Markdown')
        else:
            markup.add(telebot.types.InlineKeyboardButton(text='Далее',
                                                          callback_data=str(next_step_data['step']) + '.' + str(
                                                              next_step_data['position'])))
            self.__machine__.send_message(user_id, text=texts, reply_markup=markup,disable_notification=True,parse_mode='Markdown')

    def callback_next(self, user_id, data, mes_markup = None, mes_id = None):
        step = int(data.split('.')[0])
        position = int(data.split('.')[1])
        user_data = db.get_user_data(user_id)
        if user_data['step'] == step and user_data['position'] == position:
            current_event = FileData.get_node(step, 'story')[position]

            if mes_markup:
                # take away "Далее" btn
                if len(mes_markup) == 3:
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton(text='←', callback_data=mes_markup[0]['callback_data']),
                               telebot.types.InlineKeyboardButton(text=mes_markup[1]['text'], callback_data='-1'),
                               telebot.types.InlineKeyboardButton(text='→',
                                                                  callback_data=mes_markup[2]['callback_data']))
                    self.__machine__.edit_message_reply_markup(user_id, mes_id, reply_markup=markup)
                else:
                    self.__machine__.edit_message_reply_markup(user_id, mes_id)

            if current_event['variants']:
                keymap = telebot.types.ReplyKeyboardMarkup(True, True)
                for variant in current_event['variants']:
                    keymap.row(variant)
                current_texts = FileData.get_node(step)[position]['motive']
                self.__machine__.send_message(user_id, text=current_texts, reply_markup=keymap,disable_notification=True,parse_mode='Markdown')
            else:
                self.handle_message(user_id)

    def callback_pang(self, user_id, mes_id, data,mes_markup):
        cur_page, prev_page, next_page = data.split('.'), data.split('.'), data.split('.')
        texts = FileData.get_node(prev_page[0])[int(prev_page[1])]['text']
        max_len = len(texts)
        if max_len != int(prev_page[2]) - 1:
            prev_page[2] = str(int(prev_page[2]) - 1)
            next_page[2] = str(int(next_page[2]) + 1)
            markup = telebot.types.InlineKeyboardMarkup()
            prev_btn = telebot.types.InlineKeyboardButton(text='←', callback_data=(
                '.'.join(prev_page) if cur_page[2] != '0' else '-1'))
            num_btn = telebot.types.InlineKeyboardButton(text=next_page[2] + '/' + str(max_len), callback_data='-1')
            next_btn = telebot.types.InlineKeyboardButton(text='→', callback_data=(
                '.'.join(next_page) if int(cur_page[2]) != max_len - 1 else '-1'))
            markup.add(prev_btn, num_btn, next_btn)
            if len(mes_markup) == 2:
                markup.add(telebot.types.InlineKeyboardButton(text='Далее',
                                                              callback_data=cur_page[0] + '.' + str(
                                                                  cur_page[1])))
            self.__machine__.edit_message_text(texts[int(cur_page[2])], user_id, mes_id, reply_markup=markup)

    def get_version(self,user_id):
        self.__machine__.send_message(user_id, text=FileData.get_patch(), disable_notification=True, parse_mode='Markdown')