import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from analysis import analyze_pair, plot_indicators
from pairs import normal_pairs, otc_pairs

BOT_TOKEN = os.getenv("7986353305:AAF-eHWhKHOvpRLpba0GkXzAC3HKi7GtivM")
bot = Bot(token="7986353305:AAF-eHWhKHOvpRLpba0GkXzAC3HKi7GtivM")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    choosing_pair = State()
    choosing_interval = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for pair in normal_pairs:
        keyboard.insert(InlineKeyboardButton(pair, callback_data=f"pair:{pair}"))
    for pair in otc_pairs:
        keyboard.insert(InlineKeyboardButton(f"{pair} OTC", callback_data=f"pair:{pair}"))
    await message.answer("👋 Обери торгову пару:", reply_markup=keyboard)
    await Form.choosing_pair.set()

@dp.callback_query_handler(lambda c: c.data.startswith("pair:"), state=Form.choosing_pair)
async def process_pair(callback_query: types.CallbackQuery, state: FSMContext):
    pair = callback_query.data.split(":")[1]
    await state.update_data(pair=pair)
    keyboard = InlineKeyboardMarkup(row_width=3)
    for i in ["1m", "5m", "15m"]:
        keyboard.insert(InlineKeyboardButton(i, callback_data=f"interval:{i}"))
    await bot.send_message(callback_query.from_user.id, "⏱ Обери таймфрейм:", reply_markup=keyboard)
    await Form.choosing_interval.set()

@dp.callback_query_handler(lambda c: c.data.startswith("interval:"), state=Form.choosing_interval)
async def process_interval(callback_query: types.CallbackQuery, state: FSMContext):
    interval = callback_query.data.split(":")[1]
    data = await state.get_data()
    pair = data['pair']
    await bot.send_message(callback_query.from_user.id, f"📊 Аналіз {pair} на таймфреймі {interval}...")

    result = analyze_pair(pair, interval)

    if "error" in result:
        await bot.send_message(callback_query.from_user.id, f"❌ Помилка: {result['error']}")
        return

    message = (
        f"📈 *{pair} ({interval})*\n\n"
        f"🔼 Buy: {result['BUY']}\n"
        f"🔽 Sell: {result['SELL']}\n"
        f"➖ Neutral: {result['NEUTRAL']}\n"
        f"\n📍 Рекомендація: *{result['RECOMMENDATION']}*"
        f"\n⏱ Експірація: *3 хвилини*"
    )
    await bot.send_message(callback_query.from_user.id, message, parse_mode="Markdown")

    img_path = plot_indicators(result["INDICATORS"], pair)
    with open(img_path, 'rb') as photo:
        await bot.send_photo(callback_query.from_user.id, photo)
    os.remove(img_path)
    await state.finish()

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
