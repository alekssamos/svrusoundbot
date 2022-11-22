"svrusoundbot v1.2"

from pyrogram import errors
from pyrogram import Client, filters, idle, StopPropagation
from pyrogram.types import Message
from pyrogram.types import InputMediaAudio
from pyrogram import enums

from typing import Any, Union, List, Iterable, Tuple, Awaitable
from loguru import logger
from dotenv import load_dotenv
import asyncio
import aiofiles
import aiofiles.os
import os
import sys
import shutil
from docx import Document
from msspeech import MSSpeech

LogChat = -366949499
supported_extensions = ["docx"]
queue = []
all_workers=set()
me = None

def human_readable_size(size, decimal_places=2):
    """
    https://stackoverflow.com/a/43690506/14077164
    """
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if size < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

async def add_worker(coro:Awaitable)->None:
    task = asyncio.create_task(coro)
    all_workers.add(task)
    task.add_done_callback(lambda x: logger.debug(f"worker {x} has been removed"))
    task.add_done_callback(all_workers.discard)
    logger.debug("worker has been added")


class MyClient(Client):
    async def start(self):
        global me
        logger.debug("running bot...")
        res = await super().start()
        await add_worker(worker())
        me = await self.get_me()
        print(">>> BOT STARTED with username: @" + me.username)
        logger.info(f"BOT STARTED with username: @{me.username}")
        try:
            await self.send_message(
                chat_id=LogChat, text="Bot 1.3 started", disable_notification=True
            )
        except:
            pass
        return res

class CommandError(Exception):
    pass


load_dotenv()
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
app = MyClient(
    "svrusoundbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

app.set_parse_mode(enums.ParseMode.DISABLED)



def fnum(f:str)->str:
    ff:str = ""
    if not os.path.isfile(f) and not os.path.isdir(f):
        return f
    i = -1
    while True:
        i+=1
        ff = f+"_"+str(i)
        if not os.path.isfile(ff) and not os.path.isdir(ff):
            break
    return ff

async def run_command(*args):
    "https://stackoverflow.com/questions/63782892/using-asyncio-to-wait-for-results-from-subprocess"
    # Create subprocess
    process = await asyncio.create_subprocess_exec(
        *args,
        # stdout must a pipe to be accessible as process.stdout
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    if stdout is None:
        stdout = b""
    if stderr is None:
        stderr = b""
    if process.returncode != 0:
        raise CommandError(
            f"returncode = {process.returncode}\r\n stdout = {stdout.decode().strip()}\r\n stderr = {stderr.decode().strip()}"
        )
    # Return stdout
    return stdout.decode().strip()


async def ffmpeg_concat(files: list, filename: str) -> None:
    """
    # Combine multiple audio or video files into one.
    # Returns the error code. Zero is successful.
    # example:
    from glob import glob
    await ffmpeg_concat(glob("*.mp3"), "playlist.mp3")
    """
    if len(files) == 0:
        raise ValueError("files can't be empty")
    pipe = "|".join(files)
    return await run_command("ffmpeg", "-i", f"concat:{pipe}", "-c", "copy", filename)


async def a_main(message, progress_message, docfilename, audiofilename):
    "Обрабатывает слова и возвращает список ошибок или пустой список"
    errors:list = []
    wordDoc = Document(docfilename)
    ru_mss = MSSpeech()
    await ru_mss.set_voice((await ru_mss.get_voices_by_substring("Dmitry"))[0]["Name"])
    sv_mss = MSSpeech()
    await sv_mss.set_voice((await sv_mss.get_voices_by_substring("Mattias"))[0]["Name"])
    c:int = 0
    files:list = []
    table = wordDoc.tables[0]
    all:int = len(list(table.rows))
    logger.info(f"Starting voiceover {all} rows and 2 cells")
    await progress_message.edit(text="Начинаю озвучку...")
    for row in table.rows:
        c+=1
        logger.debug(f"{c}/{all}...")
        await progress_message.edit(f"Прогресс: {c}/{all}...")
        svword, ruword = (row.cells[0].text, row.cells[1].text)
        if svword.strip() == "" or ruword.strip() == "":
            texts = " | ".join([cell.text for cell in row.cells])
            errors.append(f"Skipping row №{c}: {texts}")
            logger.warning(errors[-1])
            continue
        files.append(f"{docfilename}{c}sv.mp3")
        files.append(f"{docfilename}{c}ru.mp3")
        await asyncio.gather(
            sv_mss.synthesize(svword, files[-2]),
            ru_mss.synthesize(ruword, files[-1])
        )
    logger.info("concat...")
    await progress_message.edit("concat files...")
    await ffmpeg_concat(files, audiofilename)
    logger.info("deleting...")
    await progress_message.edit("delete files...")
    for file in files:
        await aiofiles.os.remove(file)
    return errors

@app.on_message( filters.command(["start","help"]))
async def start_help(_, message):
    await message.reply("""
    Отправляешь мне  документ формата docs
    с таблицей со шведским словом в первой колонке и с русским во второй
    и получаешь mp3 файл с озвучкой.
    Никаких кнопок, команд и настроек здесь нет.
    """)


@app.on_message(filters.document)
async def new_document(_, message):
    logger.info("new document received")
    if not (message.document is not None and message.document.file_name.split(".")[-1].lower() in supported_extensions):
        return False
    progress_message = await message.reply(f"Очередь №{(len(queue) + 1)}")
    queue.append((message, progress_message))
    logger.debug("appended to queue")

async def worker():
    logger.info("worker started")
    while True:
        try:
            message, progress_message = queue.pop()
            logger.debug("I received a new message")
        except IndexError:
            await asyncio.sleep(0.1)
            continue
        folder = fnum(os.path.join("downloads", f"{message.chat.id}"))
        if not os.path.isdir("downloads"):
            os.mkdir("downloads")
        os.mkdir(folder)
        await progress_message.edit("Скачиваю документ...")
        file_with_text = await app.download_media(message, os.path.join(folder, message.document.file_name))
        try:
            w = a_main(
                message,
                progress_message,
                file_with_text,
                file_with_text+".mp3"
            )
            errors = await asyncio.wait_for(w, 999)
            del w
            if len(errors) > 0:
                txt = "\n".join(errors)
                await message.reply(f"Во время обработки произошли следующие ошибки: {len(errors)}\n{txt}")
            await progress_message.edit("Загрузка...")
            await message.reply_audio(
                file_with_text+".mp3",
                performer = "Mattias & Dmitry",
                title = message.document.file_name,
                progress = progress,
                progress_args  = (progress_message,)
            )
            await progress_message.delete()
        except asyncio.TimeoutError as e:
            await progress_message.edit("Слишком долго. Операция отменена.")
            logger.exception("timeout")
        except Exception:
            ei = sys.exc_info()
            logger.exception("error")
            try: await app.send_message(chat_id=LogChat, text=ei[1])
            except: pass
            await progress_message.edit(f"Нет, вообще ничего не получилось.\n{ei[0]} {ei[1]}")
        finally:
            del message
            del progress_message
            shutil.rmtree(folder)
            await asyncio.sleep(1)
            await add_worker(worker())
            break

async def progress(current, total, progress_message):
    await progress_message.edit(text=f"""
    Отправка аудио файла, {human_readable_size(current, 3)} / {human_readable_size(total, 3)} ({current * 100 / total:.1f}%) Загружено.
    """.strip())

app.run()
