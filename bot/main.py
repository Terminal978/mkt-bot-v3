import discord
from discord.ext import commands
import asyncio
import traceback
from config import BOT_TOKEN
from database import init_db

print("=== Бот запускается ===", flush=True)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await init_db()
    await bot.load_extension("cogs.shop")
    await bot.load_extension("cogs.garden")
    await bot.load_extension("cogs.inventory")
    await bot.load_extension("cogs.roles")
    await bot.load_extension("cogs.admin")
    synced = await bot.tree.sync()
    print(f"✅ Бот запущен: {bot.user} | Синхронизировано команд: {len(synced)}")

@bot.tree.command(name="start", description="Начать играть в огород-бот")
async def start(interaction: discord.Interaction):
    from database import ensure_user
    user = await ensure_user(interaction.user.id)
    embed = discord.Embed(
        title="🌱 Добро пожаловать в Огород-бот!",
        description=(
            "Выращивай овощи, ягоды и фрукты, продавай урожай и расширяй свой огород!\n\n"
            "**Команды:**\n"
            "`/shop` — Магазин семян и огородов\n"
            "`/garden` — Твой огород (посадка, полив, сбор)\n"
            "`/inventory` — Инвентарь\n"
            "`/profile` — Профиль\n"
            "`/roles` — Магазин ролей\n"
            "`/daily` — Ежедневный бонус (+100 TON)\n"
            "`/addcoins` — Выдать монеты (админ)\n"
            "`/setcoins` — Установить баланс (админ)\n\n"
            "**Как играть:**\n"
            "1. Купи семена в `/shop`\n"
            "2. Посади их в `/garden` → 🌱 Посадить\n"
            "3. Поливай грядки 💧 (нужна лейка 🪣)\n"
            "4. Собери урожай и получи монеты TON\n"
            "5. Расширяй огород в `/shop`!"
        ),
        color=0x2ecc71
    )
    embed.add_field(name="💰 Стартовый баланс", value=f"{user['coins']} TON", inline=True)
    embed.add_field(name="🪣 Лейки", value=str(user["watering_cans"]), inline=True)
    await interaction.response.send_message(embed=embed)

try:
    asyncio.run(bot.start(BOT_TOKEN))
except Exception as e:
    print(f"FATAL ERROR: {e}", flush=True)
    traceback.print_exc()
