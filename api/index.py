import json
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "8772622488:AAGldCcRLRa-PWFt_wtGftCODyjICF8IGl4"
ADMIN_ID = 6843819642

bot = Bot(token=TOKEN)
dp = Dispatcher()


class ReplyState(StatesGroup):
  waiting_for_reply = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  if message.from_user.id == ADMIN_ID:
    await message.answer(
        "👋 Привет, админ! Бот готов принимать анонимки."
    )
  else:
    await message.answer(
        "✉️ Напиши мне любое сообщение, и я анонимно передам его создателю"
        " бота!"
    )


@dp.message(F.from_user.id != ADMIN_ID)
async def forward_to_admin(message: types.Message):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[
      InlineKeyboardButton(
          text="💬 Ответить", callback_data=f"reply_{message.from_user.id}"
      )
  ]])
  await message.forward(chat_id=ADMIN_ID)
  await bot.send_message(
      chat_id=ADMIN_ID,
      text="👆 Анонимное сообщение выше ⬆️",
      reply_markup=keyboard,
  )
  await message.answer(
      "✅ Твое анонимное сообщение успешно отправлено получателю!"
  )


@dp.callback_query(F.data.startswith("reply_"))
async def process_reply_callback(
    callback: types.CallbackQuery, state: FSMContext
):
  user_id = int(callback.data.split("_")[1])
  await state.update_data(target_user_id=user_id)
  await callback.message.answer(
      "✍️ Введи текст ответа. Он будет отправлен пользователю анонимно:"
  )
  await state.set_state(ReplyState.waiting_for_reply)
  await callback.answer()


@dp.message(ReplyState.waiting_for_reply, F.from_user.id == ADMIN_ID)
async def send_reply_to_user(message: types.Message, state: FSMContext):
  data = await state.get_data()
  target_user_id = data.get("target_user_id")

  try:
    await bot.send_message(
        chat_id=target_user_id,
        text=(
            "📩 **Получен ответ на твое анонимное сообщение:**\n\n"
            f"{message.text}"
        ),
        parse_mode="Markdown",
    )
    await message.answer("✅ Ответ успешно отправлен!")
  except Exception as e:
    await message.answer(f"❌ Ошибка отправки: {e}")

  await state.clear()


# Безопасный обработчик для Vercel
async def app(request):
  try:
    # Получаем тело запроса от Telegram
    body = await request.body()
    if body:
      data = json.loads(body.decode("utf-8"))
      update = types.Update(**data)
      await dp.feed_update(bot, update)
    return {"statusCode": 200, "body": "OK"}
  except Exception as e:
    return {"statusCode": 200, "body": str(e)}
  
