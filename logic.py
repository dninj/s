import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.img_tiles as img_tiles

class DB_Map():
    def __init__(self, database):
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

    def add_city(self,user_id, city_name ):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0


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
                ax.text(lng + 0.5, lat + 0.5, city, transform=ccrs.Geodetic()) # +0.5 для смещения текста

        # Определение границ карты по координатам городов (с небольшим отступом)
        if cities: # Проверка, что список городов не пуст
            lats = [self.get_coordinates(city)[0] for city in cities if self.get_coordinates(city)]
            lngs = [self.get_coordinates(city)[1] for city in cities if self.get_coordinates(city)]

            if lats and lngs: # Проверка, что списки координат не пусты
                ax.set_extent([min(lngs) - 2, max(lngs) + 2, min(lats) - 2, max(lats) + 2], crs=ccrs.PlateCarree())

        plt.savefig(path)
        plt.close() # Закрываем plot после сохранения


    def draw_distance(self, city1, city2):
        pass


if __name__ == "__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
    # Пример использования:
    user_id = 12345
    cities_to_add = ["Moscow", "London", "New York", "Tokyo"]
    for city in cities_to_add:
      m.add_city(user_id, city)
    selected_cities = m.select_cities(user_id)
    m.create_graph("my_map.png", selected_cities)




class DB_Map():
    def __init__(self, database):
        self.database = database

    # ... (остальные методы без изменений) ...


    def create_graph(self, path, cities, marker_color='ro', background_type='default'):
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        if background_type == 'default':
            ax.add_feature(cfeature.LAND)
            ax.add_feature(cfeature.OCEAN)
            ax.add_feature(cfeature.COASTLINE)
            ax.add_feature(cfeature.BORDERS, linestyle=':')
            ax.add_feature(cfeature.LAKES, alpha=0.5)
            ax.add_feature(cfeature.RIVERS)
        elif background_type == 'image':
            request = img_tiles.StamenTerrain() #можно использовать другие источники карт
            ax.add_image(request, 8)

        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                ax.plot(lng, lat, marker_color, markersize=5, transform=ccrs.Geodetic())
                ax.text(lng + 0.5, lat + 0.5, city, transform=ccrs.Geodetic())

        if cities:
            lats = [self.get_coordinates(city)[0] for city in cities if self.get_coordinates(city)]
            lngs = [self.get_coordinates(city)[1] for city in cities if self.get_coordinates(city)]
            if lats and lngs:
                ax.set_extent([min(lngs) - 2, max(lngs) + 2, min(lats) - 2, max(lats) + 2], crs=ccrs.PlateCarree())

        plt.savefig(path)
        plt.close()


    def draw_distance(self, city1, city2):
        pass



if __name__ == "__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()
    # Пример использования:
    user_id = 12345
    cities_to_add = ["Moscow", "London", "New York", "Tokyo"]
    for city in cities_to_add:
      m.add_city(user_id, city)
    selected_cities = m.select_cities(user_id)
    # пример использования с выбором цвета маркера и фоном карты
    m.create_graph("my_map.png", selected_cities, marker_color='go', background_type='image')    