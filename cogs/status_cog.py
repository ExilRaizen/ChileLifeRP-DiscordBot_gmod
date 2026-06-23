import discord
from discord.ext import commands, tasks
from datetime import datetime
from zoneinfo import ZoneInfo

# Importamos nuestras funciones desde el archivo de lógica
from server_status import query_server, build_embed

UPDATE_INTERVAL = 60 # Segundos entre actualizaciones

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_channel_id = 1502049429752910045  # ID de tu canal
        self.status_message_id = None
        
        # Iniciar el loop al cargar el módulo
        self.update_status.start()

    def cog_unload(self):
        # Detener el loop si se recarga/apaga el módulo de forma segura
        self.update_status.cancel()

    @tasks.loop(seconds=UPDATE_INTERVAL)
    async def update_status(self):
        channel = self.bot.get_channel(self.status_channel_id)
        if channel is None:
            return

        data  = await query_server()
        embed = build_embed(data)

        try:
            if self.status_message_id:
                msg = await channel.fetch_message(self.status_message_id)
                await msg.edit(embed=embed)
            else:
                msg = await channel.send(embed=embed)
                self.status_message_id = msg.id
        except discord.NotFound:
            # Si el mensaje fue borrado manualmente, creamos uno nuevo
            msg = await channel.send(embed=embed)
            self.status_message_id = msg.id
        except Exception as e:
            print(f"[ERROR] Discord no dejó actualizar el mensaje: {e}")

        estado = "🟢 ONLINE" if data["online"] else "🔴 OFFLINE"
        print(f"[{datetime.now(ZoneInfo('America/Santiago')).strftime('%H:%M:%S')}] {estado} | Jugadores: {data.get('players', '—')}")

    @update_status.before_loop
    async def before_update_status(self):
        # Aseguramos que el bot esté conectado a los servidores de Discord antes de empezar el loop
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅  Módulo de Status (Cog) cargado correctamente.")

    @commands.command(name="status")
    async def cmd_status(self, ctx):
        """Comando manual para revisar el estado."""
        data  = await query_server()
        embed = build_embed(data)
        await ctx.send(embed=embed)

    @commands.command(name="setstatus")
    @commands.has_permissions(administrator=True)
    async def cmd_setstatus(self, ctx):
        """Comando para establecer el canal de actualizaciones."""
        self.status_channel_id = ctx.channel.id
        self.status_message_id = None
        await ctx.message.delete()
        await self.update_status()

# Función requerida por discord.py para cargar el Cog
async def setup(bot):
    await bot.add_cog(StatusCog(bot))
