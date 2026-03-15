import discord
from discord.ext import commands
from discord import app_commands
from config import SEEDS, GARDENS
from database import ensure_user, update_user


def render_garden(plots: list, garden_type: str) -> str:
    garden = GARDENS[garden_type]
    lines = [f"{garden['emoji']} **{garden['name']} огород** ({garden['slots']} грядок)\n"]
    for i, plot in enumerate(plots):
        if plot is None:
            lines.append(f"`[{i+1}]` 🟫 Пусто")
        else:
            seed = SEEDS[plot["seed_id"]]
            watered = plot["watered"]
            needed = seed["watering_needed"]
            bar = "💧" * watered + "⬜" * (needed - watered)
            if watered >= needed:
                lines.append(f"`[{i+1}]` {seed['emoji']} **{seed['name']}** — ✅ Готово к сбору!")
            else:
                lines.append(f"`[{i+1}]` {seed['emoji']} **{seed['name']}** — {bar} ({watered}/{needed})")
    return "\n".join(lines)


class PlotSelect(discord.ui.Select):
    def __init__(self, user_id: int, plots: list, mode: str):
        self.owner_id = user_id
        self.mode = mode
        options = []
        for i, plot in enumerate(plots):
            if mode == "plant" and plot is None:
                options.append(discord.SelectOption(label=f"Грядка {i+1} — Пусто", value=str(i), emoji="🟫"))
            elif mode == "water" and plot and plot["watered"] < SEEDS[plot["seed_id"]]["watering_needed"]:
                seed = SEEDS[plot["seed_id"]]
                options.append(discord.SelectOption(
                    label=f"Грядка {i+1} — {seed['name']} ({plot['watered']}/{seed['watering_needed']})",
                    value=str(i), emoji=seed["emoji"]
                ))
            elif mode == "harvest" and plot and plot["watered"] >= SEEDS[plot["seed_id"]]["watering_needed"]:
                seed = SEEDS[plot["seed_id"]]
                options.append(discord.SelectOption(
                    label=f"Грядка {i+1} — {seed['name']} готова!", value=str(i), emoji=seed["emoji"]
                ))
        if not options:
            options.append(discord.SelectOption(label="Нет доступных грядок", value="none"))
        super().__init__(placeholder="Выберите грядку...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Это не ваш огород!", ephemeral=True)
            return
        if self.values[0] == "none":
            await interaction.response.send_message("Нет доступных грядок.", ephemeral=True)
            return
        idx = int(self.values[0])
        user = await ensure_user(interaction.user.id)
        plots = user["plots"]

        if self.mode == "water":
            if user["watering_cans"] <= 0:
                await interaction.response.send_message("❌ Нет леек! Купи в /shop", ephemeral=True)
                return
            plots[idx]["watered"] += 1
            await update_user(interaction.user.id, plots=plots, watering_cans=user["watering_cans"] - 1)
            seed = SEEDS[plots[idx]["seed_id"]]
            needed = seed["watering_needed"]
            watered = plots[idx]["watered"]
            if watered >= needed:
                msg = f"💧 **{interaction.user.display_name}** полил {seed['emoji']} **{seed['name']}** — готова к сбору!"
            else:
                msg = f"💧 **{interaction.user.display_name}** полил {seed['emoji']} **{seed['name']}** ({watered}/{needed})"
            await interaction.response.send_message(msg)

        elif self.mode == "harvest":
            plot = plots[idx]
            seed = SEEDS[plot["seed_id"]]
            plots[idx] = None
            await update_user(
                interaction.user.id,
                plots=plots,
                coins=user["coins"] + seed["reward"]
            )
            await interaction.response.send_message(
                f"🎉 **{interaction.user.display_name}** собрал урожай: {seed['emoji']} **{seed['name']}**! +{seed['reward']}🪙"
            )


class SeedForPlotSelect(discord.ui.Select):
    def __init__(self, user_id: int, plot_idx: int, inventory: dict):
        self.owner_id = user_id
        self.plot_idx = plot_idx
        options = []
        for seed_id, count in inventory.items():
            if count > 0:
                seed = SEEDS[seed_id]
                options.append(discord.SelectOption(
                    label=f"{seed['name']} (x{count})",
                    value=seed_id,
                    emoji=seed["emoji"]
                ))
        if not options:
            options.append(discord.SelectOption(label="Нет семян в инвентаре", value="none"))
        super().__init__(placeholder="Выберите семя для посадки...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Это не ваш огород!", ephemeral=True)
            return
        if self.values[0] == "none":
            await interaction.response.send_message("Нет семян! Купи в /shop", ephemeral=True)
            return
        seed_id = self.values[0]
        user = await ensure_user(interaction.user.id)
        inv = user["inventory"]
        plots = user["plots"]

        if inv.get(seed_id, 0) <= 0:
            await interaction.response.send_message("❌ Нет этого семени!", ephemeral=True)
            return

        inv[seed_id] -= 1
        if inv[seed_id] == 0:
            del inv[seed_id]
        plots[self.plot_idx] = {"seed_id": seed_id, "watered": 0}
        await update_user(interaction.user.id, plots=plots, inventory=inv)
        seed = SEEDS[seed_id]
        await interaction.response.send_message(
            f"🌱 **{interaction.user.display_name}** посадил {seed['emoji']} **{seed['name']}** на грядке {self.plot_idx + 1}!"
        )


class PlantView(discord.ui.View):
    def __init__(self, user_id: int, plot_idx: int, inventory: dict):
        super().__init__(timeout=60)
        self.add_item(SeedForPlotSelect(user_id, plot_idx, inventory))


class GardenView(discord.ui.View):
    def __init__(self, user_id: int, plots: list, inventory: dict):
        super().__init__(timeout=60)
        self.owner_id = user_id
        self.plots = plots
        self.inventory = inventory

    @discord.ui.button(label="🌱 Посадить", style=discord.ButtonStyle.green)
    async def plant(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Это не ваш огород!", ephemeral=True)
            return
        user = await ensure_user(interaction.user.id)
        if not [p for p in user["plots"] if p is None]:
            await interaction.response.send_message("❌ Нет свободных грядок!", ephemeral=True)
            return
        if not user["inventory"]:
            await interaction.response.send_message("❌ Нет семян! Купи в /shop", ephemeral=True)
            return

        select = PlotSelect(interaction.user.id, user["plots"], "plant")
        view = discord.ui.View(timeout=60)
        view.add_item(select)

        async def plot_chosen(inter: discord.Interaction):
            if inter.user.id != self.owner_id:
                await inter.response.send_message("Это не ваш огород!", ephemeral=True)
                return
            idx = int(select.values[0])
            u = await ensure_user(inter.user.id)
            await inter.response.send_message(
                "Выберите семя для посадки:",
                view=PlantView(inter.user.id, idx, u["inventory"]),
                ephemeral=True
            )

        select.callback = plot_chosen
        await interaction.response.send_message("Выберите грядку для посадки:", view=view, ephemeral=True)

    @discord.ui.button(label="💧 Полить", style=discord.ButtonStyle.blurple)
    async def water(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Это не ваш огород!", ephemeral=True)
            return
        user = await ensure_user(interaction.user.id)
        view = discord.ui.View(timeout=60)
        view.add_item(PlotSelect(interaction.user.id, user["plots"], "water"))
        await interaction.response.send_message(
            f"🪣 Леек: {user['watering_cans']} | Выберите грядку для полива:",
            view=view, ephemeral=True
        )

    @discord.ui.button(label="🧺 Собрать урожай", style=discord.ButtonStyle.red)
    async def harvest(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Это не ваш огород!", ephemeral=True)
            return
        user = await ensure_user(interaction.user.id)
        view = discord.ui.View(timeout=60)
        view.add_item(PlotSelect(interaction.user.id, user["plots"], "harvest"))
        await interaction.response.send_message("Выберите готовую грядку для сбора:", view=view, ephemeral=True)


class Garden(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="garden", description="Посмотреть свой огород")
    async def garden(self, interaction: discord.Interaction):
        user = await ensure_user(interaction.user.id)
        embed = discord.Embed(
            title="🌾 Огород",
            description=render_garden(user["plots"], user["garden_type"]),
            color=0x27ae60
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"💰 {user['coins']}🪙 | 🪣 Леек: {user['watering_cans']}")
        await interaction.response.send_message(
            embed=embed,
            view=GardenView(interaction.user.id, user["plots"], user["inventory"])
        )


async def setup(bot):
    await bot.add_cog(Garden(bot))
