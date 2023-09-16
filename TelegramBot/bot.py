"""Telegram Bot"""
import os.path
import sys
from io import BytesIO

import requests
import yaml
from telegram import Update, File
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext
)

from botReplicas import Replica


# Command Handlers
async def startCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start message"""
    await update.message.reply_markdown(Replica.start)


async def infoCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Statistics"""
    try:
        response = requests.get(BASE_URL + STATISTICS).json()
    except requests.exceptions.ConnectionError:
        # if the server isn`t responding
        await context.bot.send_message(
            chat_id=update.message.chat_id, text=Replica.connectionError
        )
    else:
        # if the response is received
        await update.message.reply_markdown(
            Replica.info % (response["imagesProcessed"], response["wordsParsed"])
        )


async def setLimitCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set new Limit"""
    command = update.message.text.split()
    if len(command) == 2 and command[1].isdigit():
        context.user_data['limit'] = command[1]
        await update.message.reply_markdown(Replica.limitApplied)
    else:
        await update.message.reply_markdown(Replica.notANumber)


# File Handlers
async def photoHandler(update: Update, context: CallbackContext) -> None:
    """Handle photo and send response"""
    mes = await update.message.reply_text(
        Replica.processing, reply_to_message_id=update.message.message_id
    )

    if update.message.photo:
        # Case when photo is sent as a photo
        file: File = await context.bot.get_file(update.message.photo[-1].file_id)
    else:
        # Case when photo is sent as a document
        file: File = await update.message.effective_attachment.get_file()

    # Convert photo to bytes
    byteStream = BytesIO(await file.download_as_bytearray())
    try:
        response = requests.get(
            BASE_URL + TUPLE, data=byteStream, timeout=3,
            params={'limit': context.user_data.get('limit', 5)}
        )
    except requests.exceptions.ConnectionError:
        # if the server isn`t responding
        await context.bot.editMessageText(chat_id=update.message.chat_id,
                                          message_id=mes.message_id,
                                          text=Replica.connectionError)
        return

    await context.bot.deleteMessage(chat_id=update.message.chat_id,
                                    message_id=mes.message_id)

    # Making human-readable message from response
    text = response.json()
    s, tempLen = '', 0
    for i, (target, suggestion) in enumerate(text):
        temp = f'<b>{i + 1}</b>. {target}: {suggestion}\n'
        if len(temp) + tempLen > 4096:
            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=s,
                parse_mode='html'
            )
            s, tempLen = '', 0

        s += temp
        tempLen += len(temp)

    if s:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=s, parse_mode='html'
        )


async def wrongFileTypeHandler(update: Update, context: CallbackContext) -> None:
    """Handle wrong file type"""
    await update.message.reply_text(
        Replica.wrongFileType,
        reply_to_message_id=update.message.message_id
    )


if __name__ == '__main__':
    # Load data from config file
    with open(os.path.join(sys.path[1], 'config.yaml')) as f:
        config = yaml.safe_load(f)

        TOKEN = config['metadata']['TGToken']
        BASE_URL = config['URL']['baseUrl']
        TUPLE = config['URL']['tuple']
        STATISTICS = config['URL']['statistic']

    # Initializing
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', startCommand))
    app.add_handler(CommandHandler('info', infoCommand))
    app.add_handler(CommandHandler('set_limit', setLimitCommand))

    # Files
    app.add_handler(MessageHandler(filters.PHOTO, photoHandler))
    app.add_handler(MessageHandler(filters.Document.IMAGE, photoHandler))
    app.add_handler(MessageHandler(filters.Document.ALL, wrongFileTypeHandler))

    app.run_polling(poll_interval=3)
