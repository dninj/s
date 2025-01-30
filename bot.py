import telebot
from config import *
from logic import *
import os
import os
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, """
Доступные команды:
/show_city <название_города> - Показать город на карте.
/remember_city <название_города> - Запомнить город.
/show_my_cities - Показать все запомненные города на карте.
""")


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    city_name = message.text.split(maxsplit=1)[1:] # корректное получение названия города
    if not city_name:
        bot.send_message(message.chat.id, "Введите название города после команды /show_city")
        return

    city_name = city_name[0] # извлечение строки из списка
    coordinates = manager.get_coordinates(city_name)
    if coordinates:
        manager.create_graph("single_city_map.png", [city_name])
        with open("single_city_map.png", "rb") as map_file:
            bot.send_photo(message.chat.id, map_file)
        os.remove("single_city_map.png") # удаляем временный файл
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split(maxsplit=1)[1:] # корректное получение названия города
    if not city_name:
        bot.send_message(message.chat.id, "Введите название города после команды /remember_city")
        return
    city_name = city_name[0] # извлечение строки из списка

    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    if cities:
        manager.create_graph("my_cities_map.png", cities)
        with open("my_cities_map.png", "rb") as map_file:
            bot.send_photo(message.chat.id, map_file)
        os.remove("my_cities_map.png") # удаляем временный файл

    else:
        bot.send_message(message.chat.id, "Вы еще не добавили ни одного города.")



if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    manager.create_user_table() # Создаем таблицу при запуске бота
    bot.polling()



bot = telebot.TeleBot(TOKEN)

# ... (Функции обработчики команд остаются без изменений) ...

class DB_Map():
    def __init__(self, database): # Исправлено: init -> __init__
        self.database = database

    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return True # Возвращаем True/False для большей ясности
            else:
                return False

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city
                            FROM users_cities
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, path, cities):
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, alpha=0.5)
        ax.add_feature(cfeature.RIVERS)

        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                ax.plot(lng, lat, 'ro', markersize=5, transform=ccrs.Geodetic())
                ax.text(lng + 0.5, lat + 0.5, city, transform=ccrs.Geodetic())

        # Определение границ карты по координатам городов (с небольшим отступом)
        if cities: # Проверка, что список городов не пуст
            lats = [self.get_coordinates(city)[0] for city in cities if self.get_coordinates(city)]
            lngs = [self.get_coordinates(city)[1] for city in cities if self.get_coordinates(city)]

            if lats and lngs: # Проверка, что списки координат не пусты
                ax.set_extent([min(lngs) - 2, max(lngs) + 2, min(lats) - 2, max(lats) + 2], crs=ccrs.PlateCarree())

        plt.savefig(path)
        plt.close()


if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    manager.create_user_table()
    bot.polling()    




