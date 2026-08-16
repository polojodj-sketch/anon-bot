import asyncio
import os
from aiogram import Bot, Dispatcher
from aiohttp import web

# --- НАСТРОЙКИ ---
TOKEN = '8772622488:AAGldCcRLRa-PWFt_wtGftCODyjICF8IGl4' # Вставьте сюда токен вашего бота!
PORT = int(os.environ.get('PORT', 8080))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (чтобы не засыпал) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Веб-сервер запущен на порту {PORT}")

# --- ЛОГИКА БОТА ---
# Здесь будут ваши хендлеры, например:
# @dp.message()
# async def echo(message):
#     await message.answer(message.text)

async def main():
    # Запускаем веб-часть
    await start_web_server()
    
    # Запускаем бота
    print("Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
