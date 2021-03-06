# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.

import asyncio

from pyrogram import filters

from database.bot_settings_db import (
    add_pm_text,
    get_pm_spam_limit,
    get_pm_text,
    get_thumb,
    add_pm_thumb,
    set_pm_spam_limit,
)
from telegraph import Telegraph, exceptions, upload_file
import os
from database.pmdb import approve_user, disapprove_user, is_user_approved
from main_startup.core.decorators import friday_on_cmd, listen
from main_startup.helper_func.basic_helpers import get_text, edit_or_reply
from main_startup.helper_func.logger_s import LogIt
from main_startup.helper_func.plugin_helpers import convert_to_image

PM_WARNS = {}
OLD_MSG = {}

from plugins import devs_id

try:
    telegraph = Telegraph()
    r = telegraph.create_account(short_name="FridayUserBot.")
    auth_url = r["auth_url"]
except:
    pass

@friday_on_cmd(
    ["setpmtext"],
    cmd_help={
        "help": "Set Custom On Text!",
        "example": "{ch}setpmtext (reply to Pm Text)",
    },
)
async def set_custom_pm_texts(client, message):
    ptext = get_text(message)
    if not ptext:
        if message.reply_to_message.text:
            ptext = message.reply_to_message.text
    if not ptext:
        await message.edit(
            "`Reply To Text Message Or Give To Text As Input To SetAs Custom PM Text`"
        )
        return
    if ptext == "default":
        await add_pm_text()
    else:
        await add_pm_text(ptext)
    await message.edit(f"PM-Message Sucessfully Changed To `{ptext}`")


@friday_on_cmd(
    ["setpmlimit"],
    cmd_help={
        "help": "Set Pm Limit!",
        "example": "{ch}setpmlimit (number between 3-20)",
    },
)
async def set_custom_pm_texts(client, message):
    ptext = get_text(message)
    if not ptext:
        await message.edit("`Give Number Input!`")
        return
    if not ptext.isdigit():
        await message.edit("`Pm Limit Should Be In Numbers From 3-20`")
        return
    if int(ptext) < 3:
        await message.edit("`Pm Limit Should Be In Numbers From 3-20`")
        return
    if int(ptext) >= 20:
        await message.edit("`Pm Limit Should Be In Numbers From 3-20`")
        return
    await set_pm_spam_limit(int(ptext))
    await message.edit(f"PM-Message-Limit Sucessfully Changed To `{ptext}`")


@friday_on_cmd(
    ["block"],
    cmd_help={
        "help": "Block Replied User!",
        "example": "{ch}block (reply to user message)",
    },
)
async def blockz(client, message):
    if message.chat.type == "private":
        user_ = await client.get_users(message.chat.id)
        firstname = user_.first_name
        if await is_user_approved(message.chat.id):
            await disapprove_user(message.chat.id)
        await message.edit(
            "Blocked [{}](tg://user?id={})".format(firstname, message.chat.id)
        )
        await client.block_user(message.chat.id)
        await asyncio.sleep(3)
        await message.delete()
    elif message.chat.type == "supergroup":
        if not message.reply_to_message:
            await message.edit("`Reply To User To Block Him !`")
            return
        user_ = await client.get_users(message.reply_to_message.from_user.id)
        firstname = user_.first_name
        if await is_user_approved(message.reply_to_message.from_user.id):
            await disapprove_user(message.reply_to_message.from_user.id)
        await message.edit(
            "Blocked [{}](tg://user?id={})".format(
                firstname, message.reply_to_message.from_user.id
            )
        )
        await client.block_user(message.reply_to_message.from_user.id)
        await asyncio.sleep(3)
        await message.delete()


@friday_on_cmd(
    ["unblock"],
    cmd_help={
        "help": "Unblock Replied Uset!",
        "example": "{ch}unblock (reply to user message)",
    },
)
async def unmblock(client, message):
    if message.chat.type == "private":
        await asyncio.sleep(3)
        await message.delete()
    elif message.chat.type == "supergroup":
        if not message.reply_to_message:
            await message.edit("`Reply To User To Un-Block Him !`")
            return
        user_ = await client.get_users(message.reply_to_message.from_user.id)
        firstname = user_.first_name
        await message.edit(
            "Un-Blocked [{}](tg://user?id={})".format(
                firstname, message.reply_to_message.from_user.id
            )
        )
        await client.unblock_user(message.reply_to_message.from_user.id)
        await asyncio.sleep(3)
        await message.delete()


@friday_on_cmd(
    ["a", "accept", "allow"],
    cmd_help={
        "help": "Allow User To Pm you!",
        "example": "{ch}a (reply to user message)",
    },
)
async def allow(client, message):
    if message.chat.type == "private":
        if message.chat.id in OLD_MSG:
            await OLD_MSG[message.chat.id].delete()
        user_ = await client.get_users(message.chat.id)
        firstname = user_.first_name
        if not await is_user_approved(message.chat.id):
            await approve_user(message.chat.id)
        else:
            await message.edit("`User is Already Approved!`")
            await asyncio.sleep(3)
            await message.delete()
            return
        await message.edit(
            "Approved to pm [{}](tg://user?id={})".format(firstname, message.chat.id)
        )
        await asyncio.sleep(3)
        await message.delete()
    elif message.chat.type == "supergroup":
        if not message.reply_to_message:
            await message.edit("`Reply To User To Approve Him !`")
            return
        user_ = await client.get_users(message.reply_to_message.from_user.id)
        firstname = user_.first_name
        if not await is_user_approved(message.reply_to_message.from_user.id):
            await approve_user(message.reply_to_message.from_user.id)
        else:
            await message.edit("`User is Already Approved!`")
            await asyncio.sleep(3)
            await message.delete()
            return
        await message.edit(
            "Approved to pm [{}](tg://user?id={})".format(
                firstname, message.reply_to_message.from_user.id
            )
        )
        await asyncio.sleep(3)
        await message.delete()


@friday_on_cmd(
    ["da", "disaccept", "disallow", "disapprove"],
    cmd_help={
        "help": "Disallow User To Pm you!",
        "example": "{ch}da (reply to user message)",
    },
)
async def disallow(client, message):
    if message.chat.type == "private":
        user_ = await client.get_users(message.chat.id)
        firstname = user_.first_name
        if await is_user_approved(message.chat.id):
            await disapprove_user(message.chat.id)
        else:
            await message.edit(
                "`This User Was Never Approved. How Should I Disapprove?`"
            )
            await asyncio.sleep(3)
            await message.delete()
            return
        await message.edit(
            "DisApproved to pm [{}](tg://user?id={})".format(firstname, message.chat.id)
        )
        await asyncio.sleep(3)
        await message.delete()
    elif message.chat.type == "supergroup":
        if not message.reply_to_message:
            await message.edit("`Reply To User To DisApprove Him !`")
            return
        user_ = await client.get_users(message.reply_to_message.from_user.id)
        firstname = user_.first_name
        if await is_user_approved(message.reply_to_message.from_user.id):
            await disapprove_user(message.reply_to_message.from_user.id)
        else:
            await message.edit(
                "`This User Was Never Approved. How Should I Disapprove?`"
            )
            await asyncio.sleep(3)
            await message.delete()
            return
        await message.edit(
            "DisApproved to pm [{}](tg://user?id={})".format(
                firstname, message.reply_to_message.from_user.id
            )
        )
        await asyncio.sleep(3)
        await message.delete()
        
@friday_on_cmd(['setpmpic', 'spp'],
   cmd_help={
        "help": "Set Replied Image As Your Pm Permit Image.",
        "example": "{ch}setpmpic (reply to image)",
    })
async def set_my_pic(client, message):
    ms_ = await edit_or_reply(message, "`Please Wait!`")
    if not (message.reply_to_message or message.reply_to_message.photo or message.reply_to_message.sticker):
        await ms_.edit("`Reply To Image To Set As Your Pm Permit Pic.`")
        return
    if message.reply_to_message.sticker:
        m_d = await convert_to_image(message, client)
    else:
        m_d = await message.reply_to_message.download()
    try:
        media_url = upload_file(m_d)
    except exceptions.TelegraphException as exc:
        await ms_.edit(
                f"`Unable To Upload Media To Telegraph! \nTraceBack : {exc}`"
            )
        os.remove(m_d)
        return
    media_url = f"https://telegra.ph/{media_url[0]}"
    await add_pm_thumb(media_url)
    await ms_.edit("`Sucessfully Set This Image As Pm Permit Image!`")
    os.remove(m_d)
        

@listen(filters.incoming & filters.private & ~filters.edited & ~filters.me)
async def pmPermit(client, message):
    if not message.from_user:
        message.continue_propagation()
    if await is_user_approved(message.chat.id):
        message.continue_propagation()
    if message.from_user.id in devs_id:
        await approve_user(message.chat.id)
        message.continue_propagation()
    user_ = await client.get_users(message.chat.id)
    if user_.is_contact:
        message.continue_propagation()
    if user_.is_bot:
        message.continue_propagation()
    if user_.is_verified:
        message.continue_propagation()
    if user_.id == (await client.get_me()).id:
        message.continue_propagation()
    if user_.is_scam:
        await message.reply_text("`Scammer Aren't Welcome To My Masters PM!`")
        await client.block_user(user_.id)
        message.continue_propagation()
    if user_.is_support:
        message.continue_propagation()
    text = await get_pm_text()
    log = LogIt(message)
    capt = await get_thumb()
    pm_s_ = await get_pm_spam_limit()
    if message.chat.id not in PM_WARNS:
        PM_WARNS[message.chat.id] = 0
    elif PM_WARNS[message.chat.id] >= int(pm_s_):
        await message.reply_text(
            f"`Thats It! I Gave You {int(pm_s_)} Warning. Now Fuck Off. Blocked And Reported!`"
        )
        await client.block_user(user_.id)
        if message.chat.id in OLD_MSG:
            OLD_MSG.pop(message.chat.id)
        if message.chat.id in PM_WARNS:
            PM_WARNS.pop(message.chat.id)
        blockeda = f"**#Blocked_PMPERMIT** \n**User :** `{user_.id}` \n**Reason :** `Spam Limit Reached.`"
        await log.log_msg(client, blockeda)
        message.continue_propagation()
    warnings_got = f"{int(PM_WARNS[message.chat.id]) + 1}/{int(pm_s_)}"
    user_firstname = message.from_user.first_name
    me_f = client.me.first_name
    holy = await message.reply_photo(
        capt,
        caption=text.format(
            user_firstname=user_firstname, warns=warnings_got, boss_firstname=me_f
        ),
    )
    PM_WARNS[message.chat.id] += 1
    if message.chat.id in OLD_MSG:
        await OLD_MSG[message.chat.id].delete()
    OLD_MSG[message.chat.id] = holy
    message.continue_propagation()
