import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot("." , intents=intents)
intents.message_content = True

@bot.event
async def on_ready():
 print("Bot inicializado com sucesso!")

@bot.event
async def on_member_join(member):
 channel = discord.utils.get(member.guild.text_channels, name="boas-vindas")
 if channel:
  await channel.send(f"👋 Olá {member.mention}, seja bem-vindo(a) ao servidor!")


#quando o usuário digitar .ola, o bot irá responde-"lo
@bot.command()
async def ola(ctx:commands.Context):
 autor = ctx.author.name
 await ctx.reply(f"Eai {autor} digo, capitão broxa!")


#quando o usuário digitar .imitar e após digitar o texto, o bot irá imita-lo
@bot.command()
async def imitar(ctx:commands.Context , *, texto):
 await ctx.reply(texto)


#quando o usuário digitar .play e a musica, o bot irá tocar a musica
@bot.command()
async def play(ctx, url):
  if ctx.author.voice is None:
    await ctx.send("Você precisa estar em um canal de voz para usar este comando.")
    return
  
  canal = ctx.author.voice.channel
  if ctx.voice_client is None:
   await canal.connect()
  elif ctx.voice_client.channel != canal:
   await ctx.voice_client.move_to(canal)
  ydl_opts = {
  'format': 'bestaudio/best',
  'noplaylist': True,
  'quiet': True
    }

  ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
                      '-protocol_whitelist file,http,https,tcp,tls',
    'options': '-vn'
}
  

  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
   info = ydl.extract_info(url, download=False)
   audio_url = info['url']

  source = await discord.FFmpegOpusAudio.from_probe(
    audio_url,
    executable="C:/ffmpeg/bin/ffmpeg.exe",  # Use o caminho exato do seu sistema
    **ffmpeg_opts
)
  ctx.voice_client.stop()
  ctx.voice_client.play(source)
  await ctx.send(f"🎶 Tocando: {info['title']}")


# quando o usuário digitar .stop, o bot irá parar a musica
@bot.command()
async def stop(ctx):
  if ctx.voice_client:
    await ctx.voice_client.disconnect()
    await ctx.send("🛑 Reprodução interrompida.")
  else:
    await ctx.send("O bot não está conectado a nenhum canal de voz.")

bot.run("MTM3NTk5Mjc0NjI1ODQ2ODk1NQ.G8VvOc.eBGODmF5eEuX9pqoMAjsiPjUYk6Cvg5R5xlgp8")