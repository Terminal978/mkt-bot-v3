import discord
from discord.ext import commands
from discord import app_commands
from config import SEEDS, GARDENS, WATERING_CAN_PRICE
from database import ensure_user, update_user


class SeedSelect(discord.ui.Select):
    def __init__(self, user_id: int):
        self.buyer_id = user_id
        options = [
            discord.SelectOption(
                label=f"{s['name']} — {s['price']}🪙",
                description=f"Поливов: {s['watering_needed']} | Награда: {s['reward']}🪙",
                value=seed_id,
                emoji=s["emoji"]
            )
            for seed_id, s in SEEDS.items()
        ]
        super().__init__(placeholder="Выберите семя...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.buyer_id:
            await interaction.response.send_message("Это не ваш магазин!", ephemeral=True)
            return
        seed_id = self.values[0]
        seed = SEEDS[seed_id]
        user = await ensure_user(interaction.user.id)

        if user["coins"] < seed["price"]:
            await interaction.response.send_message("❌ Недостаточно монет!", ephemeral=True)
            return

        inv = user["inventory"]
        inv[seed_id] = inv.get(seed_id, 0) + 1
        await update_user(interaction.user.id, coins=user["coins"] - seed["price"], inventory=inv)
        await interaction.response.send_message(
            f"🛒 **{interaction.user.display_name}** купил {seed['emoji']} **{seed['name']}**! Баланс: {user['coins'] - seed['price']}🪙"
        )


class GardenSelect(discord.ui.Select):
    def __init__(self, user_id: int, current_garden: str):
        self.buyer_id = user_id
        garden_order = list(GARDENS.keys())
        current_idx = garden_order.index(current_garden)
        options = []
        for g_id, g in GARDENS.items():
            label = f"{g['name']} ({g['slots']} грядок) — {g['price']}🪙"
            if g_id == current_garden:
                label = "✅ " + label
            options.append(discord.SelectOption(
                label=label, value=g_id, emoji=g["emoji"],
                default=(g_id == current_garden)
            ))
        super().__init__(placeholder="Выберите огород...", options=options)
        self.current_idx = current_idx
        self.garden_order = garden_order

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.buyer_id:
            await interaction.response.send_message("Это не ваш магазин!", ephemeral=True)
            return
        garden_id = self.values[0]
        garden = GARDENS[garden_id]
        user = await ensure_user(interaction.user.id)
        new_idx = self.garden_order.index(garden_id)

        if new_idx <= self.current_idx:
            await interaction.response.send_message("У вас уже есть этот или лучший огород!", ephemeral=True)
            return
        if user["coins"] < garden["price"]:
            await interaction.response.send_message("❌ Недостаточно монет!", ephemeral=True)
            return

        old_plots = user["plots"]
        new_plots = old_plots + [None] * (garden["slots"] - len(old_plots))
        await update_user(
            interaction.user.id,
            coins=user["coins"] - garden["price"],
            garden_type=garden_id,
            plots=new_plots
        )
        await interaction.response.send_message(
            f"🏡 **{interaction.user.display_name}** купил {garden['emoji']} **{garden['name']}** ({garden['slots']} грядок)!"
        )


class ShopView(discord.ui.View):
    def __init__(self, user_id: int, current_garden: str):
        super().__init__(timeout=60)
        self.add_item(SeedSelect(user_id))
        self.add_item(GardenSelect(user_id, current_garden))

    @discord.ui.button(label="🪣 Купить лейку (50🪙)", style=discord.ButtonStyle.blurple, row=2)
    async def buy_can(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await ensure_user(interaction.user.id)
        if user["coins"] < WATERING_CAN_PRICE:
            await interaction.response.send_message("❌ Недостаточно монет!", ephemeral=True)
            return
        await update_user(
            interaction.user.id,
            coins=user["coins"] - WATERING_CAN_PRICE,
            watering_cans=user["watering_cans"] + 1
        )
        await interaction.response.send_message(
            f"🪣 **{interaction.user.display_name}** купил лейку! Баланс: {user['coins'] - WATERING_CAN_PRICE}🪙"
        )


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shop", description="Открыть магазин семян и огородов")
    async def shop(self, interaction: discord.Interaction):
        user = await ensure_user(interaction.user.id)
        garden = GARDENS[user["garden_type"]]
        embed = discord.Embed(title="🛒 Магазин", color=0x2ecc71)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="💰 Баланс", value=f"{user['coins']}🪙", inline=True)
        embed.add_field(name="🏡 Огород", value=f"{garden['emoji']} {garden['name']}", inline=True)
        embed.add_field(name="🪣 Лейки", value=str(user["watering_cans"]), inline=True)

        seeds_text = "\n".join(
            f"{s['emoji']} **{s['name']}** — {s['price']}🪙 | Поливов: {s['watering_needed']} | +{s['reward']}🪙"
            for s in SEEDS.values()
        )
        embed.add_field(name="🌰 Семена", value=seeds_text, inline=False)

        await interaction.response.send_message(
            embed=embed,
            view=ShopView(interaction.user.id, user["garden_type"])
        )


async def setup(bot):
    await bot.add_cog(Shop(bot))
