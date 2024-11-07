#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/private > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/private/blob/master/LICENSE >
#
# All rights reserved.
import asyncio
import importlib
import sys

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from private import HELPABLE, LOGGER, app, userbot
from private.core.call import Yukki
from private.plugins import ALL_MODULES
from private.utils.database import get_banned_users, get_gbanned


async def init():
    if len(config.STRING_SESSIONS) == 0:
        LOGGER("private").error("No Assistant Clients Vars Defined!.. Exiting Process.")
        return
    if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
        LOGGER("private").warning(
            "No Spotify Vars defined. Your bot won't be able to play spotify queries."
        )
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        imported_module = importlib.import_module(all_module)

        if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
            if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                HELPABLE[imported_module.__MODULE__.lower()] = imported_module
    LOGGER("private.plugins").info("Successfully Imported All Modules ")
    await userbot.start()
    await Yukki.start()
    LOGGER("private").info("Assistant Started Sucessfully")
    try:
        await Yukki.stream_call(
            "http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("private").error(
            "Please ensure the voice call in your log group is active."
        )
        sys.exit()

    await Yukki.decorators()
    LOGGER("private").info("private Started Successfully")
    await idle()
    await app.stop()
    await userbot.stop()


if __name__ == "__main__":
    asyncio.get_event_loop_policy().get_event_loop().run_until_complete(init())
    LOGGER("private").info("Stopping private! GoodBye")
