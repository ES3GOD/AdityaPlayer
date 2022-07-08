import os
import aiofiles
import aiohttp
import ffmpeg
import requests
from os import path
from asyncio.queues import QueueEmpty
from typing import Callable
from pyrogram import Client, filters
from pyrogram.types import Message, Voice, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from modules.cache.admins import set
from modules.clientbot import clientbot, queues
from modules.clientbot.clientbot import client as USER
from modules.helpers.admins import get_administrators
from youtube_search import YoutubeSearch
from modules import converter
from PIL import ImageFilter
from modules.downloaders import youtube
from modules.config import DURATION_LIMIT, que, SUDO_USERS
from modules.cache.admins import admins as a
from modules.helpers.filters import command, other_filters
from modules.helpers.command import commandpro
from modules.helpers.decorators import errors, authorized_users_only
from modules.helpers.errors import DurationLimitError
from modules.helpers.gets import get_url, get_file_name
from PIL import Image, ImageFont, ImageDraw
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputStream
from pytgcalls.types.input_stream import InputAudioStream

# plus
chat_id = None
useer = "NaN"


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 27:        
            text1 += " " + i
        elif len(text2) + len(i) < 25:        
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1,text2]

# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image = Image.open(f"./background.png")
    black = Image.open("etc/black.jpg")
    img = Image.open("etc/CodexunSq.png")
    image5 = changeImageSize(1280, 720, img)
    image1 = changeImageSize(1280, 720, image)
    image1 = image1.filter(ImageFilter.BoxBlur(10))
    image11 = changeImageSize(1280, 720, image)
    image1 = image11.filter(ImageFilter.BoxBlur(10))
    image2 = Image.blend(image1,black,0.6)

    # Cropping circle from thubnail
    image3 = image11.crop((280,0,1000,720))
    #lum_img = Image.new('L', [720,720] , 0)
   # draw = ImageDraw.Draw(lum_img)
   # draw.pieslice([(0,0), (720,720)], 0, 360, fill = 255, outline = "white")
   # img_arr =np.array(image3)
    #lum_img_arr =np.array(lum_img)
    #final_img_arr = np.dstack((img_arr,lum_img_arr))
    #image3 = Image.fromarray(final_img_arr)
    image3 = image3.resize((500,500))
    

    image2.paste(image3, (100,115))
    image2.paste(image5, mask = image5)

    # fonts
    font1 = ImageFont.truetype(r'etc/Codexun.otf', 30)
    font2 = ImageFont.truetype(r'etc/Codexun.otf', 60)
    font3 = ImageFont.truetype(r'etc/Codexun.otf', 49)
    font4 = ImageFont.truetype(r'etc/Mukta-ExtraBold.ttf', 35)

    image4 = ImageDraw.Draw(image2)

    # title
    title1 = truncate(title)
    image4.text((670, 280), text=title1[0], fill="white", font = font3, align ="left") 
    image4.text((670, 332), text=title1[1], fill="white", font = font3, align ="left") 

    # description
    views = f"Views : {views}"
    duration = f"Duration : {duration} minutes"
    channel = f"Request : Pratheek Music Bot"

    image4.text((670, 410), text=views, fill="white", font = font4, align ="left") 
    image4.text((670, 460), text=duration, fill="white", font = font4, align ="left") 
    image4.text((670, 510), text=channel, fill="white", font = font4, align ="left")

    
    image2.save(f"final.png")
    os.remove(f"background.png")
    final = f"temp.png"
    return final

@Client.on_message(
    commandpro(["/play", "/yt", "/ytp", "play", "yt", "ytp", "@", "#"])
    & filters.group
    & ~filters.edited
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    global que
    global useer
    
    lel = await message.reply("**🔎 Searching...**")

    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "Aditya_Player"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "**👨‍🔧 Promote me as Admin First Before Playing any Songs**")
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "**📪 Music Bot is Ready To Play now**")

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    await lel.edit(
                        f"**🧑‍🏭 Add assistant manually**")
    try:
        await USER.get_chat(chid)
    except:
        await lel.edit(
            f"**🧑‍🏭 Add assistant manually**")
        return
    
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"**❌ Duration more than {DURATION_LIMIT} Minutes cannot be played**"
            )

        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://te.legra.ph/file/ed6920a2f0ab5af3fd55d.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
            [
                [
                        InlineKeyboardButton(
                            text="⚙️Support",
                            url=f"https://t.me/CoreFourxd")

                ]
            ]
        )

        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            keyboard = InlineKeyboardMarkup(
            [
                [
                        InlineKeyboardButton(
                            text="⚙️Support",
                            url=f"https://t.me/CoreFourxd")

                ]
            ]
        )

        except Exception as e:
            title = "NaN"
            thumb_name = "https://te.legra.ph/file/ed6920a2f0ab5af3fd55d.png"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
            [
                [
                        InlineKeyboardButton(
                            text="⚙️Support",
                            url=f"https://t.me/CoreFourxd")

                ]
            ]
        )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"**❌ Duration more than {DURATION_LIMIT} Minutes cannot be played**"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))
    else:
        if len(message.command) < 2:
            return await lel.edit(
                "**🔍 Provide me a song name**"
            )
        await lel.edit("**🔍 Processing...**")
        query = message.text.split(None, 1)[1]
        # print(query)
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            await lel.edit(
                "**❌ Music Bot found try any other song**"
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
            [
                [
                        InlineKeyboardButton(
                            text="⚙️Support",
                            url=f"https://t.me/CoreFourxd")

                ]
            ]
        )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"**❌ Duration more than {DURATION_LIMIT} Minutes cannot be played**"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))
    ACTV_CALLS = []
    chat_id = message.chat.id
    for x in clientbot.pytgcalls.active_calls:
        ACTV_CALLS.append(int(x.chat_id))
    if int(chat_id) in ACTV_CALLS:
        position = await queues.put(chat_id, file=file_path)
        await message.reply_photo(
            photo="final.png",
            caption="**➕ Added to Queue**".format(position),
            reply_markup=keyboard,
        )
    else:
        await clientbot.pytgcalls.join_group_call(
                chat_id, 
                InputStream(
                    InputAudioStream(
                        file_path,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )

        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="**▶️ Playing now**".format(),
           )

    os.remove("final.png")
    return await lel.delete()
    
    
@Client.on_message(commandpro(["/pause", "pause"]) & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    await clientbot.pytgcalls.pause_stream(message.chat.id)
    await message.reply_text("**⏸️ Paused**")


@Client.on_message(commandpro(["/resume", "resume"]) & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    await clientbot.pytgcalls.resume_stream(message.chat.id)
    await message.reply_text("**🔁 Resumed**")



@Client.on_message(commandpro(["/skip", "/next", "skip", "next"]) & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    ACTV_CALLS = []
    chat_id = message.chat.id
    for x in clientbot.pytgcalls.active_calls:
        ACTV_CALLS.append(int(x.chat_id))
    if int(chat_id) not in ACTV_CALLS:
        await message.reply_text("**⏩ Skipped**")
    else:
        queues.task_done(chat_id)
        
        if queues.is_empty(chat_id):
            await clientbot.pytgcalls.leave_group_call(chat_id)
        else:
            await clientbot.pytgcalls.change_stream(
                chat_id, 
                InputStream(
                    InputAudioStream(
                        clientbot.queues.get(chat_id)["file"],
                    ),
                ),
            )


    await message.reply_text("**⏩ Skipped**")


@Client.on_message(commandpro(["/end", "end", "/stop", "stop", "x"]) & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    try:
        clientbot.queues.clear(message.chat.id)
    except QueueEmpty:
        pass

    await clientbot.pytgcalls.leave_group_call(message.chat.id)
    await message.reply_text("**⏹️ Music Ended**")


@Client.on_message(commandpro(["reload", "refresh"]))
@errors
@authorized_users_only
async def admincache(client, message: Message):
    set(
        message.chat.id,
        (
            member.user
            for member in await message.chat.get_members(filter="administrators")
        ),
    )

    await message.reply_photo(
                              photo="https://te.legra.ph/file/02306701e296bcf8634fa.png",
                              caption="**🔄 Reloaded**"
    )
