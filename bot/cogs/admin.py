import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, date
from config import DAILY_REWARD
from database import ensure_user, update_user


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addcoins", description="[Админ] Добавить монеты игроку")
    @app_commands.describe(member="Игрок", amount="Количество монет")
    @app_commands.checks.has_permissions(administrator=True)
    async def addcoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount == 0:
            await interaction.response.send_message("Укажи ненулевое количество монет!", ephemeral=True)
            return

        user = await ensure_user(member.id)
        new_balance = user["coins"] + amount
        if new_balance < 0:
            await interaction.response.send_message(
                f"❌ Нельзя: баланс уйдёт в минус ({user['coins']} + {amount} = {new_balance})",
                ephemeral=True
            )
            return

        await update_user(member.id, coins=new_balance)

        if amount > 0:
            msg = f"💰 **{interaction.user.display_name}** выдал **{amount}🪙** игроку **{member.display_name}**! Баланс: {new_balance}🪙"
        else:
            msg = f"💸 **{interaction.user.display_name}** снял **{abs(amount)}🪙** у **{member.display_name}**. Баланс: {new_balance}🪙"

        await interaction.response.send_message(msg)

    @addcoins.error
    async def addcoins_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Только администраторы могут использовать эту команду!", ephemeral=True)

    @app_commands.command(name="setcoins", description="[Админ] Установить баланс игроку")
    @app_commands.describe(member="Игрок", amount="Новый баланс")
    @app_commands.checks.has_permissions(administrator=True)
    async def setcoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount < 0:
            await interaction.response.send_message("Баланс не может быть отрицательным!", ephemeral=True)
            return

        await ensure_user(member.id)
        await update_user(member.id, coins=amount)
        await interaction.response.send_message(
            f"💰 **{interaction.user.display_name}** установил баланс **{member.display_name}** → **{amount}🪙**"
        )

    @setcoins.error
    async def setcoins_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ Только администраторы могут использовать эту команду!", ephemeral=True)

    @app_commands.command(name="daily", description="Получить ежедневный бонус")
    async def daily(self, interaction: discord.Interaction):
        user = await ensure_user(interaction.user.id)
        today = date.today().isoformat()

        if user.get("last_daily") == today:
            await interaction.response.send_message(
                f"⏳ Ты уже получал бонус сегодня! Возвращайся завтра.\n"
                f"Баланс: {user['coins']}🪙",
                ephemeral=True
            )
            return

        new_balance = user["coins"] + DAILY_REWARD
        await update_user(interaction.user.id, coins=new_balance, last_daily=today)
        await interaction.response.send_message(
            f"🎁 **{interaction.user.display_name}** получил ежедневный бонус: **+{DAILY_REWARD}🪙**! "
            f"Баланс: {new_balance}🪙"
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
