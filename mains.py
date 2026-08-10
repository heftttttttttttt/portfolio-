import telebot
from telebot import types
import requests
import time
import os
import random

bot = telebot.TeleBot('')


def get_5shows():
    response = requests.get("https://api.tvmaze.com/search/shows", params={"q": "Horror"})
    
    shows_data = response.json()
    horror5 = []
    
    for item in shows_data:
        show = item["show"]
        genres = show.get("genres", [])
        if "Horror" in genres:
            horror5.append(show)
    
    random.shuffle(horror5)
    random_5 = horror5[:5]
    return format_shows(random_5, "5 случайных фильмов ужасов")


def get_20shows():
    all_shows = []
    seen_ids = set()
    page = 0
    
    while len(all_shows) < 20 and page < 30:
        try:
            response = requests.get(
                "https://api.tvmaze.com/shows", 
                params={"genres": "Horror", "page": page},
                timeout=10
            )
            
            if response.status_code != 200:
                break
                
            data = response.json()
            if not data: 
                break
                
            for show in data:
                genres = show.get("genres", [])
                if "Horror" in genres and show['id'] not in seen_ids:
                    seen_ids.add(show['id'])
                    rating = show.get('rating', {}).get('average', 0) or 0
                    all_shows.append((rating, show))
            
            page += 1
            time.sleep(0.3) 
            
        except Exception as e:
            break
    
    if not all_shows:
        return "Фильмы ужасов не найдены"
    
    all_shows.sort(key=lambda x: x[0], reverse=True)
    top_20 = [show for rating, show in all_shows[:20]]
    
    return format_shows(top_20, f"20 самых популярных фильмов ужасов")


def search_by_year(year):
    all_shows = []
    seen_ids = set()
    page = 0
    
    while page < 30:
        try:
            response = requests.get(
                "https://api.tvmaze.com/shows", 
                params={"genres": "Horror", "page": page},
                timeout=10
            )
            
            if response.status_code != 200:
                break
                
            data = response.json()
            if not data:
                break
                
            for show in data:
                genres = show.get("genres", [])
                if "Horror" in genres and show['id'] not in seen_ids:
                    premiered = show.get('premiered', '')
                    if premiered and premiered[:4] == str(year):
                        seen_ids.add(show['id'])
                        all_shows.append(show)
            
            if len(all_shows) >= 30:
                break
                
            page += 1
            time.sleep(0.3)
            
        except Exception as e:
            break
    
    if not all_shows:
        return f"Фильмы ужасов {year} года не найдены"
    
    all_shows.sort(key=lambda x: x.get('rating', {}).get('average', 0) or 0, reverse=True)
    
    return format_shows(all_shows, f"Фильмы ужасов {year} года")


def format_shows(shows_list, title="Фильмы"):
    if not shows_list:
        return "Список пуст"
    
    result = [f"{title}:"]
    
    for i, show in enumerate(shows_list, 1):
        name = show['name']
        
        rating_value = show['rating']['average']
        if rating_value is None:
            rating = "Нет данных"
        else:
            rating = f"{rating_value}/10"
        
        genres = ', '.join(show['genres'])
        year = show['premiered'][:4] if show.get('premiered') else "Год неизвестен"
        
        result.append(f"{i}. {name} ({year})")
        result.append(f"   Рейтинг: {rating}")
        result.append(f"   Жанры: {genres}")
        result.append("")
    
    return "\n".join(result)


@bot.message_handler(commands=['start'])
def start_command(message):
    start_message = [
        "Какой ваш любимый ужастик? Мой - Хеллуин.",
        "P.S. используйте команды для работы бота /help"
    ]
    bot.send_message(message.chat.id, "\n".join(start_message))


@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = [
        "Доступные команды:",
        "/start - Приветственное сообщение",
        "/5r - 5 случайных фильмов ужасов",
        "/20fav - 20 самых популярных ужастиков",
        "/year - Поиск ужастиков по году выпуска",
        "/help - Показать это сообщение"
    ]
    bot.send_message(message.chat.id, "\n".join(help_text))


@bot.message_handler(commands=['5r'])
def random_5_command(message):
    result = get_5shows()
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['20fav'])
def popular_20_command(message):
    result = get_20shows()
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['year'])
def year_command(message):
    msg = bot.send_message(message.chat.id, "Введите год выпуска (например: 2020):")
    bot.register_next_step_handler(msg, process_year_step)


def process_year_step(message):
    try:
        year = int(message.text)
        if year < 1900 or year > 2025:
            bot.send_message(message.chat.id, "Пожалуйста, введите год от 1900 до 2025")
            return
        result = search_by_year(year)
        bot.send_message(message.chat.id, result)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число")


bot.polling(none_stop=True)