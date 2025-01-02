import telebot
from telebot import types
import json
import os
from datetime import datetime, timedelta
import time
from keep_alive import keep_alive
keep_alive()

# Bot tokeningizni kiritishingiz kerak
bot = telebot.TeleBot('7319299432:AAFckpwgsiXqUKQGE7xmNdBYYct4faZg1ow')

# Foydalanuvchi ma'lumotlari fayli yo'li
user_data_file = 'user_data.json'

# Foydalanuvchi ma'lumotlari fayli mavjudligini ta'minlash
if not os.path.exists(user_data_file):
    with open(user_data_file, 'w') as file:
        json.dump({}, file)



# Foydalanuvchi ma'lumotlarini yangilash funktsiyasi
def update_user_data(user_id, user_name, user_username):
    with open(user_data_file, 'r') as file:
        data = json.load(file)
    if user_id in data:
        data[user_id]['name'] = user_name
        data[user_id]['username'] = user_username
        with open(user_data_file, 'w') as file:
            json.dump(data, file)
        return True
    else:
        return False





# List of admin user IDs (Replace with actual IDs)
admins = [7577190183]

@bot.message_handler(commands=['post'])
def handle_post(message):
    if message.chat.type == 'private' and message.from_user.id in admins:
        bot.reply_to(message, "Iltimos, postingizni yuboring (rasm va sarlavha).")
        bot.register_next_step_handler(message, process_post)
    else:
        bot.reply_to(message, "Kechirasiz, bu buyruq faqat adminlar uchun.")

def process_post(message):
    if message.photo:
        photo = message.photo[-1].file_id
        caption = message.caption if message.caption else "No caption"

        # Send the photo with caption to the channel
        sent_message = bot.send_photo('@Hentay_uz_official', photo, caption=caption)

        # Create inline button
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton('Tomosha Qilish', url='https://t.me/hentay_uz_bot')
        markup.add(button)

        # Edit the message to add the inline button
        bot.edit_message_caption(caption=caption, chat_id=sent_message.chat.id, message_id=sent_message.message_id, reply_markup=markup)

        bot.reply_to(message, "Post jo'natildi.")
    else:
        bot.reply_to(message, "Iltimos, rasm yuboring.")
        bot.register_next_step_handler(message, process_post)







@bot.message_handler(commands=['status'])
def bot_status(message):
    # User ma'lumotlarini yuklash
    with open('user_data.json', 'r') as user_file:
        user_data = json.load(user_file)
    user_count = len(user_data)

    # Anime ma'lumotlarini yuklash
    with open('hentay_data.json', 'r') as anime_file:
        anime_data = json.load(anime_file)
    anime_count = len(anime_data)
    total_episodes = sum(anime['qismi_soni'] for anime in anime_data)

    # Status xabarini tuzish
    status_message = (
        f"📊 Bot statistikalari:\n\n"
        f"👥 Foydalanuvchilar soni: {user_count}\n"
        f"📚 Animeslar soni: {anime_count}\n"
        f"🎥 Jami qismlar soni: {total_episodes}"
    )

    # Xabarni yuborish
    bot.reply_to(message, status_message)




import threading
import time

@bot.message_handler(commands=['reset'])
def reset_premium_time(message):
    if message.from_user.id != admin:
        bot.reply_to(message, "Sizda ushbu komandani ishlatish huquqi yo'q.")
        return

    if message.chat.type != 'private':
        bot.reply_to(message, "Ushbu komanda faqat private chatlarda ishlaydi.")
        return

    bot.reply_to(message, "Premium muddatlarini tiklash jarayoni boshlandi.")

    with open(user_data_file, 'r') as user_file:
        user_data = json.load(user_file)

    for user_id, user_info in user_data.items():
        if user_info.get('prem', False) and user_info['prem_time'] > 0:
            threading.Thread(target=decrease_prem_time, args=(user_id, user_info['prem_time'], user_data)).start()

    bot.reply_to(message, "Barcha premium foydalanuvchilar uchun premium muddatlari davom ettirildi.")

def decrease_prem_time(user_id, prem_time, user_data):
    while prem_time > 0:
        time.sleep(1)
        prem_time -= 1

        with open(user_data_file, 'w') as user_file:
            user_data[user_id]['prem_time'] = prem_time
            json.dump(user_data, user_file, indent=4)

    user_data[user_id]['prem'] = False

    with open(user_data_file, 'w') as user_file:
        json.dump(user_data, user_file, indent=4)

    # Foydalanuvchiga prem tugaganini bildirish
    try:
        bot.send_message(user_id, "Premium muddati tugadi. Qayta olish uchun @BlitzB_admin ga murojaat qiling.")
    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 403:
            bot.send_message(admin[0], f"Foydalanuvchi {user_id} botni blok qilgan. Unga xabar yuborilmadi.")














@bot.message_handler(commands=['add'])
def add_anime(message):
    if message.from_user.id != admin:
        bot.reply_to(message, "Sizda ushbu komandani ishlatish huquqi yo'q.")
        return

    if message.chat.type != 'private':
        bot.reply_to(message, "Ushbu komanda faqat private chatlarda ishlaydi.")
        return

    bot.reply_to(message, "Anime ID sini kiriting:")
    bot.register_next_step_handler(message, process_anime_id)

import json

def process_anime_id(message):
    anime_id = message.text.strip()

    with open('hentay_data.json', 'r') as file:
        anime_data = json.load(file)

    anime = next((item for item in anime_data if item["id"] == int(anime_id)), None)

    if anime:
        bot.reply_to(message, f"Anime nomi: {anime['nomi']}\nQism qo'shmoqchimisiz? (yes/no)\n\n qismini kiritin")
        bot.register_next_step_handler(message, process_add_episode_number, anime, anime_id, anime_data)
    else:
        bot.reply_to(message, "Yangi anime qo'shamizmi? (yes/no)")
        bot.register_next_step_handler(message, process_add_new_anime, anime_id)


def process_add_episode_number(message, anime, anime_id, anime_data):
    try:
        episode_number = int(message.text.strip())
        bot.reply_to(message, "link berin")
        bot.register_next_step_handler(message, process_episode_link, anime, anime_id, episode_number, anime_data)

    except ValueError:
        bot.reply_to(message, "Faqat raqam")
        bot.register_next_step_handler(message, process_add_episode_number, anime, anime_id, anime_data)

def process_episode_link(message, anime, anime_id, episode_number, anime_data):
    link = message.text.strip()
    new_episode = {str(episode_number): str(link)}

    # Add new episode to the anime's existing entries
    anime[str(episode_number)] = link

    with open("hentay_data.json", "w") as file:
        json.dump(anime_data, file, indent=4)

    bot.reply_to(message, f"Qism qoshildi: {episode_number}")



def process_add_new_anime(message, anime_id):
    if message.text.strip().lower() == 'yes':
        bot.reply_to(message, "Anime nomini kiriting:")
        bot.register_next_step_handler(message, process_new_anime_name, anime_id)
    else:
        bot.reply_to(message, "Amal bekor qilindi.")

def process_new_anime_name(message, anime_id):
    anime_name = message.text.strip()
    bot.reply_to(message, "Nechta qism bor?")
    bot.register_next_step_handler(message, process_new_anime_episodes, anime_id, anime_name)

def process_new_anime_episodes(message, anime_id, anime_name):
    episodes = message.text.strip()
    bot.reply_to(message, "Qaysi davlat?")
    bot.register_next_step_handler(message, process_new_anime_country, anime_id, anime_name, episodes)

def process_new_anime_country(message, anime_id, anime_name, episodes):
    country = message.text.strip()
    bot.reply_to(message, "Qaysi til?")
    bot.register_next_step_handler(message, process_new_anime_language, anime_id, anime_name, episodes, country)

def process_new_anime_language(message, anime_id, anime_name, episodes, country):
    language = message.text.strip()
    bot.reply_to(message, "Nechanchi yili chiqqan?")
    bot.register_next_step_handler(message, process_new_anime_year, anime_id, anime_name, episodes, country, language)

def process_new_anime_year(message, anime_id, anime_name, episodes, country, language):
    year = int(message.text.strip())
    bot.reply_to(message, "Janri nima?")
    bot.register_next_step_handler(message, process_new_anime_genre, anime_id, anime_name, episodes, country, language, year)

def process_new_anime_genre(message, anime_id, anime_name, episodes, country, language, year):
    genre = message.text.strip()
    bot.reply_to(message, "Pfp uchun file path kiriting:")
    bot.register_next_step_handler(message, process_new_anime_pfp, anime_id, anime_name, episodes, country, language, year, genre)

def process_new_anime_pfp(message, anime_id, anime_name, episodes, country, language, year, genre):
    pfp = message.text.strip()
    bot.reply_to(message, "Linkni kiriting:")
    bot.register_next_step_handler(message, process_new_anime_link, anime_id, anime_name, episodes, country, language, year, genre, pfp)

def process_new_anime_link(message, anime_id, anime_name, episodes, country, language, year, genre, pfp):
    link = message.text.strip()
    new_anime = {
        "id": int(anime_id),
        "nomi": anime_name,
        "qismi_soni": int(episodes),
        "qismi": int(episodes),
        "davlat": country,
        "tili": language,
        "yili": year,
        "janri": genre,
        "qidirishlar_soni": 0,
        "pfp": pfp,
        "1": link
    }

    with open('hentay_data.json', 'r') as file:
        anime_data = json.load(file)

    anime_data.append(new_anime)

    with open('hentay_data.json', 'w') as file:
        json.dump(anime_data, file, indent=4)

    bot.reply_to(message, "Yangi anime qo'shildi.")



@bot.message_handler(commands=['del'])
def delete_anime(message):
    if message.from_user.id != admin:
        bot.reply_to(message, "Sizda ushbu komandani ishlatish huquqi yo'q.")
        return

    if message.chat.type != 'private':
        bot.reply_to(message, "Ushbu komanda faqat private chatlarda ishlaydi.")
        return

    bot.reply_to(message, "Anime ID sini kiriting:")
    bot.register_next_step_handler(message, process_delete_anime_id)

def process_delete_anime_id(message):
    anime_id = message.text.strip()

    with open('hentay_data.json', 'r') as file:
        anime_data = json.load(file)

    anime = next((item for item in anime_data if item["id"] == int(anime_id)), None)

    if anime:
        anime_info = (
            f"Anime nomi: {anime['nomi']}\n"
            f"Qismlar soni: {anime['qismi_soni']}\n"
            f"Davlat: {anime['davlat']}\n"
            f"Til: {anime['tili']}\n"
            f"Yili: {anime['yili']}\n"
            f"Janri: {anime['janri']}\n"
            f"Qidirishlar soni: {anime['qidirishlar_soni']}\n"
        )
        bot.reply_to(message, f"{anime_info}\nBu animeni o'chirmoqchimisiz? (yes/no)")
        bot.register_next_step_handler(message, confirm_delete_anime, anime_id, anime_data)
    else:
        bot.reply_to(message, "Anime topilmadi.")

def confirm_delete_anime(message, anime_id, anime_data):
    if message.text.strip().lower() == 'yes':
        anime_data = [item for item in anime_data if item["id"] != int(anime_id)]

        with open('hentay_data.json', 'w') as file:
            json.dump(anime_data, file, indent=4)

        bot.reply_to(message, "Anime o'chirildi.")
    else:
        bot.reply_to(message, "Amal bekor qilindi.")





@bot.message_handler(commands=['bankai'])
def bankai_command(message):
    if message.from_user.id != admin:
        bot.reply_to(message, "Sizda ushbu komandani ishlatish huquqi yo'q.")
        return

    if message.chat.type != 'private':
        bot.reply_to(message, "Ushbu komanda faqat private chatlarda ishlaydi.")
        return

    if message.reply_to_message and message.text.strip() != '/bankai':
        bot.reply_to(message, "Iltimos, faqat reply qiling yoki faqat ID kiriting. Ikkisidan birini tanlang.")
        return

    # Agar reply qilingan bo'lsa
    if message.reply_to_message:
        user_id = str(message.reply_to_message.from_user.id)
    else:
        # Agar ID kiritsilgan bo'lsa
        try:
            user_id = message.text.split()[1].strip()
        except IndexError:
            bot.reply_to(message, "Iltimos, foydalanuvchi ID sini kiriting yoki kimdirga reply qiling.")
            return

    # user_data.json faylidan foydalanuvchini o'chirish
    with open(user_data_file, 'r') as file:
        user_data = json.load(file)

    if user_id in user_data:
        user_data.pop(user_id)
        with open(user_data_file, 'w') as file:
            json.dump(user_data, file, indent=4)
        bot.reply_to(message, f"Foydalanuvchi ma'lumotlari o'chirildi: {user_id}")
    else:
        bot.reply_to(message, "Foydalanuvchi ma'lumotlar bazasida topilmadi.")



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id

    if message.chat.type != 'private':
        bot.send_message(chat_id, "Men faqat Private ishlayman.")
        return

    user_id = str(message.from_user.id)

    # user_data.json faylini ochish
    with open(user_data_file, 'r') as file:
        data = json.load(file)

    if user_id in data:
        user_name = data[user_id]['name']
        welcome_message = f"Hush kelibsiz!!! {user_name} 😊"
    else:
        user_name = message.from_user.first_name
        user_username = message.from_user.username
        save_user_data(user_id, user_name, user_username)
        welcome_message = "Hentay botimizga hush kelibsiz, foydalanish uchun pastdagi tugmalardan foydalaning 😊"

    # Kanalga obuna bo'lganligini tekshirish
    channel_id1 = '@hentay_uz_official'
    channel_id2 = '@hentay_uz_chat'
    channel_id3 = '@Anime_chat_aki'
    joined_channel1 = check_user_joined_channel(user_id, channel_id1)
    joined_channel2 = check_user_joined_channel(user_id, channel_id2)
    joined_channel3 = check_user_joined_channel(user_id, channel_id3)

    if joined_channel1 and joined_channel2 and joined_channel3:
        bot.send_message(chat_id, welcome_message)

        # Custom reply keyboard
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        button1 = telebot.types.KeyboardButton('🔍 Hentay izlash')
        button2 = telebot.types.KeyboardButton('🔞 Premium ')
        button3 = telebot.types.KeyboardButton("📚 Malumot")
        button4 = telebot.types.KeyboardButton('💵 Reklama va Homiylik')
        keyboard.row(button1)
        keyboard.row(button2, button3, button4)

        bot.send_message(chat_id, "Iltimos, pastdagi tugmalardan foydalaning:", reply_markup=keyboard)
    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        join_button1 = types.InlineKeyboardButton(text="Kanal", url=f"https://t.me/{channel_id1[1:]}")
        join_button2 = types.InlineKeyboardButton(text="Chat", url=f"https://t.me/{channel_id2[1:]}")
        join_button3 = types.InlineKeyboardButton(text="AKI", url=f"https://t.me/{channel_id3[1:]}")
        confirm_button = types.InlineKeyboardButton(text="✅Tasdiqlash", callback_data="confirm")

        markup.add(join_button1)
        markup.add(join_button3)
        markup.add(join_button2)
        markup.add(confirm_button)

        bot.send_message(chat_id, "Iltimos, foydalanishdan oldin quyidagi kanallarga obuna bo'ling:", reply_markup=markup)

# Check user subscription status
def check_user_joined_channel(user_id, channel_id):
    try:
        chat_member = bot.get_chat_member(channel_id, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except:
        return False

# Save user data function
def save_user_data(user_id, user_name, user_username):
    with open(user_data_file, 'r+') as file:
        data = json.load(file)
        if user_id not in data:
            data[user_id] = {
                'name': user_name,
                'username': user_username,
                'joined_at': time.time(),
                'prem': False,
                'prem_time': 0
            }
            file.seek(0)
            json.dump(data, file, indent=4)


@bot.callback_query_handler(func=lambda call: call.data == "confirm")
def confirm_subscription(call):
    user_id = str(call.from_user.id)
    channel_id1 = '@hentay_uz_official'
    channel_id2 = '@hentay_uz_chat'
    channel_id3 = '@anime_chat_aki'

    joined_channel1 = check_user_joined_channel(user_id, channel_id1)
    joined_channel2 = check_user_joined_channel(user_id, channel_id2)
    joined_channel3 = check_user_joined_channel(user_id, channel_id3)

    if joined_channel1 and joined_channel2 and joined_channel3:
        bot.answer_callback_query(call.id, "Obuna tasdiqlandi. Foydalanishni boshlashingiz mumkin.")
        send_welcome(call.message)  # Foydalanuvchi obuna bo'lgach, /start buyrug'ini qayta chaqirish
    else:
        bot.answer_callback_query(call.id, "Iltimos, Kanallarga obuna bo'ling.")



@bot.message_handler(func=lambda message: message.text == '🔍 Hentay izlash' and message.chat.type == 'private')
def search_anime(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)

    # Kanalga obuna bo'lganligini tekshirish
    channel_id1 = '@hentay_uz_official'
    channel_id2 = '@hentay_uz_chat'


    joined_channel1 = check_user_joined_channel(user_id, channel_id1)
    joined_channel2 = check_user_joined_channel(user_id, channel_id2)

    if joined_channel1 and joined_channel2:
        # Faqat Orqaga tugmasi bilan yangi reply keyboard
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        back_button = telebot.types.KeyboardButton('Orqaga')
        keyboard.add(back_button)
        msg = bot.send_message(chat_id, "Anime kodini kiriting:", reply_markup=keyboard)

        bot.register_next_step_handler(msg, get_anime_by_id)
    else:
        message_text = (
            "Iltimos, ushbu xizmatdan foydalanish uchun ikkala kanalga ham obuna bo'ling:\n"
            f"Kanal 1: {channel_id1}\n"
            f"Kanal 2: {channel_id2}\n"
        )
        bot.send_message(chat_id, message_text)

# Check user subscription status function
def check_user_joined_channel(user_id, channel_id):
    try:
        chat_member = bot.get_chat_member(channel_id, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except:
        return False



def get_anime_by_id(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)

    # Kanalga obuna bo'lganligini tekshirish
    channel_id1 = '@hentay_uz_official'
    channel_id2 = '@hentay_uz_chat'

    joined_channel1 = check_user_joined_channel(user_id, channel_id1)
    joined_channel2 = check_user_joined_channel(user_id, channel_id2)

    if joined_channel1 and joined_channel2:
        # Foydalanuvchi "Orqaga" tugmasini bosdi, qaytish
        if message.text == 'Orqaga':
            go_back(message)
            return

        # Raqamlarni tekshirish
        try:
            anime_id = int(message.text)
        except ValueError:
            bot.send_message(chat_id, "Iltimos, faqat raqam kiriting.")
            bot.register_next_step_handler(message, get_anime_by_id)  # Takrorlash uchun qaytadan registratsiya qilish
            return

        with open('hentay_data.json', 'r') as file:
            data = json.load(file)

        anime = next((item for item in data if item["id"] == anime_id), None)

        if anime:
            anime["qidirishlar_soni"] += 1
            with open('hentay_data.json', 'w') as file:
                json.dump(data, file, indent=4)

            anime_info = (
                f"🎬 Nomi: {anime['nomi']}\n"
                f"🎥 Qismi: {anime['qismi_soni']}\n"
                f"🌍 Davlati: {anime['davlat']}\n"
                f"🇺🇿 Tili: {anime['tili']}\n"
                f"📆 Yili: {anime['yili']}\n"
               
