import asyncio
import os

from pyrogram import enums, filters, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import (
    BANNED_USERS,
    SOUNCLOUD_IMG_URL,
    STREAM_IMG_URL,
    TELEGRAM_AUDIO_URL,
    TELEGRAM_VIDEO_URL,
    SUPPORT_CHAT,
    adminlist,
    confirmer,
    votemode,
)
from Oneforall import YouTube, app
from Oneforall.core.call import Hotty
from Oneforall.misc import SUDOERS, db
from Oneforall.utils.database import (
    get_active_chats,
    get_upvote_count,
    group_assistant,
    is_active_chat,
    is_music_playing,
    is_nonadmin_chat,
    music_off,
    music_on,
    set_loop,
)
from Oneforall.utils.decorators.language import languageCB
from Oneforall.utils.formatters import seconds_to_min
from Oneforall.utils.inline import close_markup
from Oneforall.utils.inline.rich import (
    send_now_playing_rich,
    set_now_playing_state,
    update_now_playing_progress,
    deliver_rich,
    html_to_rich_blocks,
)
from Oneforall.utils.stream.autoclear import auto_clean
from Oneforall.utils.thumbnails import get_thumb

checker = {}
upvoters = {}


@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    command, chat = callback_request.split("|")
    counter = None
    if "_" in str(chat):
        bet = chat.split("_")
        chat = bet[0]
        counter = bet[1]
    chat_id = int(chat)
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)
    mention = CallbackQuery.from_user.mention
    if command == "UpVote":
        if chat_id not in votemode:
            votemode[chat_id] = {}
        if chat_id not in upvoters:
            upvoters[chat_id] = {}

        voters = (upvoters[chat_id]).get(CallbackQuery.message.id)
        if not voters:
            upvoters[chat_id][CallbackQuery.message.id] = []

        vote = (votemode[chat_id]).get(CallbackQuery.message.id)
        if not vote:
            votemode[chat_id][CallbackQuery.message.id] = 0

        if CallbackQuery.from_user.id in upvoters[chat_id][CallbackQuery.message.id]:
            (upvoters[chat_id][CallbackQuery.message.id]).remove(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.id] -= 1
        else:
            (upvoters[chat_id][CallbackQuery.message.id]).append(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.id] += 1
        upvote = await get_upvote_count(chat_id)
        get_upvotes = int(votemode[chat_id][CallbackQuery.message.id])
        if get_upvotes >= upvote:
            votemode[chat_id][CallbackQuery.message.id] = upvote
            try:
                exists = confirmer[chat_id][CallbackQuery.message.id]
                current = db[chat_id][0]
            except Exception:
                return await CallbackQuery.edit_message_text("ғᴀɪʟᴇᴅ.")
            try:
                if current["vidid"] != exists["vidid"]:
                    return await CallbackQuery.edit_message.text(_["admin_35"])
                if current["file"] != exists["file"]:
                    return await CallbackQuery.edit_message.text(_["admin_35"])
            except Exception:
                return await CallbackQuery.edit_message_text(_["admin_36"])
            try:
                await CallbackQuery.edit_message_text(_["admin_37"].format(upvote))
            except Exception:
                pass
            command = counter
            mention = "ᴜᴘᴠᴏᴛᴇs"
        else:
            if (
                CallbackQuery.from_user.id
                in upvoters[chat_id][CallbackQuery.message.id]
            ):
                await CallbackQuery.answer(_["admin_38"], show_alert=True)
            else:
                await CallbackQuery.answer(_["admin_39"], show_alert=True)
            upl = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"👍 {get_upvotes}",
                            callback_data=f"ADMIN  UpVote|{chat_id}_{counter}",
                        )
                    ]
                ]
            )
            await CallbackQuery.answer(_["admin_40"], show_alert=True)
            return await CallbackQuery.edit_message_reply_markup(reply_markup=upl)
    else:
        is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
        if not is_non_admin:
            if CallbackQuery.from_user.id not in SUDOERS:
                admins = adminlist.get(CallbackQuery.message.chat.id)
                if not admins:
                    return await CallbackQuery.answer(_["admin_13"], show_alert=True)
                else:
                    if CallbackQuery.from_user.id not in admins:
                        return await CallbackQuery.answer(
                            _["admin_14"], show_alert=True
                        )

    play_now = False
    if command == "PlayNow":
        tracks = db.get(chat_id) or []
        index = next(
            (i for i, t in enumerate(tracks) if i > 0 and t.get("qid") == counter),
            None,
        )
        if index is None:
            return await CallbackQuery.answer("Track is no longer in queue.", show_alert=True)
        if index != 1:
            tracks.insert(1, tracks.pop(index))
        play_now = True
        command = "Skip"

    if command == "Pause":
        if not await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_1"], show_alert=True)
        await CallbackQuery.answer()
        await music_off(chat_id)
        await Hotty.pause_stream(chat_id)
        await set_now_playing_state(chat_id, playing=False)
        await CallbackQuery.message.reply_text(
            _["admin_2"].format(mention), reply_markup=close_markup(_)
        )
    elif command == "Resume":
        if await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_3"], show_alert=True)
        await CallbackQuery.answer()
        await music_on(chat_id)
        await Hotty.resume_stream(chat_id)
        await set_now_playing_state(chat_id, playing=True)
        await CallbackQuery.message.reply_text(
            _["admin_4"].format(mention), reply_markup=close_markup(_)
        )
    elif command == "Stop" or command == "End":
        await CallbackQuery.answer()
        await Hotty.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await CallbackQuery.message.reply_text(
            _["admin_5"].format(mention), reply_markup=close_markup(_)
        )
        try:
            await CallbackQuery.message.delete()
        except Exception:
            pass
    elif command == "Skip" or command == "Replay":
        check = db.get(chat_id)
        if not check:
            return await CallbackQuery.answer("❌ Queue is empty!", show_alert=True)

        try:
            await CallbackQuery.answer("⏭️ Skipping to next song...", show_alert=False)
        except Exception:
            pass

        if command == "Skip":
            try:
                assistant = await group_assistant(Hotty, chat_id)
                await Hotty.change_stream(assistant, chat_id)
                return
            except Exception as e:
                try:
                    await CallbackQuery.message.reply_text(f"❌ Skip Error: {e}")
                except Exception:
                    pass
                return
        else:
            queued = check[0]["file"]
            streamtype = check[0]["streamtype"]
            status = True if str(streamtype) == "video" else None
            try:
                await Hotty.skip_stream(chat_id, queued, video=status)
                return await CallbackQuery.answer("⟲ Replaying track...")
            except Exception as e:
                return await CallbackQuery.answer(f"Replay Error: {e}", show_alert=True)


async def markup_timer():
    while not await asyncio.sleep(7):
        active_chats = await get_active_chats()
        for chat_id in active_chats:
            try:
                if not await is_music_playing(chat_id):
                    continue
                playing = db.get(chat_id)
                if not playing:
                    continue
                duration_seconds = int(playing[0]["seconds"])
                if duration_seconds == 0:
                    continue
                try:
                    mystic = playing[0]["mystic"]
                except Exception:
                    continue
                try:
                    check = checker[chat_id][mystic.id]
                    if check is False:
                        continue
                except Exception:
                    pass
                try:
                    await update_now_playing_progress(
                        mystic,
                        chat_id,
                        seconds_to_min(playing[0]["played"]),
                        playing[0]["dur"],
                    )
                except Exception:
                    continue
            except Exception:
                continue


@app.on_callback_query(filters.regex("nowplaying_queue") & ~BANNED_USERS)
async def nowplaying_queue_alert(client, CallbackQuery):
    chat_id = int(CallbackQuery.data.split(None, 1)[1])
    tracks = db.get(chat_id) or []
    upcoming = tracks[1:]
    if not upcoming:
        return await CallbackQuery.answer("Queue is empty.", show_alert=True)
    lines = [f"{i}. {t['title'][:40]}" for i, t in enumerate(upcoming[:10], start=1)]
    await CallbackQuery.answer("\n".join(lines), show_alert=True)


asyncio.create_task(markup_timer())
