import discord
from discord.ext import commands
from discord import app_commands
from config import SEEDS, GARDENS
from database import ensure_user


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inventory", description="Посмотреть инвентарь")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = await ensure_user(interaction.user.id)
        garden = GARDENS[user["garden_type"]]

        embed = discord.Embed(title="🎒 Инвентарь", color=0xe67e22)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="💰 Монеты", value=f"{user['coins']} TON", inline=True)
        embed.add_field(name="🪣 Лейки", value=str(user["watering_cans"]), inline=True)
        embed.add_field(name="🏡 Огород", value=f"{garden['emoji']} {garden['name']}", inline=True)

        if user["inventory"]:
            seeds_text = "\n".join(
                f"{SEEDS[sid]['emoji']} **{SEEDS[sid]['name']}** x{count}"
                for sid, count in user["inventory"].items()
            )
        else:
            seeds_text = "Нет семян. Купи в /shop!"

        embed.add_field(name="🌰 Семена", value=seeds_text, inline=False)

        plots = user["plots"]
        planted = sum(1 for p in plots if p is not None)
        ready = sum(
            1 for p in plots
            if p and p["watered"] >= SEEDS[p["seed_id"]]["watering_needed"]
        )
        embed.add_field(
            name="🌾 Грядки",
            value=f"Занято: {planted}/{len(plots)} | Готово к сбору: {ready}",
            inline=False
        )

        await interaction.followup.send(embed=embed)
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = await ensure_user(interaction.user.id)
        garden = GARDENS[user["garden_type"]]
        plots = user["plots"]
        total_seeds = sum(user["inventory"].values())

        embed = discord.Embed(
            title=f"👤 {interaction.user.display_name}",
            color=0x3498db
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="💰 Монеты", value=f"{user['coins']} TON", inline=True)
        embed.add_field(name="🪣 Лейки", value=str(user["watering_cans"]), inline=True)
        embed.add_field(name="🌰 Семян в инвентаре", value=str(total_seeds), inline=True)
        embed.add_field(name="🏡 Огород", value=f"{garden['emoji']} {garden['name']} ({len(plots)} грядок)", inline=False)

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Inventory(bot))
