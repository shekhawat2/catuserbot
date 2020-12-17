import asyncio
import os
import shutil
import time
from datetime import datetime

import git
import patch
from telethon.tl.functions.users import GetFullUserRequest

from userbot.plugins import reply_id

from ..utils import admin_cmd, progress, sudo_cmd
from . import ALIVE_NAME

DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else "cat"


@borg.on(admin_cmd(pattern="cclock(?: |$)(.*)", outgoing=True))
@borg.on(sudo_cmd(pattern="cclock(?: |$)(.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    mone = await edit_or_reply(event, "`Processing ...`")

    event.pattern_match.group(1)
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    if event.reply_to_msg_id:
        start = datetime.now()
        reply_message = await event.get_reply_message()
        reply_to_id = await reply_id(event)
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
            enablerzip = replied_user.user.username + "-CClockEnabler"
            disablerzip = replied_user.user.username + "-CClockDisabler"

            REPO = (
                "https://"
                + str(GITHUB_ACCESS_TOKEN)
                + "@github.com/shekhawat2/miui_cclock.git"
            )
            if os.path.exists("cclock"):
                shutil.rmtree("cclock")
            git.Repo.clone_from(REPO, "cclock")
            shutil.move(
                os.path.join(downloaded_file_name),
                os.path.join("cclock", "MiuiSystemUI.apk"),
            )

            os.chdir("cclock")
            await mone.edit(f"Generating CClock...")
            os.system("./tools/apktool if framework/framework-res.apk")
            os.system("./tools/apktool if framework/framework-ext-res.apk")
            os.system("./tools/apktool if framework/miui.apk")
            os.system("./tools/apktool if framework/miuisystem.apk")
            shutil.rmtree(
                "flashable/system/system/priv-app/MiuiSystemUI", ignore_errors=True
            )
            os.makedirs("flashable/system/system/priv-app/MiuiSystemUI")
            shutil.copy(
                "MiuiSystemUI.apk",
                "flashable/system/system/priv-app/MiuiSystemUI/MiuiSystemUI.apk",
            )

            shutil.make_archive(disablerzip, "zip", root_dir="flashable")
            os.system("./tools/apktool d -s MiuiSystemUI.apk")
            os.remove("MiuiSystemUI.apk")
            patch.fromfile("lcclock").apply()

            os.system("./tools/apktool b MiuiSystemUI")
            shutil.rmtree(
                "flashable/system/system/priv-app/MiuiSystemUI", ignore_errors=True
            )
            os.makedirs("flashable/system/system/priv-app/MiuiSystemUI")
            shutil.copy(
                "MiuiSystemUI/dist/MiuiSystemUI.apk",
                "flashable/system/system/priv-app/MiuiSystemUI/MiuiSystemUI.apk",
            )

            os.system(
                "java -jar ./tools/signapk/signapk.jar ./tools/keys/platform.x509.pem tools/keys/platform.pk8 ./MiuiSystemUI/dist/MiuiSystemUI.apk ./flashable/system/system/priv-app/MiuiSystemUI/MiuiSystemUI.apk"
            )
            shutil.make_archive(enablerzip, "zip", root_dir="flashable")

            await mone.edit(
                f"__**➥ CClock Generating...**__\n__**➥ Contact @Shekhawat2 to get it**__"
            )

            await mone.edit(f"Generated CClock")

            await event.client.send_file(
                event.chat_id, enablerzip + ".zip", reply_to=reply_to_id
            )
            await event.client.send_file(
                event.chat_id, disablerzip + ".zip", reply_to=reply_to_id
            )

            os.chdir("..")
            shutil.rmtree("cclock")

    else:
        await mone.edit("Reply to a message to download to my local server.")


"""CMD_HELP.update(
    {
        "cclock": " reply .cclock to media\
\nUsage: Makes Center Clock for MiuiSystemUI"
    }
)"""
