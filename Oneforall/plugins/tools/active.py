import asyncio
import time

from pyrogram import filters, types
from pyrogram.enums import ButtonStyle
from pyrogram.types import Message
from unidecode import unidecode

from config import OWNER_ID
from Oneforall import app
from Oneforall.misc import SUDOERS
from Oneforall.utils.database import (
    get_active_chats,
    get_active_video_chats,
    remove_active_chat,
    remove_active_video_chat,
)
from Oneforall.utils.inline.rich import caption_blocks, edit_rich

FETCH_CONCURRENCY = 15
DISPLAY_LIMIT = 60
REFRESH_COOLDOWN = 5

_gate = asyncio.Semaphore(FETCH_CONCURRENCY)
_last_refresh = {}


async def _resolve(chat_id, drop):
    async with _gate:
        try:
            chat = await app.get_chat(chat_id)
        except Exception:
            await drop(chat_id)
            return None
    title = unidecode((chat.title or str(chat_id)).strip()).upper() or str(chat_id)
    return {"id": chat_id, "title": title, "username": chat.username}


async def _resolve_all(chat_ids, drop):
    tasks = [asyncio.ensure_future(_resolve(cid, drop)) for cid in chat_ids]
    resolved = await asyncio.gather(*tasks) if tasks else []
    return [r for r in resolved if r]


def _entry_line(index, chat):
    label = f"{index}. {chat['title']}"
    if chat["username"]:
        line = f'<a href="https://t.me/{chat["username"]}">{label}</a>'
    else:
        line = label
    return f"{line}  <code>{chat['id']}</code>"


def _build_caption(kind_label, chats, elapsed):
    if not chats:
        return f"» ɴᴏ ᴀᴄᴛɪᴠᴇ {kind_label} ᴄʜᴀᴛs ᴏɴ {app.mention}."
    shown = chats[:DISPLAY_LIMIT]
    body = "\n".join(_entry_line(i, chat) for i, chat in enumerate(shown, start=1))
    remaining = len(chats) - len(shown)
    if remaining > 0:
        body += f"\n\n» ᴀɴᴅ <b>{remaining}</b> ᴍᴏʀᴇ ᴄʜᴀᴛs..."
    return (
        f"<b>» ʟɪsᴛ ᴏғ ᴄᴜʀʀᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ {kind_label} ᴄʜᴀᴛs [{len(chats)}] :</b>\n\n"
        f"{body}\n\n"
        f"⚡ <b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ :</b> <code>{elapsed}s</code>"
    )


def _controls(kind):
    return [
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text="🔄 Refresh",
                    style=ButtonStyle.SUCCESS,
                    callback_data=f"ACTIVE r|{kind}",
                ),
                types.RichMessageButton(
                    text="🗑️ Close",
                    style=ButtonStyle.DANGER,
                    callback_data="ACTIVE x",
                ),
            ]
        )
    ]


async def _fetch(kind):
    if kind == "vc":
        chat_ids = await get_active_chats()
        chats = await _resolve_all(chat_ids, remove_active_chat)
    else:
        chat_ids = await get_active_video_chats()
        chats = await _resolve_all(chat_ids, remove_active_video_chat)
    return chats


async def _render(kind, message):
    label = "ᴠᴏɪᴄᴇ" if kind == "vc" else "ᴠɪᴅᴇᴏ"
    started = time.monotonic()
    chats = await _fetch(kind)
    elapsed = round(time.monotonic() - started, 2)
    caption = _build_caption(label, chats, elapsed)
    blocks = caption_blocks(caption) + _controls(kind)
    return await edit_rich(message, blocks)


async def _launch(message: Message, kind):
    loading = await message.reply_text("» ɢᴇᴛᴛɪɴɢ ᴀᴄᴛɪᴠᴇ ᴄʜᴀᴛs ʟɪsᴛ...")
    try:
        await _render(kind, loading)
    except Exception:
        try:
            await loading.edit_text("» ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴀᴄᴛɪᴠᴇ ᴄʜᴀᴛs.")
        except Exception:
            pass


@app.on_message(filters.command(["activevc", "activevoice", "ac"]) & (filters.user(OWNER_ID) | SUDOERS))
async def activevc(client, message: Message):
    await _launch(message, "vc")


@app.on_message(filters.command(["activev", "activevideo"]) & (filters.user(OWNER_ID) | SUDOERS))
async def activevi_(client, message: Message):
    await _launch(message, "video")


@app.on_callback_query(filters.regex(r"^ACTIVE ") & (filters.user(OWNER_ID) | SUDOERS))
async def active_callback(client, cq):
    action, _sep, kind = cq.data.split(" ", 1)[1].partition("|")
    if action == "x":
        await cq.answer()
        return await cq.message.delete()
    if action != "r":
        return await cq.answer()
    key = (cq.message.chat.id, cq.message.id)
    now = time.monotonic()
    if now - _last_refresh.get(key, 0) < REFRESH_COOLDOWN:
        return await cq.answer("» ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ғᴇᴡ sᴇᴄᴏɴᴅs ʙᴇғᴏʀᴇ ʀᴇғʀᴇsʜɪɴɢ ᴀɢᴀɪɴ.", show_alert=False)
    _last_refresh[key] = now
    await cq.answer("» ʀᴇғʀᴇsʜɪɴɢ...")
    try:
        await _render(kind, cq.message)
    except Exception:
        await cq.answer("» ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇғʀᴇsʜ.", show_alert=True)
