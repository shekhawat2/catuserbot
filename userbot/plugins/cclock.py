import asyncio
import math
import os
import shutil
import time
from datetime import datetime

import git
from pySmartDL import SmartDL
from telethon.tl.functions.users import GetFullUserRequest

from var import Var

from .. import ALIVE_NAME
from ..utils import admin_cmd, edit_or_reply, humanbytes, progress, sudo_cmd

DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else "cat"


@borg.on(admin_cmd(pattern="cclock(?: |$)(.*)", outgoing=True))
@borg.on(sudo_cmd(pattern="cclock(?: |$)(.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    mone = await edit_or_reply(event, "`Processing ...`")
    input_str = event.pattern_match.group(1)
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await bot.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                ),
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
        else:
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit(
                f"__**➥ Downloaded in {ms} seconds.**__\n__**➥ Downloaded to :- **__ `{downloaded_file_name}`\n__**➥ Downloaded by :-**__ {DEFAULTUSER}"
            )
            reply_message = await event.get_reply_message()
            replied_user = await event.client(GetFullUserRequest(reply_message.from_id))
            replied_user.user.first_name
            replied_user.user.username
            GITHUB_ACCESS_TOKEN = Var.GITHUB_ACCESS_TOKEN
            REPO = (
                "https://"
                + str(GITHUB_ACCESS_TOKEN)
                + "@github.com/shekhawat2/miui_cclock.git"
            )
            if os.path.exists("cclock"):
                shutil.rmtree("cclock")
            repo = git.Repo.clone_from(REPO, "cclock")
            shutil.move(
                os.path.join(downloaded_file_name),
                os.path.join("cclock", "MiuiSystemUI.apk"),
            )
            repo.config_writer().set_value("user", "name", "Anand Shekhawat").release()
            repo.config_writer().set_value(
                "user", "email", "anandsingh215@yahoo.com"
            ).release()
            repo.git.add("MiuiSystemUI.apk", f=True)
            repo.git.commit("--amend", "-m", replied_user.user.username)
            repo.git.push("origin", "master", f=True)
            await mone.edit(
                f"__**➥ CClock Generating...**__\n__**➥ Contact @Shekhawat2 to get it**__"
            )
            if os.path.exists("cclock"):
                shutil.rmtree("cclock")
    elif input_str:
        start = datetime.now()
        url = input_str
        file_name = os.path.basename(url)
        to_download_directory = Config.TMP_DOWNLOAD_DIRECTORY
        if "|" in input_str:
            url, file_name = input_str.split("|")
        url = url.strip()
        file_name = file_name.strip()
        downloaded_file_name = os.path.join(to_download_directory, file_name)
        downloader = SmartDL(url, downloaded_file_name, progress_bar=False)
        downloader.start(blocking=False)
        c_time = time.time()
        while not downloader.isFinished():
            total_length = downloader.filesize if downloader.filesize else None
            downloaded = downloader.get_dl_size()
            display_message = ""
            now = time.time()
            diff = now - c_time
            percentage = downloader.get_progress() * 100
            downloader.get_speed()
            round(diff) * 1000
            progress_str = "{0}{1}\nProgress: {2}%".format(
                "".join(["█" for i in range(math.floor(percentage / 5))]),
                "".join(["░" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )
            estimated_total_time = downloader.get_eta(human=True)
            try:
                current_message = f"trying to download\nURL: {url}\nFile Name: {file_name}\n{progress_str}\n{humanbytes(downloaded)} of {humanbytes(total_length)}\nETA: {estimated_total_time}"
                if round(diff % 10.00) == 0 and current_message != display_message:
                    await mone.edit(current_message)
                    display_message = current_message
            except Exception as e:
                logger.info(str(e))
        end = datetime.now()
        ms = (end - start).seconds
        if downloader.isSuccessful():
            await mone.edit(
                f"__**➥ Downloaded in {ms} seconds.**__\n__**➥ Downloaded to :- **__ `{downloaded_file_name}`\n__**➥ Downloaded by :-**__ {DEFAULTUSER}"
            )
        else:
            await mone.edit("Incorrect URL\n {}".format(input_str))
    else:
        await mone.edit("Reply to a message to download to my local server.")


"""CMD_HELP.update(
    {
        "download": ".download <link|filename> or reply to media\
\nUsage: Downloads file to the server."
    }
)"""
