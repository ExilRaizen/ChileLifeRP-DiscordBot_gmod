import a2s
import discord
from datetime import datetime
from zoneinfo import ZoneInfo

# ============================================================
#  CONFIGURACIÓN — Edita estos valores
# ============================================================
SERVER_IP   = "151.242.242.197"
SERVER_PORT = 27070
# Lista de puertos a intentar si el principal falla (27070, luego 27015, etc.)
PORTS_TO_TRY = [27070, 27015, 27071] 

# ============================================================
#  DECORACIÓN DEL EMBED — Personaliza a tu gusto
# ============================================================
EMBED_CONFIG = {
    "color_online":  0x57F287,
    "color_offline": 0xED4245,
    "thumbnail_url": "", 
    "image_url":     "", 
    "footer_text":   "🕹️ Estado actualizado automáticamente",
    "footer_icon":   "",
}
# ============================================================

async def query_server() -> dict:
    """Busca el servidor intentando varios puertos."""
    for port in PORTS_TO_TRY:
        address = (SERVER_IP, port)
        try:
            # 1. Intentar obtener la información básica
            info = await a2s.ainfo(address, timeout=3.0)
            
            # 2. Intentar obtener los NOMBRES de los jugadores
            player_list = []
            try:
                players = await a2s.aplayers(address, timeout=2.0)
                player_list = [p.name for p in players if p.name]
            except Exception as e:
                print(f"[DEBUG] Se obtuvo info del server, pero falló la lista de jugadores en puerto {port}.")

            return {
                "online":      True,
                "name":        info.server_name,
                "map":         info.map_name,
                "players":     info.player_count,
                "max_players": info.max_players,
                "player_list": player_list,
                "ip":          SERVER_IP,
                "port":        SERVER_PORT,
                "vac":         info.vac_enabled,
                "game":        info.game,
            }
        except Exception as e:
            # Si falla este puerto, el bucle for intentará con el siguiente
            print(f"[DEBUG] Falló intento en puerto {port}: {e}")
            continue
            
    # Si probó todos los puertos y todos fallaron:
    return {"online": False}


def build_embed(data: dict) -> discord.Embed:
    """Construye el mensaje visual (Embed)"""
    now = datetime.now(ZoneInfo("America/Santiago"))
    
    cb = "```" # Variable de ayuda para evitar errores de formato en Python

    if data["online"]:
        embed = discord.Embed(
            title="🟢  Servidor Online",
            color=EMBED_CONFIG["color_online"],
            timestamp=now,
        )

        embed.add_field(name="🏷️  Nombre Del Servidor", value=f"{cb}{data['name']}{cb}", inline=False)
        embed.add_field(name="🗺️  Mapa actual", value=f"`{data['map']}`", inline=True)
        embed.add_field(name="👥  Jugadores", value=f"`{data['players']} / {data['max_players']}`", inline=True)
        embed.add_field(name="🔒  VAC", value="`Activado`" if data["vac"] else "`Desactivado`", inline=True)
        embed.add_field(name="🔌  Conexión", value=f"{cb}{data['ip']}:{data['port']}{cb}", inline=False)
        
        # Solo mostrar lista si hay jugadores Y el servidor permitió leer sus nombres
        if data["player_list"]:
            names = data["player_list"][:15]
            display = "\n".join(f"• {n}" for n in names)
            if len(data["player_list"]) > 15:
                display += f"\n*... y {len(data['player_list']) - 15} más*"
            embed.add_field(name=f"📋  Jugadores conectados ({len(data['player_list'])})", value=display, inline=False)
        elif data["players"] > 0:
            embed.add_field(name="📋  Jugadores", value="*Hay jugadores, pero el servidor oculta los nombres*", inline=False)
        else:
            embed.add_field(name="📋  Jugadores conectados", value="*El servidor está vacío*", inline=False)

    else:
        embed = discord.Embed(
            title="🔴  Servidor Offline",
            description="No se pudo conectar al servidor. Puede estar caído o reiniciándose.",
            color=EMBED_CONFIG["color_offline"],
            timestamp=now,
        )
        embed.add_field(name="🔌  Dirección", value=f"{cb}{data.get('ip', SERVER_IP)}:{data.get('port', 'Desconocido')}{cb}", inline=False)
        
    if EMBED_CONFIG["thumbnail_url"]: 
        embed.set_thumbnail(url=EMBED_CONFIG["thumbnail_url"])
    if EMBED_CONFIG["image_url"]: 
        embed.set_image(url=EMBED_CONFIG["image_url"])
    
    footer_kwargs = {"text": EMBED_CONFIG["footer_text"]}
    if EMBED_CONFIG["footer_icon"]: 
        footer_kwargs["icon_url"] = EMBED_CONFIG["footer_icon"]
    embed.set_footer(**footer_kwargs)

    return embed