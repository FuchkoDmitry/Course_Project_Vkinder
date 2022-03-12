import vk_api
from random import randrange
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from data import cities, sex, relation, sex_reverse, relation_reverse
import re
from user_api import find_users, get_photos_for_founded_users, vk_user_session
from db import Users, add_user_to_db, Base, engine, clear_table, lines_count
from datetime import datetime
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


def upload_photos_in_chat_2(user_photos, text, counter=0):

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text.lower()
            uid = event.user_id
            if text == 'start' or text == 'next' or text == 'search' or text == 'go':
                if len(user_photos) == 0:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.NEGATIVE)
                    write_message(uid, message='список закончился, для начала нового поиска нажмите TRY AGAIN',
                                  keyboard=keyboard)

                    return bot_logic()

                for user_id, photos in user_photos.items():
                    user_link = f'https://vk.com/id{user_id}'
                    name, surname = get_fullname(user_id)
                    keyboard = VkKeyboard(one_time=False, inline=True)
                    keyboard.add_openlink_button('перейти на страницу пользователя', user_link)
                    write_message(user_id=uid, message=f'{surname} {name}', keyboard=keyboard)
                    add_user_to_db(user_id)
                    print(f'{user_id} добавлен в БД')
                    print(user_id, photos)
                    for photo in photos:
                        photo_bytes = requests.get(photo[1]).content
                        photo_object = BytesIO(photo_bytes)
                        try:
                            response = upload.photo_messages(photo_object)[0]
                        except Exception:
                            print('error', photo)
                            continue
                        owner_id = response['owner_id']
                        photo_id = response['id']
                        access_key = response['access_key']
                        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                        write_message(user_id=uid, attachment=attachment)

                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                    write_message(user_id=uid, message='next далее', keyboard=keyboard)
                    del user_photos[user_id]
                    upload_photos_in_chat_2(user_photos, text, counter=counter)

            elif text == 'exit':
                write_message(user_id=uid, message='для начала нового поиска нажмите start')
                return start_bot(text)


# def upload_photos_in_chat(photos, text, counter=0):
#
#     for event in longpoll.listen():
#         if event.type == VkEventType.MESSAGE_NEW and event.to_me:
#             text = event.text.lower()
#             uid = event.user_id
#             if text == 'start' or text == 'next' or text == 'search' or text == 'go':
#                 try:
#
#                     user_link = f'https://vk.com/id{photos[counter][0]}'
#                     name, surname = get_fullname(photos[counter][0])
#                     keyboard = VkKeyboard(one_time=False, inline=True)
#                     keyboard.add_openlink_button('перейти на страницу пользователя', user_link)
#                     write_message(user_id=uid, message=f'{surname} {name}', keyboard=keyboard)
#                     add_user_to_db(photos[counter][0])
#                     print(f'{photos[counter][0]} добавлен в БД')
#
#                     for photo in photos[counter][1]:
#                         write_message(user_id=uid, attachment=photo)
#                     counter += 1
#
#
#                     keyboard = VkKeyboard(one_time=True)
#                     keyboard.add_button('NEXT', color=VkKeyboardColor.POSITIVE)
#                     keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
#                     write_message(user_id=uid, message='next далее', keyboard=keyboard)
#                     upload_photos_in_chat(photos, text, counter=counter)
#                 except IndexError:
#                     keyboard = VkKeyboard(one_time=True)
#                     keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.NEGATIVE)
#                     write_message(uid, message='список закончился, для начала нового поиска нажмите TRY AGAIN',
#                                   keyboard=keyboard)
#
#                     return bot_logic()
#
#             elif text == 'exit':
#                 write_message(user_id=uid, message='для начала нового поиска нажмите start')
#                 return start_bot(text)


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
                    write_message(user_id=uid, message='instruction')
                else:
                    write_message(user_id=uid, message='dont understand message')


def bot_logic():

    search_parameters = dict()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                text = event.text.lower()
                uid = event.user_id
                name, surname = get_fullname(uid)

                if text in sex:
                    # search_parameters = dict()
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
                    search_parameters['hometown'] = text
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('SEARCH', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_line()
                    keyboard.add_button('MENU', color=VkKeyboardColor.NEGATIVE)
                    keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.PRIMARY)
                    write_message(uid, f"{name}, твои критерии поиска:\n пол - "
                                       f"{sex_reverse[search_parameters['sex']].title()}.\n"
                                       f"Возраст - {search_parameters['age_from']}.\n Семейное положение - "
                                       f"{relation_reverse[search_parameters['status']].title()}.\n"
                                       f"Город - {search_parameters['hometown'].capitalize()}.\n "
                                       f"Если все верно нажимай 'SEARCH', если нет - 'TRY AGAIN'.\n 'MENU' для выхода "
                                       f"в главное меню ", keyboard)

                elif text == 'search':
                    write_message(uid, f'{name} идет поиск... Это займет некоторое время.')

                    if len(search_parameters) > 0:
                        search_parameters['offset'] = lines_count(Users) + 20
                        print(search_parameters)
                        print(datetime.now())
                        users_list = find_users(**search_parameters)
                        print(datetime.now(), 'find_users done')

                        if not users_list:
                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.POSITIVE)
                            write_message(uid,
                                          message=f'{name}, поиск не дал результатов, '
                                                  f'нажми TRY AGAIN для нового поиска', keyboard=keyboard)
                        else:
                            users_photos = get_photos_for_founded_users(users_list)
                            print(datetime.now(), 'get_photos_for_founded_users done')
                            # founded_users = give_photos_to_user(users_photos)
                            print(datetime.now(), 'give_photos to user done')
                            # offset = len(founded_users)
                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button('GO', color=VkKeyboardColor.POSITIVE)
                            write_message(uid, f'{name}, поиск завершен, жми GO для просмотра. '
                                               f'Найдено {len(users_photos)} пользователей', keyboard=keyboard)
                            upload_photos_in_chat_2(users_photos, text)

                            # upload_photos_in_chat(founded_users, text, counter=0)
                            print(datetime.now())

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


