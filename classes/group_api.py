import vk_api
from random import randrange
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from data import cities, sex, relation, sex_reverse, relation_reverse
import re
from user_api import find_users, get_photos_for_founded_users, vk_user_session
from db import Users, add_user_to_db, clear_table, add_to_favorites, add_to_blacklist

import requests
from io import BytesIO
from vk_api.upload import VkUpload


GROUP_TOKEN = '242ccb4880c150584eaa54371361c18bff724d7969d0705af912250f3b2468ec7d71eb23a50ec38aedf75'

vk_group_session = vk_api.VkApi(token=GROUP_TOKEN)
vk = vk_group_session.get_api()
longpoll = VkLongPoll(vk_group_session)
upload = VkUpload(vk_user_session)


def write_message(user_id=None, message=None, keyboard=None, attachment=None):
    post = {'user_id': user_id,
            'random_id': randrange(10 ** 7),
            }
    if message:
        post['message'] = message

    if keyboard:
        post['keyboard'] = keyboard.get_keyboard()

    if attachment:
        post['attachment'] = attachment

    vk_group_session.method('messages.send', post)


def get_fullname(user_id):
    request = vk_group_session.method('users.get', values={'user_ids': user_id})[0]
    first_name = request['first_name']
    last_name = request['last_name']
    return first_name, last_name


def bot_logic_advanced(user_photos, text, attachments=None, user_id=None):

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text.lower()
            uid = event.user_id
            if text == 'start' or text == 'next' or text == 'search' or text == 'go':
                if user_id:
                    del user_photos[user_id]
                if len(user_photos) == 0:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.NEGATIVE)
                    write_message(uid, message='список закончился, для начала нового поиска нажмите TRY AGAIN',
                                  keyboard=keyboard)
                    return bot_logic()

                for user_id, photos in user_photos.items():
                    user_link = f'https://vk.com/id{user_id}'
                    attachments = []
                    name, surname = get_fullname(user_id)
                    keyboard = VkKeyboard(one_time=False, inline=True)
                    keyboard.add_openlink_button('перейти на страницу пользователя', user_link)
                    write_message(user_id=uid, message=f'{surname} {name}', keyboard=keyboard)
                    add_user_to_db(user_id)

                    for photo in photos:
                        photo_bytes = requests.get(photo[1]).content
                        photo_object = BytesIO(photo_bytes)
                        try:
                            response = upload.photo_messages(photo_object)[0]
                        except Exception:
                            continue
                        owner_id = response['owner_id']
                        photo_id = response['id']
                        access_key = response['access_key']
                        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                        write_message(user_id=uid, attachment=attachment)
                        attachments.append(attachment)

                    keyboard = VkKeyboard(one_time=False, inline=True)
                    keyboard.add_button('FAVORITE', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('BLACKLIST', color=VkKeyboardColor.NEGATIVE)
                    write_message(uid, 'FAVORITE - в избранное, BLACKLIST - в чс', keyboard)

                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.SECONDARY)
                    write_message(user_id=uid, message='next далее, ', keyboard=keyboard)

                    bot_logic_advanced(user_photos, text, attachments=attachments, user_id=user_id)

            elif text == 'favorite':
                if add_to_favorites(uid, user_id, ','.join(attachments)):
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.SECONDARY)
                    write_message(user_id=uid, message='пользователь добавлен в избранное. '
                                                       'Next далее', keyboard=keyboard)
                else:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.SECONDARY)
                    write_message(user_id=uid, message='пользователь был добавлен в избранное ранее. '
                                                       'Next далее', keyboard=keyboard)
                del user_photos[user_id]
                bot_logic_advanced(user_photos, text)

            elif text == 'blacklist':
                if add_to_blacklist(uid, user_id):
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.SECONDARY)
                    write_message(user_id=uid, message='пользователь добавлен в черный список. '
                                                       'Next далее', keyboard=keyboard)
                else:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.SECONDARY)
                    write_message(user_id=uid, message='пользователь уже был в черном списке. '
                                                       'Next далее', keyboard=keyboard)
                del user_photos[user_id]
                bot_logic_advanced(user_photos, text)

            elif text == 'exit':
                write_message(user_id=uid, message='для начала нового поиска нажмите start')
                return start_bot(text)


def start_bot(text=None):
    clear_table(Users)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                text = event.text.lower()
                uid = event.user_id

                name, surname = get_fullname(uid)

                if text == 'start' or text == 'try again':
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Мужской', color=VkKeyboardColor.NEGATIVE)
                    keyboard.add_button('Женский', color=VkKeyboardColor.SECONDARY)
                    write_message(uid, f'Привет {name} {surname}, выбери пол: ', keyboard)
                    bot_logic()
                elif text == 'exit':
                    write_message(user_id=uid, message=f'Пока {name}. Возвращайся.')

                elif text == 'help':
                    write_message(user_id=uid, message='start - начать. exit выход.')
                else:
                    write_message(user_id=uid, message='Я тебя не понимаю. нажми start и мы начнем или help для помощи')


def bot_logic():

    search_parameters = dict()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                text = event.text.lower()
                uid = event.user_id
                name, surname = get_fullname(uid)

                if text in sex:
                    search_parameters['sex'] = sex[text]
                    write_message(uid, f'{name}, введи возраст:')

                elif re.search(r'^[0-9]{1,3}', text):
                    if int(text) > 18:
                        search_parameters['age_from'] = int(text)
                        search_parameters['age_to'] = int(text) + 1
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('замужем/женат', color=VkKeyboardColor.NEGATIVE)
                        keyboard.add_button('не замужем/не женат', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_line()
                        keyboard.add_button('есть друг/есть подруга', color=VkKeyboardColor.SECONDARY)
                        keyboard.add_button('В активном поиске', color=VkKeyboardColor.PRIMARY)
                        write_message(uid, f'{name}, выбери семейное положение: ', keyboard)
                    else:
                        write_message(uid, f'{name}, введите возраст больше 18 лет: ')

                elif text in relation:
                    search_parameters['status'] = relation[text]
                    write_message(uid, 'введи город поиска:')

                elif text in cities:
                    search_parameters['hometown'] = text.title()
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('SEARCH', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_line()
                    keyboard.add_button('MENU', color=VkKeyboardColor.NEGATIVE)
                    keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.PRIMARY)
                    write_message(uid, f"{name}, твои критерии поиска:\n пол - "
                                       f"{sex_reverse[search_parameters['sex']].title()}.\n"
                                       f"Возраст - {search_parameters['age_from']}.\n Семейное положение - "
                                       f"{relation_reverse[search_parameters['status']].title()}.\n"
                                       f"Город - {search_parameters['hometown'].title()}.\n "
                                       f"Если все верно нажимай 'SEARCH', если нет - 'TRY AGAIN'.\n 'MENU' для выхода "
                                       f"в главное меню ", keyboard)

                elif text == 'search':
                    write_message(uid, f'{name} идет поиск... Это займет некоторое время.')

                    if len(search_parameters) > 0:
                        # search_parameters['offset'] = lines_count(Users) + 20
                        users_list = find_users(**search_parameters)

                        if not users_list:
                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.POSITIVE)
                            write_message(uid,
                                          message=f'{name}, поиск не дал результатов, '
                                                  f'нажми TRY AGAIN для нового поиска', keyboard=keyboard)
                        else:
                            users_photos = get_photos_for_founded_users(users_list)
                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button('GO', color=VkKeyboardColor.POSITIVE)
                            write_message(uid, f'{name}, поиск завершен, жми GO для просмотра. '
                                               f'Найдено {len(users_photos)} пользователей', keyboard=keyboard)
                            bot_logic_advanced(users_photos, text)

                    else:
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('Мужской', color=VkKeyboardColor.NEGATIVE)
                        keyboard.add_button('Женский', color=VkKeyboardColor.SECONDARY)
                        write_message(uid, f'{name}, не выбраны критерии поиска, выбери пол:', keyboard)

                elif text == 'try again' or text == 'start':
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Мужской', color=VkKeyboardColor.NEGATIVE)
                    keyboard.add_button('Женский', color=VkKeyboardColor.SECONDARY)
                    write_message(uid, f'Привет{name} {surname}, выбери пол: ', keyboard)

                elif text == 'menu':
                    write_message(uid, message='start- начать, help- помощь, exit- выход')
                    start_bot()

                else:
                    write_message(uid, message='я тебя не понял, попробуй еще раз, menu для информации')


if __name__ == "__main__":
    start_bot()


