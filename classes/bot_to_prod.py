from db import Users, clear_table
from group_api import write_message, get_fullname
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from group_api import vk_group_session
import re
from user_api import find_users, get_photos_for_founded_users, give_photos_to_user
from data import cities, sex, relation, sex_reverse, relation_reverse


longpoll = VkLongPoll(vk_group_session)


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
                        users_list = find_users(**search_parameters)

                        if not users_list:
                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.POSITIVE)
                            write_message(uid,
                                          message=f'{name}, поиск не дал результатов, '
                                                  f'нажми TRY AGAIN для нового поиска', keyboard=keyboard)
                        else:
                            users_photos = get_photos_for_founded_users(users_list)
                            founded_users = give_photos_to_user(users_photos)
                            # offset = len(founded_users)
                            keyboard = VkKeyboard(one_time=True)
                            keyboard.add_button('GO', color=VkKeyboardColor.POSITIVE)
                            write_message(uid, f'{name}, поиск завершен, жми GO для просмотра. '
                                               f'Найдено {len(founded_users)} пользователей', keyboard=keyboard)
                            upload_photos_in_chat(founded_users, text, counter=0)

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