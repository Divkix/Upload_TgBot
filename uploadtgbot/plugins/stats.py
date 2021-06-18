from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, Message

from uploadtgbot.vars import Vars
from uploadtgbot.bot_class import UploadTgBot
from uploadtgbot.db import MainDB
from uploadtgbot.utils.display_progress import human_bytes
from uploadtgbot.utils.constants import Constants
from uploadtgbot.utils.custom_filters import user_check


@UploadTgBot.on_message(filters.command("stats", Vars.PREFIX_HANDLER) & user_check)
async def stats_bot(_, m: Message):
    stats = await get_stats_func(m.from_user.id, False)
    await m.reply_text(
        stats,
        quote=True,
        reply_markup=Constants.refresh_stats(m.from_user.id, False),
    )
    return


@UploadTgBot.on_message(filters.command("admin_stats", Vars.PREFIX_HANDLER) & filters.user(Vars.OWNER_ID))
async def admin_stats_bot(_, m: Message):
    stats = await get_stats_func(m.from_user.id, True)
    await m.reply_text(
        stats,
        quote=True,
        reply_markup=Constants.refresh_stats(m.from_user.id, True),
    )
    return


@UploadTgBot.on_callback_query(filters.regex("^refresh_"))
async def refresh_stats(_, q: CallbackQuery):
    rtype = q.data.split("_")[1]
    user_id = q.from_user.id

    stats = await get_stats_func(user_id, False)
    kb = Constants.refresh_stats(user_id, False)

    if rtype == "admin":
        kb = Constants.refresh_stats(q.from_user.id, True)
        stats = await get_stats_func(user_id, True)

    try:
        await q.message.edit_text(
            stats,
            reply_markup=kb,
        )
    except MessageNotModified:
        pass
    await q.answer("Refreshed stats!")


@UploadTgBot.on_callback_query(filters.regex("^upgrade_acct"))
async def upgrade_acct(_, q: CallbackQuery):
    await q.answer("Not yet supported!", show_alert=True)


async def get_stats_func(user_id: int, admin: bool):
    if admin:
        total_usage, total_users, total_downloads = MainDB.get_all_usage()
        total_usage = human_bytes(total_usage)  # Convert to human readable format
        stats = (
            "<b>Admin Stats</b>"
            "\n\n"
            f"<b>Total Downloads:</b> <i>{total_downloads}</i>"
            f"\n<b>Total Usage:</b> <i>{total_usage}</i>"
            f"\n<b>Total Users:</b> <i>{total_users}</i>"
        )
    else:
        user_stats = MainDB(user_id).get_info()
        total_usage = human_bytes(user_stats["total_usage"])  # Convert to human readable format
        total_downloads = user_stats["total_downloads"]
        plan = user_stats["plan"]
        join_date = user_stats["join_date"].strftime("%m/%d/%Y, %H:%M:%S")
        stats = (
            f"<b>Downloads:</b> <i>{total_downloads}</i>"
            f"\n<b>Usage:</b> <i>{total_usage}</i>"
            f"\n<b>Plan:</b> <i>{plan}</i>"
            f"\n<b>Joined:<b> <i>{join_date}</i>"
        )
    return stats
