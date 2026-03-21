import os
BOT_TOKEN = os.environ["BOT_TOKEN"]

OWNER_ID = 1384943274917101719  # единственный кто может выдавать валюту

SEEDS = {
    "strawberry": {"name": "Клубника",   "price": 50,   "watering_needed": 3, "emoji": "🍓", "reward": 400},
    "watermelon": {"name": "Арбуз",      "price": 80,   "watering_needed": 5, "emoji": "🍉", "reward": 650},
    "apple":      {"name": "Яблоко",     "price": 60,   "watering_needed": 4, "emoji": "🍎", "reward": 520},
    "grape":      {"name": "Виноград",   "price": 70,   "watering_needed": 4, "emoji": "🍇", "reward": 540},
    "tomato":     {"name": "Помидор",    "price": 30,   "watering_needed": 2, "emoji": "🍅", "reward": 220},
    "carrot":     {"name": "Морковь",    "price": 20,   "watering_needed": 2, "emoji": "🥕", "reward": 200},
    "pumpkin":    {"name": "Тыква",      "price": 90,   "watering_needed": 6, "emoji": "🎃", "reward": 850},
    "cherry":     {"name": "Вишня",      "price": 55,   "watering_needed": 3, "emoji": "🍒", "reward": 420},
    # Экзотические
    "dragon":     {"name": "Драконий фрукт", "price": 500,  "watering_needed": 8,  "emoji": "🐉", "reward": 3000},
    "durian":     {"name": "Дуриан",         "price": 400,  "watering_needed": 7,  "emoji": "🌵", "reward": 2400},
    "mango":      {"name": "Манго",          "price": 300,  "watering_needed": 6,  "emoji": "🥭", "reward": 1800},
    "coconut":    {"name": "Кокос",          "price": 350,  "watering_needed": 7,  "emoji": "🥥", "reward": 2100},
    "passion":    {"name": "Маракуйя",       "price": 450,  "watering_needed": 8,  "emoji": "🌺", "reward": 2700},
    "truffle":    {"name": "Трюфель",        "price": 800,  "watering_needed": 10, "emoji": "🍄", "reward": 5000},
}

GARDENS = {
    "small":  {"name": "Маленький", "slots": 2,  "price": 0,    "emoji": "🌱"},
    "medium": {"name": "Средний",   "slots": 4,  "price": 200,  "emoji": "🌿"},
    "large":  {"name": "Большой",   "slots": 6,  "price": 500,  "emoji": "🌳"},
    "mega":   {"name": "Мега",      "slots": 10, "price": 1200, "emoji": "🏡"},
}

START_COINS = 200
WATERING_CAN_PRICE = 10  # цена лейки
DAILY_REWARD = 100  # монет за ежедневный бонус

# Роли: название, цена, эмодзи (роли должны существовать на сервере с такими же именами)
ROLES = {
    "OLD":         {"price": 1500, "emoji": "✨", "description": "Самый старый игрок клана MKT."},
    "Фермер":  {"price": 3000, "emoji": "🏆", "description": "Легендарный фермер клана."},
    "Exclusive": {"price": 6000, "emoji": "👑", "description": "Легенда сервера."},
}
