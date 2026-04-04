import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, date
from config import DAILY_REWARD, OWNER_ID, ROLES
from database import ensure_user, update_user


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addcoins", description="[Владелец] Добавить монеты игроку")
    @app_commands.describe(member="Игрок", amount="Количество монет")
    async def addcoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ У тебя нет прав на эту команду!", ephemeral=True)
            return
        if amount == 0:
            await interaction.response.send_message("Укажи ненулевое количество монет!", ephemeral=True)
            return
        await interaction.response.defer()
        user = await ensure_user(member.id)
        new_balance = user["coins"] + amount
        if new_balance < 0:
            await interaction.followup.send(
                f"❌ Нельзя: баланс уйдёт в минус ({user['coins']} + {amount} = {new_balance})",
                ephemeral=True
            )
            return

        await update_user(member.id, coins=new_balance)

        if amount > 0:
            msg = f"💰 **{interaction.user.display_name}** выдал **{amount} TON** игроку **{member.display_name}**! Баланс: {new_balance} TON"
        else:
            msg = f"💸 **{interaction.user.display_name}** снял **{abs(amount)} TON** у **{member.display_name}**. Баланс: {new_balance} TON"

        await interaction.followup.send(msg)



    @app_commands.command(name="setcoins", description="[Владелец] Установить баланс игроку")
    @app_commands.describe(member="Игрок", amount="Новый баланс")
    async def setcoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ У тебя нет прав на эту команду!", ephemeral=True)
            return
        if amount < 0:
            await interaction.response.send_message("Баланс не может быть отрицательным!", ephemeral=True)
            return
        await interaction.response.defer()
        await ensure_user(member.id)
        await update_user(member.id, coins=amount)
        await interaction.followup.send(
            f"💰 **{interaction.user.display_name}** установил баланс **{member.display_name}** → **{amount} TON**"
        )



    @app_commands.command(name="daily", description="Получить ежедневный бонус")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = await ensure_user(interaction.user.id)
        today = date.today().isoformat()

        if user.get("last_daily") == today:
            await interaction.followup.send(
                f"⏳ Ты уже получал бонус сегодня! Возвращайся завтра.\n"
                f"Баланс: {user['coins']} TON",
                ephemeral=True
            )
            return

        new_balance = user["coins"] + DAILY_REWARD
        await update_user(interaction.user.id, coins=new_balance, last_daily=today)
        await interaction.followup.send(
            f"🎁 **{interaction.user.display_name}** получил ежедневный бонус: **+{DAILY_REWARD} TON**! "
            f"Баланс: {new_balance} TON"
        )


    @app_commands.command(name="push", description="[Владелец] Выдать роль Фермер участнику")
    @app_commands.describe(member="Участник, которому выдать роль")
    async def push(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ У тебя нет прав на эту команду!", ephemeral=True)
            return
        await interaction.response.defer()

        role_name = "Фермер"
        role_data = ROLES[role_name]

        existing = discord.utils.get(member.roles, name=role_name)
        if existing:
            await interaction.followup.send(
                f"⚠️ У **{member.display_name}** уже есть роль **{role_name}**!", ephemeral=True
            )
            return

        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            await interaction.followup.send(
                f"❌ Роль **{role_name}** не найдена на сервере. Создайте её вручную.", ephemeral=True
            )
            return

        if interaction.guild.me.top_role <= role:
            await interaction.followup.send(
                "❌ Роль бота должна быть выше роли Фермер в иерархии.", ephemeral=True
            )
            return

        await member.add_roles(role, reason=f"Выдано командой /push от {interaction.user}")
        await interaction.followup.send(
            f"{role_data['emoji']} **{member.display_name}** получил роль **{role_name}**!"
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
