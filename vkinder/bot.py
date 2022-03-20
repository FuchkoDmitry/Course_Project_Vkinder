from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import re
from vkinder.user import find_users, get_photos_for_founded_users, vk_user_session
from data import cities, sex, relation, sex_reverse, relation_reverse
from vkinder.db import Users, add_user_to_db, create_tables, add_to_favorites, add_to_blacklist,\
    lines_count, get_users_in_table, Favorites, BlackList, delete_from_blacklist, delete_from_favorites
from vkinder.group import write_message, get_fullname, vk_group_session
import requests
from io import BytesIO
from vk_api.upload import VkUpload


longpoll = VkLongPoll(vk_group_session)
upload = VkUpload(vk_user_session)


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
                    keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.SECONDARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                    write_message(user_id=uid, message='next далее, exit в главное меню, '
                                                       'try again изменить параметры поиска ', keyboard=keyboard)

                    bot_logic_advanced(user_photos, text, attachments=attachments, user_id=user_id)

            elif text == 'favorite':
                if add_to_favorites(uid, user_id, ','.join(attachments)):
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.SECONDARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                    write_message(user_id=uid, message='пользователь добавлен в избранное. '
                                                       'Next далее, exit в главное меню, '
                                                       'try again изменить параметры поиска ', keyboard=keyboard)
                else:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.SECONDARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                    write_message(user_id=uid, message='пользователь был добавлен в избранное ранее. '
                                                       'Next далее, exit в главное меню,'
                                                       ' try again изменить параметры поиска ', keyboard=keyboard)
                del user_photos[user_id]
                bot_logic_advanced(user_photos, text)

            elif text == 'blacklist':
                if add_to_blacklist(uid, user_id, ','.join(attachments)):
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('TRY AGAIN', color=VkKeyboardColor.SECONDARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                    write_message(user_id=uid, message='пользователь добавлен в черный список. '
                                                       'Next далее, exit в главное меню,'
                                                       ' try again изменить параметры поиска ', keyboard=keyboard)
                else:
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.SECONDARY)
                    write_message(user_id=uid, message='пользователь добавлен в черный список ранее. '
                                                       'Next далее, exit в главное меню,'
                                                       ' try again изменить параметры поиска ', keyboard=keyboard)
                del user_photos[user_id]
                bot_logic_advanced(user_photos, text)

            elif text == 'try again':
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Мужской', color=VkKeyboardColor.NEGATIVE)
                keyboard.add_button('Женский', color=VkKeyboardColor.SECONDARY)
                write_message(uid, 'выбери пол: ', keyboard)
                bot_logic()

            elif text == 'exit':
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('START', color=VkKeyboardColor.POSITIVE)
                keyboard.add_line()
                keyboard.add_button('FAVORITES', color=VkKeyboardColor.PRIMARY)
                keyboard.add_button('BLACKLISTED', color=VkKeyboardColor.NEGATIVE)
                write_message(user_id=uid, message='для начала нового поиска нажмите start, '
                                                   'favorites - посмотреть избранное, '
                                                   'blacklisted - посмотреть черный список')
                return start_bot(text)


def start_bot(text=None, users_list=None, count=-1, user_id=None):
    # create_tables(Users)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:

            if event.to_me:
                text = event.text.lower()
                uid = event.user_id

                name, surname = get_fullname(uid)

                if text == 'start' or text == 'try again':
                    if text == 'start':
                        create_tables(Users)
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('Мужской', color=VkKeyboardColor.NEGATIVE)
                    keyboard.add_button('Женский', color=VkKeyboardColor.SECONDARY)
                    write_message(uid, f'Привет {name} {surname}, выбери пол: ', keyboard)
                    bot_logic()
                elif text == 'exit':
                    write_message(user_id=uid, message=f'Пока {name}. Возвращайся.')

                elif text == 'help':
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('START', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_line()
                    keyboard.add_button('FAVORITES', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('BLACKLISTED', color=VkKeyboardColor.NEGATIVE)
                    write_message(user_id=uid, message='start - начать. exit выход. '
                                                       'favorites - посмотреть избранное. '
                                                       'blacklisted - посмотреть черный список')

                elif text == 'favorites' or text == 'next':
                    favorites = get_users_in_table(Favorites, uid)

                    try:
                        count += 1
                        user_link = f'https://vk.com/id{favorites[count].favorite_id}'
                        name, surname = get_fullname(favorites[count].favorite_id)
                        keyboard = VkKeyboard(one_time=False, inline=True)
                        keyboard.add_openlink_button('перейти на страницу пользователя', user_link)
                        write_message(user_id=uid, message=f'{surname} {name}', keyboard=keyboard)
                        for photo in favorites[count].photos_list.split(','):
                            write_message(user_id=uid, attachment=photo)
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('NEXT', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('DELETE', color=VkKeyboardColor.PRIMARY)
                        keyboard.add_line()
                        keyboard.add_button('START', color=VkKeyboardColor.SECONDARY)
                        keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                        write_message(uid, 'NEXT - далее, DELETE - удалить из избранного, EXIT - выход, '
                                           'START - начать новый поиск', keyboard)
                        start_bot(count=count, user_id=favorites[count].favorite_id)
                    except IndexError:
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('START', color=VkKeyboardColor.SECONDARY)
                        keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                        write_message(uid, 'пользователи в избранном закончились, EXIT - выход, '
                                           'START - начать новый поиск', keyboard)
                        start_bot()
                    except TypeError:
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('START', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('HELP', color=VkKeyboardColor.SECONDARY)
                        write_message(uid, 'в избранном никого нет, start - начать новый поиск, help - помощь',
                                      keyboard)

                elif text == 'blacklisted' or text == 'bl next':
                    blacklisted = get_users_in_table(BlackList, uid)

                    try:
                        count += 1
                        user_link = f'https://vk.com/id{blacklisted[count].blacklisted_user_id}'
                        name, surname = get_fullname(blacklisted[count].blacklisted_user_id)
                        keyboard = VkKeyboard(one_time=False, inline=True)
                        keyboard.add_openlink_button('перейти на страницу пользователя', user_link)
                        write_message(user_id=uid, message=f'{surname} {name}', keyboard=keyboard)
                        for photo in blacklisted[count].photos_list.split(','):
                            write_message(user_id=uid, attachment=photo)
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('BL NEXT', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('BL DELETE', color=VkKeyboardColor.PRIMARY)
                        keyboard.add_line()
                        keyboard.add_button('START', color=VkKeyboardColor.SECONDARY)
                        keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                        write_message(uid, 'BL NEXT - далее, BL DELETE - удалить из избранного, EXIT - выход, '
                                           'START - начать новый поиск', keyboard)

                        start_bot(count=count, user_id=blacklisted[count].blacklisted_user_id)
                    except IndexError:
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('START', color=VkKeyboardColor.SECONDARY)
                        keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                        write_message(uid, 'пользователи в черном списке закончились, EXIT - выход, '
                                           'START - начать новый поиск', keyboard)
                        start_bot()
                    except TypeError:
                        keyboard = VkKeyboard(one_time=True)
                        keyboard.add_button('START', color=VkKeyboardColor.POSITIVE)
                        keyboard.add_button('HELP', color=VkKeyboardColor.SECONDARY)
                        write_message(uid, 'в черном списке никого нет, start - начать новый поиск, help - помощь',
                                      keyboard)

                elif text == 'bl delete':
                    delete_from_blacklist(uid, user_id)
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('BL NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_line()
                    keyboard.add_button('START', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                    write_message(uid, 'Пользователь удален из черного списка. BL NEXT - далее, '
                                           'EXIT - выход, START - начать новый поиск', keyboard)
                    start_bot(count=count)

                elif text == 'delete':
                    delete_from_favorites(uid, user_id)
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('NEXT', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_line()
                    keyboard.add_button('START', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                    write_message(uid, 'Пользователь удален из избранного. NEXT - далее, '
                                       'EXIT - выход, START - начать новый поиск', keyboard)
                    start_bot()

                else:
                    write_message(user_id=uid, message='Я тебя не понимаю. нажми start'
                                                       ' и мы начнем или help для помощи')


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
                    try:
                        write_message(uid, f"{name}, твои критерии поиска:\n пол - "
                                           f"{sex_reverse[search_parameters['sex']].title()}.\n"
                                           f"Возраст - {search_parameters['age_from']}.\n Семейное положение - "
                                           f"{relation_reverse[search_parameters['status']].title()}.\n"
                                           f"Город - {search_parameters['hometown'].title()}.\n "
                                           f"Если все верно нажимай 'SEARCH', если нет - 'TRY AGAIN'.\n "
                                           f"'MENU' для выхода "
                                           f"в главное меню ", keyboard)
                    except KeyError:
                        write_message(uid, 'SEARCH - начать поиск, MENU - вернуться в главное меню,'
                                           ' TRY AGAIN - изменить параметры поиска', keyboard)

                elif text == 'search':
                    write_message(uid, f'{name} идет поиск... Это займет некоторое время.')

                    if len(search_parameters) > 0:
                        search_parameters['offset'] = lines_count(Users)
                        users_list = find_users(user_id=uid, **search_parameters)

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
                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button('START', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('EXIT', color=VkKeyboardColor.NEGATIVE)
                    keyboard.add_button('HELP', color=VkKeyboardColor.SECONDARY)
                    keyboard.add_line()
                    keyboard.add_button('FAVORITES', color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button('BLACKLISTED', color=VkKeyboardColor.SECONDARY)
                    write_message(uid, 'start- начать, help- помощь, exit- выход, '
                                       'favorites - посмотреть избранное, blacklisted - посмотреть ЧС', keyboard)
                    start_bot()
                else:
                    write_message(uid, message='я тебя не понял, попробуй еще раз, menu для информации')
