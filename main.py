from sys import executable

import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(".", intents=intents)
intents.message_content = True

queues = {}

async def play_next(ctx):
    if ctx.guild.id in queues and queues [ctx.guild.id]:
        video_info = queues[ctx.guild.id].pop(0)
        audio_url = video_info['url']
        titulo = video_info['title']

        source = await discord.FFmpegOpusAudio.from_probe(
            audio_url,
            executable="C:/ffmpeg/bin/ffmpeg.exe",
            **ffmpeg_opts
        )

        ctx.voice_client.play(source, after=lambda _: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

        await ctx.send(f"🎶 Tocando agora: **{titulo}**")
    else:
        await ctx.send("✅ Fila terminada.")

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

#Confirma que o bo foi inicializado
@bot.event
async def on_ready():
    print("Bot inicializado com sucesso!")

#Da boas vindas à novos mebros
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="boas-vindas")
    if channel:
        await channel.send(f"👋 Olá {member.mention}, seja bem-vindo(a) ao servidor!")


@bot.command()
async def ola(ctx: commands.Context):
    autor = ctx.author.name
    await ctx.reply(f"Eai {autor} digo, capitão broxa!")

#imita um texto digitado pelo usuário
@bot.command()
async def imitar(ctx: commands.Context, *, texto):
    await ctx.reply(texto)


@bot.command()
async def play(ctx, *, search: str):
    #Conecta ao canal de voz
    if ctx.author.voice is None:
        return await ctx.send("Você precisa estar em um canal de voz para usar este comando.")

    canal_voz = ctx.author.voice.channel
    if ctx.voice_client is None:
        await canal_voz.connect()
    elif ctx.voice_client.channel != canal_voz:
        await ctx.voice_client.move_to(canal_voz)

    #Divide a busca em várias músicas - Usa a vírgula como separador
    songs = [song.strip() for song in search.split(',')]

    # Se houver mais de uma música, envia uma mensagem inicial
    if len(songs) > 1:
        await ctx.send(f"🔎 Processando {len(songs)} músicas. Isso pode levar um momento...")

    songs_added = 0
    songs_failed = []

    #Faz um loop para cada música na lista
    for song_query in songs:
        if not song_query:  #Pula buscas vazias (ex: .play a,,c)
            continue

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(song_query, download=False)
                if 'entries' not in info or not info['entries']:
                    songs_failed.append(song_query)
                    continue  #Pula para a próxima música

                video_info = info['entries'][0]

                #Garante que a fila para o servidor existe
                if ctx.guild.id not in queues:
                    queues[ctx.guild.id] = []

                #Adiciona a música encontrada na fila
                queues[ctx.guild.id].append(video_info)
                songs_added += 1

            except Exception as e:
                print(f"Erro ao buscar '{song_query}': {e}")
                songs_failed.append(song_query)

    #Informe
    if songs_added > 0:
        await ctx.send(f"✅ Adicionei **{songs_added}** música(s) à fila.")
    if songs_failed:
        failed_list = "\n- ".join(songs_failed)
        await ctx.send(f"❌ Não consegui encontrar as seguintes músicas:\n- {failed_list}")

    #Inicia a fila caso o bot nao esteja tocando nada
    if not ctx.voice_client.is_playing() and songs_added > 0:
        await play_next(ctx)

#Termina a musca/playlist
@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()


        await ctx.voice_client.disconnect()
        await ctx.send("🛑 Reprodução interrompida e bot desconectado.")
    else:
        await ctx.send("O bot não está conectado a nenhum canal de voz.")


#Pula a música
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.send("⏭️ Pulando música...")
        ctx.voice_client.stop()
    else:
        await ctx.send("Não há música tocando para pular.")

#Mostra a fila de músicas
@bot.command(name="fila", aliases=["q", "queque"])
async def show_queque(ctx):
    if ctx.guild.id not in queues or not queues[ctx.guild.id]:
        return await ctx.send("A fila está vazia!")

    mensagem_fila = "📋 **Fila de Músicas:**\n"
    for i, video in enumerate(queues[ctx.guild.id]):
        #Limitação em 10 músicas para manter o chat otganizado
        if i >= 10:
            mensagem_fila += f"\n... e mais {len(queues[ctx.guild.id]) - i} músicas."
            break
        mensagem_fila += f"`{i + 1}.` {video['title']}\n"

    await ctx.send(mensagem_fila)

bot.run("")
