import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

SEEDS = {
    "strawberry": {"name": "Клубника",  "price": 50,  "watering_needed": 3, "emoji": "🍓", "reward": 150},
    "watermelon": {"name": "Арбуз",     "price": 80,  "watering_needed": 5, "emoji": "🍉", "reward": 300},
    "apple":      {"name": "Яблоко",    "price": 60,  "watering_needed": 4, "emoji": "🍎", "reward": 200},
    "grape":      {"name": "Виноград",  "price": 70,  "watering_needed": 4, "emoji": "🍇", "reward": 250},
    "tomato":     {"name": "Помидор",   "price": 30,  "watering_needed": 2, "emoji": "🍅", "reward": 100},
    "carrot":     {"name": "Морковь",   "price": 20,  "watering_needed": 2, "emoji": "🥕", "reward": 80},
    "pumpkin":    {"name": "Тыква",     "price": 90,  "watering_needed": 6, "emoji": "🎃", "reward": 350},
    "cherry":     {"name": "Вишня",     "price": 55,  "watering_needed": 3, "emoji": "🍒", "reward": 170},
}

GARDENS = {
    "small":  {"name": "Маленький", "slots": 2,  "price": 0,    "emoji": "🌱"},
    "medium": {"name": "Средний",   "slots": 4,  "price": 200,  "emoji": "🌿"},
    "large":  {"name": "Большой",   "slots": 6,  "price": 500,  "emoji": "🌳"},
    "mega":   {"name": "Мега",      "slots": 10, "price": 1200, "emoji": "🏡"},
}

START_COINS = 200
WATERING_CAN_PRICE = 50
DAILY_REWARD = 100  # монет за ежедневный бонус

# Роли: название, цена, эмодзи (роли должны существовать на сервере с такими же именами)
ROLES = {
    "OLD":         {"price": 1500, "emoji": "✨", "description": "Самый старый игрок клана MKT."},
    "Dungeon Master":  {"price": 3000, "emoji": "🏆", "description": "Мастер своего дела"},
    "Exclusive": {"price": 6000, "emoji": "👑", "description": "Легенда сервера"},
}
