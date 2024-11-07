#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/private > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/private/blob/master/LICENSE >
#
# All rights reserved.
#
from typing import Union

from pyrogram.types import InlineKeyboardButton

from config import GITHUB_REPO
from private import app


def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?start=help",
            ),
            InlineKeyboardButton(text=_["S_B_2"], callback_data="settings_helper"),
        ],
    ]
    return buttons


def private_panel(_, BOT_USERNAME, OWNER: Union[bool, int] = None):
    buttons = (
        [InlineKeyboardButton(text=_["S_B_8"], callback_data="settings_back_helper")],
    )
    [
        InlineKeyboardButton(
            text=_["S_B_5"], url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    ],
    [
        InlineKeyboardButton(
            text="𝐈𝐂𝐎𝐍 𝐁𝐀𝐊𝐔 𝐒𝐎𝐇𝐁𝐄𝐓 🇦🇿", url="https://t.me/iconSohbetQrupu"
        )
    ],
    [InlineKeyboardButton(text="Crime 𝐁𝐥𝐨𝐠⁰³⁹🖤", url="https://t.me/CrimeBlog")],
    [
        InlineKeyboardButton(
            text=_["S_B_7"],
            user_id=OWNER,
        )
    ]
    return buttons
