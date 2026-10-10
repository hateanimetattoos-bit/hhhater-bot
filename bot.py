import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiohttp import web

# ============================================
#  НАСТРОЙКИ — ЗАПОЛНИ СВОИМИ ДАННЫМИ
# ============================================
BOT_TOKEN = "8891258598:AAHhhEc3quAdsCGwDY0C9w9H4ec56ObId8g"
ADMIN_ID = 1340848500
# ============================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message):
    await message.answer(
        "Привет! Это бот магазина hhhater shop 🖤\n"
        "Заказы оформляются на сайте."
    )


async def handle_order(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if request.method == "OPTIONS":
        return web.json_response({}, headers=headers)

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "bad json"},
                                 status=400, headers=headers)

    name = data.get("name", "—")
    tg = data.get("tg", "—")
    city = data.get("city", "—")
    delivery = data.get("delivery", "—")
    pvz = data.get("pvz", "—")
    comment = data.get("comment", "—").strip() or "—"
    items = data.get("items", [])

    total = sum(i["price"] * i["qty"] for i in items)
    lines = [f"• {i['title']} × {i['qty']} — {i['price'] * i['qty']}₽" for i in items]
    order_text = "\n".join(lines)

    admin_msg = (
        f"🛒 <b>НОВАЯ ЗАЯВКА — hhhater shop</b>\n\n"
        f"👤 Имя: {name}\n"
        f"💬 Телеграм: {tg}\n"
        f"🏙 Город: {city}\n"
        f"🚚 Доставка: {delivery}\n"
        f"📍 ПВЗ: {pvz}\n"
        f"📝 Комментарий: {comment}\n\n"
        f"<b>Товары:</b>\n{order_text}\n\n"
        f"💰 <b>Товары: {total}₽</b>\n"
        f"📦 Доставка: посчитать\n\n"
        f"<i>Напиши клиенту в ЛС, посчитай доставку, отправь карту.</i>"
    )

    try:
        await bot.send_message(ADMIN_ID, admin_msg)
    except Exception as e:
        print("Не смог отправить админу:", e)

    return web.json_response({"ok": True}, headers=headers)


async def main():
    app = web.Application()
    app.router.add_post("/order", handle_order)
    app.router.add_options("/order", handle_order)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    print("✅ Бот запущен. Жду заявки...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())