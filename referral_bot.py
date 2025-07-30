import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔑 Replace your actual token here
TOKEN = "8288675469:AAE9GvC7a-9gMue9gQnovHRUJ58"
CHANNEL_ID = "@onlineearning2026toinfinite"  # Channel username

users_file = "users.json"
REFERRAL_REWARD = 10
DAILY_BONUS = 5
MIN_WITHDRAWAL = 100

def load_users():
    try:
        with open(users_file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(users_file, "w") as f:
        json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    users = load_users()

    # 🔐 Check if user joined channel
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user.id)
        if member.status not in ["member", "administrator", "creator"]:
            await update.message.reply_text(
                f"🚫 Please join our channel first:\n👉 {CHANNEL_ID}\n\nUske baad /start dobara bhejo."
            )
            return
    except:
        await update.message.reply_text("⚠️ Bot ko channel me admin rights do pehle.")
        return

    # 🧾 New user registration with referral
    if user_id not in users:
        ref_code = context.args[0] if context.args else None
        users[user_id] = {"balance": 0, "referrals": [], "last_bonus": 0}

        if ref_code and ref_code in users and user_id not in users[ref_code]["referrals"]:
            users[ref_code]["balance"] += REFERRAL_REWARD
            users[ref_code]["referrals"].append(user_id)

        save_users(users)

    # ⌨️ Menu
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus")],
        [InlineKeyboardButton("🔗 Referral Link", callback_data="refer")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
    ]
    await update.message.reply_text("🎉 Welcome to Refer to Earn Bot!", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    users = load_users()

    if user_id not in users:
        await query.edit_message_text("⚠️ Please send /start to register.")
        return

    if query.data == "balance":
        bal = users[user_id]["balance"]
        await query.edit_message_text(f"💼 Your balance: ₹{bal}")

    elif query.data == "refer":
        ref_link = f"https://t.me/onlineearningreferearn_bot?start={user_id}"
        await query.edit_message_text(f"🔗 Your referral link:\n{ref_link}\n\n👥 Earn ₹10 per referral!")

    elif query.data == "bonus":
        current = int(time.time())
        last = users[user_id].get("last_bonus", 0)
        if current - last >= 86400:
            users[user_id]["balance"] += DAILY_BONUS
            users[user_id]["last_bonus"] = current
            save_users(users)
            await query.edit_message_text("🎁 Daily bonus ₹5 added to your balance!")
        else:
            await query.edit_message_text("⏳ You’ve already claimed your bonus. Try again later.")

    elif query.data == "withdraw":
        bal = users[user_id]["balance"]
        if bal >= MIN_WITHDRAWAL:
            await query.edit_message_text("✅ Withdrawal request received. We'll process it soon.")
            users[user_id]["balance"] = 0
            save_users(users)
        else:
            await query.edit_message_text("❌ Minimum ₹100 required to withdraw.")

def main():
    print("✅ Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
