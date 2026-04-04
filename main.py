import discord
from discord.ext import commands
import asyncio
import traceback
import os
import sys
from aiohttp import web
from config import BOT_TOKEN
from database import init_db

# Добавляем папку bot в путь поиска модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bot"))

print("=== Бот запускается ===", flush=True)

async def health(request):
    return web.Response(text="OK")

async def start_web():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Health server on port {port}", flush=True)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("on_ready fired", flush=True)
    try:
        await asyncio.wait_for(init_db(), timeout=15)
        print("DB initialized", flush=True)
    except asyncio.TimeoutError:
        print("ERROR: DB connection timeout! Check DATABASE_URL", flush=True)
        return
    except Exception as e:
        print(f"ERROR: DB init failed: {e}", flush=True)
        traceback.print_exc()
        return
    for cog in ["cogs.shop", "cogs.garden", "cogs.inventory", "cogs.roles", "cogs.admin"]:
        try:
            await bot.load_extension(cog)
            print(f"Loaded {cog}", flush=True)
        except Exception as e:
            print(f"ERROR loading {cog}: {e}", flush=True)
            traceback.print_exc()
    print("Cogs loaded", flush=True)
    synced = await bot.tree.sync()
    print(f"Bot ready: {bot.user} | Commands synced: {len(synced)}", flush=True)

@bot.tree.command(name="start", description="Начать играть в огород-бот")
async def start(interaction: discord.Interaction):
    await interaction.response.defer()
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
    await interaction.followup.send(embed=embed)

async def main():
    await start_web()
    try:
        await bot.start(BOT_TOKEN)
    except Exception as e:
        print(f"FATAL ERROR: {e}", flush=True)
        traceback.print_exc()

asyncio.run(main())
