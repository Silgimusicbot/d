#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/private > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/private/blob/master/LICENSE >
#
# All rights reserved.
#
import os
from random import randint

from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import BANNED_USERS, SERVER_PLAYLIST_LIMIT
from strings import get_command
from private import Carbon, YouTube, app
from private.utils.database import (
    delete_playlist,
    get_assistant,
    get_playlist,
    get_playlist_names,
    save_playlist,
)
from private.utils.decorators import language, languageCB
from private.utils.decorators.play import botplaylist_markup, join_chat
from private.utils.inline.playlist import get_playlist_markup, warning_markup
from private.utils.pastebin import Yukkibin
from private.utils.stream.stream import stream

ADD_PLAYLIST_COMMAND = get_command("ADD_PLAYLIST_COMMAND")
PLAY_PLAYLIST_COMMAND = get_command("PLAY_PLAYLIST_COMMAND")
PLAYLIST_COMMAND = get_command("PLAYLIST_COMMAND")
DELETE_PLAYLIST_COMMAND = get_command("DELETE_PLAYLIST_COMMAND")


@app.on_message(filters.command(PLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def check_playlist(client, message: Message, _):
    _playlist = await get_playlist_names(message.from_user.id)
    if _playlist:
        get = await message.reply_text(_["playlist_2"])
    else:
        return await message.reply_text(_["playlist_3"])
    msg = _["playlist_4"]
    count = 0
    for ptlist in _playlist:
        _note = await get_playlist(message.from_user.id, ptlist)
        title = _note["title"]
        title = title.title()
        duration = _note["duration"]
        count += 1
        msg += f"\n\n{count}- {title[:70]}\n"
        msg += _["playlist_5"].format(duration)
    link = await Yukkibin(msg)
    lines = msg.count("\n")
    if lines >= 17:
        car = os.linesep.join(msg.split(os.linesep)[:17])
    else:
        car = msg
    carbon = await Carbon.generate(car, randint(100, 10000000000))
    await get.delete()
    await message.reply_photo(carbon, caption=_["playlist_15"].format(link))


async def get_keyboard(_, user_id):
    keyboard = InlineKeyboard(row_width=5)
    _playlist = await get_playlist_names(user_id)
    count = len(_playlist)
    for x in _playlist:
        _note = await get_playlist(user_id, x)
        title = _note["title"]
        title = title.title()
        keyboard.row(
            InlineKeyboardButton(
                text=title,
                callback_data=f"del_playlist {x}",
            )
        )
    keyboard.row(
        InlineKeyboardButton(
            text=_["PL_B_5"],
            callback_data=f"delete_warning",
        ),
        InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"close"),
    )
    return keyboard, count


@app.on_message(
    filters.command(DELETE_PLAYLIST_COMMAND) & filters.group & ~BANNED_USERS
)
@language
async def del_group_message(client, message: Message, _):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["PL_B_6"],
                    url=f"https://t.me/{app.username}?start=delplaylists",
                ),
            ]
        ]
    )
    await message.reply_text(_["playlist_6"], reply_markup=upl)


async def get_keyboard(_, user_id):
    keyboard = InlineKeyboard(row_width=5)
    _playlist = await get_playlist_names(user_id)
    count = len(_playlist)
    for x in _playlist:
        _note = await get_playlist(user_id, x)
        title = _note["title"]
        title = title.title()
        keyboard.row(
            InlineKeyboardButton(
                text=title,
                callback_data=f"del_playlist {x}",
            )
        )
    keyboard.row(
        InlineKeyboardButton(
            text=_["PL_B_5"],
            callback_data=f"delete_warning",
        ),
        InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"close"),
    )
    return keyboard, count


@app.on_message(
    filters.command(DELETE_PLAYLIST_COMMAND) & filters.private & ~BANNED_USERS
)
@language
async def del_plist_msg(client, message: Message, _):
    _playlist = await get_playlist_names(message.from_user.id)
    if _playlist:
        get = await message.reply_text(_["playlist_2"])
    else:
        return await message.reply_text(_["playlist_3"])
    keyboard, count = await get_keyboard(_, message.from_user.id)
    await get.edit_text(_["playlist_7"].format(count), reply_markup=keyboard)


@app.on_callback_query(filters.regex("play_playlist") & ~BANNED_USERS)
@languageCB
async def play_playlist(client, CallbackQuery, _):
    message = CallbackQuery.message
    userbot = await get_assistant(message.chat.id)
    try:
        try:
            get = await app.get_chat_member(CallbackQuery.message.chat.id, userbot.id)
        except ChatAdminRequired:
            return await msg.edit(
                _["call_1"],
            )
        if get.status == ChatMemberStatus.BANNED:
            return await msg.edit(_["call_2"])
    except UserNotParticipant:
        msg = await message.reply_text("🥀")
        await join_chat(message, message.chat.id, _, msg)

    callback_data = CallbackQuery.data.strip()
    mode = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        try:
            return await CallbackQuery.answer(
                _["playlist_3"],
                show_alert=True,
            )
        except:
            return
    chat_id = CallbackQuery.message.chat.id
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.message.delete()
    result = []
    try:
        await CallbackQuery.answer()
    except:
        pass
    video = True if mode == "v" else None
    mystic = await CallbackQuery.message.reply_text(_["play_1"])
    for vidids in _playlist:
        result.append(vidids)
    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="playlist",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
        return await mystic.edit_text(err)
    return await mystic.delete()


@app.on_message(filters.command(PLAY_PLAYLIST_COMMAND) & ~BANNED_USERS & filters.group)
@languageCB
async def play_playlist_command(client, message, _):
    try:
        try:
            userbot = await get_assistant(message.chat.id)
            get = await app.get_chat_member(message.chat.id, userbot.id)
        except ChatAdminRequired:
            return await msg.edit_text(_["call_1"])
        if (
            get.status == ChatMemberStatus.BANNED
            or get.status == ChatMemberStatus.RESTRICTED
        ):
            try:
                await app.unban_chat_member(chat_id, userbot.id)
            except:
                return await msg.edit_text(
                    text=_["call_2"].format(userbot.username, userbot.id),
                )
            await join_chat(message, message.chat.id, _, msg)
    except UserNotParticipant:
        msg = await message.reply_text("🥀")
        await join_chat(message, message.chat.id, _, msg)

    mode = message.command[0][0]
    user_id = message.from_user.id
    _playlist = await get_playlist_names(user_id)
    if not _playlist:
        try:
            return await message.reply(
                _["playlist_3"],
                quote=True,
            )
        except:
            return

    chat_id = message.chat.id
    user_name = message.from_user.first_name

    try:
        await message.delete()
    except:
        pass

    result = []
    video = True if mode == "v" else None
    mystic = await message.reply_text(_["play_1"])

    for vidids in _playlist:
        result.append(vidids)

    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            message.chat.id,
            video,
            streamtype="playlist",
        )
    except Exception as e:
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_3"].format(ex_type)
        return await mystic.edit_text(err)

    return await mystic.delete()


"""
@app.on_message(filters.command(ADD_PLAYLIST_COMMAND) & ~BANNED_USERS)
@language
async def add_playlist(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text(_["playlist_22"])
    query = message.command[1]

    if "youtube.com/playlist" in query:
        adding = await message.reply_text(_["playlist_21"])
        try:
            results = Playlist(url)
            for video in results.videos:
                if video.get("isPlayable"):
                    video_info = {
                        "videoid": video["id"],
                        "title": video["title"],
                        "duration": video["duration"],
                    }
                    user_id = message.from_user.id
                    await save_playlist(user_id, video["id"], video_info)

        except Exception as e:
            return await message.reply_text(
                f"Looking like not a valid youtube playlist url or\nPlaylist created by YouTube Not Supported"
            )

        user_id = message.from_user.id
        await adding.delete()
        return await message.reply_text(_["playlist_20"])
    else:
        try:
            user_id = message.from_user.id
            _check = await get_playlist(user_id, videoid)
            if _check:
                try:
                    return await message.reply_text(_["playlist_8"])
                except KeyError:
                    pass

            _count = await get_playlist_names(user_id)
            count = len(_count)
            if count == SERVER_PLAYLIST_LIMIT:
                try:
                    return await message.reply_text(
                        _["playlist_9"].format(SERVER_PLAYLIST_LIMIT)
                    )
                except KeyError:
                    pass

            m = await message.reply(_["playlist_21"])
            title, duration_min, duration_sec, thumbnail, videoid = (
                await YouTube.details(videoid, True)
            )
            title = (title[:50]).title()
            plist = {
                "videoid": videoid,
                "title": title,
                "duration": duration_min,
            }

            await save_playlist(user_id, videoid, plist)
            await m.delete()
            await message.reply_photo(thumbnail, caption=_["playlist_20"])

        except KeyError:
            return await message.reply_text("**Something wrong happens **")
        except Exception:
            pass
"""


@app.on_callback_query(filters.regex("remove_playlist") & ~BANNED_USERS)
@languageCB
async def del_plist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    deleted = await delete_playlist(CallbackQuery.from_user.id, videoid)
    if deleted:
        try:
            await CallbackQuery.answer(_["playlist_11"], show_alert=True)
        except:
            pass
    else:
        try:
            return await CallbackQuery.answer(_["playlist_12"], show_alert=True)
        except:
            return

    return await CallbackQuery.edit_message_text(text=_["playlist_23"])


@app.on_callback_query(filters.regex("remove_playlist") & ~BANNED_USERS)
@languageCB
async def del_plist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    CallbackQuery.from_user.id
    deleted = await delete_playlist(CallbackQuery.from_user.id, videoid)
    if deleted:
        try:
            await CallbackQuery.answer(_["playlist_11"], show_alert=True)
        except:
            pass
    else:
        try:
            return await CallbackQuery.answer(_["playlist_12"], show_alert=True)
        except:
            return

    return await CallbackQuery.edit_message_text(text=_["playlist"])


@app.on_callback_query(filters.regex("add_playlist") & ~BANNED_USERS)
@languageCB
async def add_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    _check = await get_playlist(user_id, videoid)
    if _check:
        try:
            return await CallbackQuery.answer(_["playlist_8"], show_alert=True)
        except:
            return
    _count = await get_playlist_names(user_id)
    count = len(_count)
    if count == SERVER_PLAYLIST_LIMIT:
        try:
            return await CallbackQuery.answer(
                _["playlist_9"].format(SERVER_PLAYLIST_LIMIT),
                show_alert=True,
            )
        except:
            return
    (
        title,
        duration_min,
        duration_sec,
        thumbnail,
        vidid,
    ) = await YouTube.details(videoid, True)
    title = (title[:50]).title()
    plist = {
        "videoid": vidid,
        "title": title,
        "duration": duration_min,
    }
    await save_playlist(user_id, videoid, plist)
    try:
        title = (title[:30]).title()
        return await CallbackQuery.answer(
            _["playlist_10"].format(title), show_alert=True
        )
    except:
        return


@app.on_callback_query(filters.regex("del_playlist") & ~BANNED_USERS)
@languageCB
async def del_plist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    deleted = await delete_playlist(CallbackQuery.from_user.id, videoid)
    if deleted:
        try:
            await CallbackQuery.answer(_["playlist_11"], show_alert=True)
        except:
            pass
    else:
        try:
            return await CallbackQuery.answer(_["playlist_12"], show_alert=True)
        except:
            return
    keyboard, count = await get_keyboard(_, user_id)
    return await CallbackQuery.edit_message_reply_markup(reply_markup=keyboard)


@app.on_callback_query(filters.regex("delete_whole_playlist") & ~BANNED_USERS)
@languageCB
async def del_whole_playlist(client, CallbackQuery, _):
    _playlist = await get_playlist_names(CallbackQuery.from_user.id)
    for x in _playlist:
        await CallbackQuery.answer(_["playlist_25"], show_alert=True)
        await delete_playlist(CallbackQuery.from_user.id, x)
    return await CallbackQuery.edit_message_text(_["playlist_13"])


@app.on_callback_query(filters.regex("get_playlist_playmode") & ~BANNED_USERS)
@languageCB
async def get_playlist_playmode_(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    buttons = get_playlist_markup(_)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("home_play") & ~BANNED_USERS)
@languageCB
async def home_play_(client, CallbackQuery, _):
    pass

    try:
        await CallbackQuery.answer()
    except:
        pass
    buttons = botplaylist_markup(_)
    return await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("delete_warning") & ~BANNED_USERS)
@languageCB
async def delete_warning_message(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    upl = warning_markup(_)
    return await CallbackQuery.edit_message_text(_["playlist_14"], reply_markup=upl)


@app.on_callback_query(filters.regex("del_back_playlist") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    user_id = CallbackQuery.from_user.id
    _playlist = await get_playlist_names(user_id)
    if _playlist:
        try:
            await CallbackQuery.answer(_["playlist_2"], show_alert=True)
        except:
            pass
    else:
        try:
            return await CallbackQuery.answer(_["playlist_3"], show_alert=True)
        except:
            return
    keyboard, count = await get_keyboard(_, user_id)
    return await CallbackQuery.edit_message_text(
        _["playlist_7"].format(count), reply_markup=keyboard
    )
