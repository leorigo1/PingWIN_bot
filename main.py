import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(".", intents=intents)
intents.message_content = True


@bot.event
async def on_ready():
    print("Bot inicializado com sucesso!")


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="boas-vindas")
    if channel:
        await channel.send(f"👋 Olá {member.mention}, seja bem-vindo(a) ao servidor!")


@bot.command()
async def ola(ctx: commands.Context):
    autor = ctx.author.name
    await ctx.reply(f"Eai {autor} digo, capitão broxa!")


@bot.command()
async def imitar(ctx: commands.Context, *, texto):
    await ctx.reply(texto)


@bot.command()
async def play(ctx, *, search: str):
    # 1. Verifica se o usuário está em um canal de voz
    if ctx.author.voice is None:
        await ctx.send("Você precisa estar em um canal de voz para usar este comando.")
        return

    # 2. Conecta ao canal de voz do usuário
    canal = ctx.author.voice.channel
    if ctx.voice_client is None:
        await canal.connect()
    elif ctx.voice_client.channel != canal:
        await ctx.voice_client.move_to(canal)

    await ctx.send(f"🔎 Procurando por: `{search}`...")

    # 3. Configura o yt-dlp e o FFmpeg
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch'
    }

    ffmpeg_opts = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    try:
        # 4. Usa o yt-dlp para BUSCAR a música pelo nome
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search, download=False)

            if 'entries' not in info or not info['entries']:
                await ctx.send("❌ Não consegui encontrar nenhuma música com esse nome.")
                return

            video_info = info['entries'][0]
            audio_url = video_info['url']
            titulo = video_info['title']

        # 5. Prepara o áudio para o Discord usando FFmpeg
        source = await discord.FFmpegOpusAudio.from_probe(
            audio_url,
            executable="C:/ffmpeg/bin/ffmpeg.exe",  # Lembre-se de verificar este caminho!
            **ffmpeg_opts
        )

        # 6. Toca o áudio
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        ctx.voice_client.play(source)
        await ctx.send(f"🎶 Tocando agora: **{titulo}**")

    except Exception as e:
        await ctx.send("Ocorreu um erro ao tentar tocar a música.")
        print(f"Erro no comando play: {e}")


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 Reprodução interrompida e bot desconectado.")
    else:
        await ctx.send("O bot não está conectado a nenhum canal de voz.")

bot.run("")
