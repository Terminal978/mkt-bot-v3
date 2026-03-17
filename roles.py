import discord
from discord.ext import commands
from discord import app_commands
from config import ROLES
from database import ensure_user, update_user


class RoleSelect(discord.ui.Select):
    def __init__(self, user_id: int, guild: discord.Guild, member_roles: list[int]):
        self.buyer_id = user_id
        self.guild = guild
        options = []
        for role_name, data in ROLES.items():
            owned = any(r.name == role_name for r in guild.roles if r.id in member_roles)
            label = f"{data['emoji']} {role_name} — {data['price']}🪙"
            if owned:
                label = "✅ " + label
            options.append(discord.SelectOption(
                label=label,
                value=role_name,
                description=data["description"],
                emoji=data["emoji"]
            ))
        super().__init__(placeholder="Выберите роль для покупки...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.buyer_id:
            await interaction.response.send_message("Это не ваш магазин!", ephemeral=True)
            return

        role_name = self.values[0]
        data = ROLES[role_name]

        # Проверяем, есть ли уже роль
        existing = discord.utils.get(interaction.user.roles, name=role_name)
        if existing:
            await interaction.response.send_message(f"У вас уже есть роль **{role_name}**!", ephemeral=True)
            return

        user = await ensure_user(interaction.user.id)
        if user["coins"] < data["price"]:
            await interaction.response.send_message(
                f"❌ Недостаточно монет! Нужно {data['price']}🪙, у вас {user['coins']}🪙",
                ephemeral=True
            )
            return

        # Ищем роль на сервере
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            await interaction.response.send_message(
                f"❌ Роль **{role_name}** не найдена на сервере. Попросите администратора создать её.",
                ephemeral=True
            )
            return

        # Проверяем права бота
        if interaction.guild.me.top_role <= role:
            await interaction.response.send_message(
                "❌ У бота недостаточно прав для выдачи этой роли. Роль бота должна быть выше покупаемой.",
                ephemeral=True
            )
            return

        await interaction.user.add_roles(role, reason="Куплено в магазине ролей")
        await update_user(interaction.user.id, coins=user["coins"] - data["price"])

        await interaction.response.send_message(
            f"{data['emoji']} **{interaction.user.display_name}** купил роль **{role_name}**! "
            f"Баланс: {user['coins'] - data['price']}🪙"
        )


class RoleShopView(discord.ui.View):
    def __init__(self, user_id: int, guild: discord.Guild, member_role_ids: list[int]):
        super().__init__(timeout=60)
        self.add_item(RoleSelect(user_id, guild, member_role_ids))


class RoleShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roles", description="Магазин ролей за монеты")
    async def roles(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Эта команда работает только на сервере!", ephemeral=True)
            return

        user = await ensure_user(interaction.user.id)
        member_role_ids = [r.id for r in interaction.user.roles]

        embed = discord.Embed(title="🎭 Магазин ролей", color=0x9b59b6)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="💰 Ваш баланс", value=f"{user['coins']}🪙", inline=False)

        roles_text = ""
        for role_name, data in ROLES.items():
            owned = discord.utils.get(interaction.user.roles, name=role_name)
            status = "✅" if owned else "🔒"
            roles_text += f"{status} {data['emoji']} **{role_name}** — {data['price']}🪙\n{data['description']}\n\n"

        embed.add_field(name="Доступные роли", value=roles_text, inline=False)
        embed.set_footer(text="Роли выдаются навсегда!")

        await interaction.response.send_message(
            embed=embed,
            view=RoleShopView(interaction.user.id, interaction.guild, member_role_ids)
        )


async def setup(bot):
    await bot.add_cog(RoleShop(bot))
