import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="comando", aliases=["comandos", "ayuda"])
    async def cmd_comandos(self, ctx):
        """Muestra la lista de comandos disponibles."""
        
        
        embed = discord.Embed(
            title="Panel de comandos - ChileLifeRP",
            description="Manual de comandos para su uso en el server",
            color=discord.Color.from_rgb(230, 130, 10),
        )

        # Sección de rangos VIP
        embed.add_field(
            name=" 💲Gestión de rangos💲",
            value=(
                "**`$rango @Usuario [rango] [tiempo]`**\n"
                "**Rangos válidos:** `diamond`, `golden`, `silver`\n"
                "**Ejemplos de uso:**\n"
                "└ `$rango @RikkoPoto diamond 30d` *(Da Diamond por 30 días)*\n"
                "└ `$rango @Raizen silver 12h` *(Da Silver por 12 horas)*\n\n"
                "**`$tiemporango @Usuario`**\n"
                "Muestra el tiempo restante del rango VIP."
            ),
            inline=False
        )

        # Sección de moderación
        embed.add_field(
            name=" 🛡️Moderación🛡️",
            value=(
                "**`$kick @Usuario [motivo]`**\n"
                "Expulsa al usuario del Discord.\n\n"
                "**`$ban @Usuario [tiempo opcional] [motivo]`**\n"
                "Banea al usuario del servidor (deja vacío el tiempo para baneo permanente).\n"
                "**Ejemplo:** `$ban @Usuario 7d Romper reglas`"
            ),
            inline=False
        )

        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))