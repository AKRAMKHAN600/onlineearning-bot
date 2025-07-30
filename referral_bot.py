from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import datetime
import telegram.error

# Replace with your bot token
TOKEN = "8288675469:AAE9GvC7a-9gMue9gQnovHRUJ58UbcG_8bk"
CHANNEL_USERNAME = "onlineearning2026toinfinite"  # Only the username, no @ or link

# In-memory user data
users = {}

# --- Helper functions ---

def get_ref_link(user_id):
    return f"https://t.me/Onlineearningreferearn_bot?start={user_id}"

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("💸 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus")],
        [InlineKeyboardButton("👫 Refer & Earn", callback_data="refer")],
        [InlineKeyboardButton("📤 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("❓ How to Earn", callback_data="how")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def check_user_joined(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return member.status in ["member", "creator", "administrator"]
    except telegram.error.TelegramError:
        return False

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    args = context.args

    joined = await check_user_joined(user_id, context)
    if not joined:
        join_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ I Joined", callback_data="check_joined")]
        ])
        await update.message.reply_text(
            "🚫 You must join our channel to use this bot.",
            reply_markup=join_button
        )
        return

    # First time user init
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "referrals": [],
            "last_bonus": None
        }

        # Handle referral
        if args:
            ref_id = int(args[0])
            if ref_id != user_id and user_id not in users.get(ref_id, {}).get("referrals", []):
                if ref_id in users:
                    users[ref_id]["balance"] += 10
                    users[ref_id]["referrals"].append(user_id)

    await update.message.reply_text(
        f"👋 Welcome {user.first_name} to *Refer to Earn🤑easy😈*\n\n"
        f"✅ You’ve joined the channel!\nLet’s start earning.",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "balance":
        balance = users.get(user_id, {}).get("balance", 0)
        await query.edit_message_text(f"💰 Your current balance is ₹{balance}")

    elif query.data == "bonus":
        await query.edit_message_text("🎁 Daily bonus feature coming soon!")

    elif query.data == "withdraw":
        await query.edit_message_text("💸 Withdraw option coming soon!")

    elif query.data == "how":
        await query.edit_message_text("❓ Invite friends using your referral link and earn ₹10!")

    elif query.data == "refer":
        ref_link = get_ref_link(user_id)
        await query.edit_message_text(
            text=f"🔗 Your referral link:\n{ref_link}\n\n👥 Invite friends & earn ₹10 per referral!"
        )

    user_data = users.get(user_id)
    if not user_data:
        await query.edit_message_text("⚠️ Please send /start first.")
        return

    if data == "balance":
        await query.edit_message_text(
            f"💰 Your Balance: ₹{user_data['balance']}\n"
            f"👫 Referrals: {len(user_data['referrals'])}",
            reply_markup=get_main_menu()
        )

    elif data == "bonus":
        today = datetime.date.today()
        if user_data["last_bonus"] == today:
            msg = "🎁 You already claimed your daily bonus today!"
        else:
            user_data["balance"] += 5
            user_data["last_bonus"] = today
            msg = "✅ ₹5 Daily Bonus Added!"
        await query.edit_message_text(msg, reply_markup=get_main_menu())

    elif data == "refer":
        ref_link = get_ref_link(user_id)
        await query.edit_message_text(
            f"👫 *Refer & Earn ₹10 per user!*\n\n"
            f"🔗 Your Link:\n{ref_link}",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )

    elif data == "withdraw":
        if user_data["balance"] >= 100:
            await query.edit_message_text(
                "✅ Withdrawal Requested Successfully!\n📩 You will be contacted soon.",
                reply_markup=get_main_menu()
            )
            user_data["balance"] = 0  # Reset after request
        else:
            await query.edit_message_text(
                "❌ Minimum ₹100 required to withdraw!",
                reply_markup=get_main_menu()
            )

    elif data == "how":
        await query.edit_message_text(
            "💡 *How to Earn?*\n\n"
            "1. Invite your friends using your referral link.\n"
            "2. Earn ₹10 per valid user.\n"
            "3. Claim ₹5 Daily Bonus.\n"
            "4. Withdraw when balance is ₹100+ 💸",
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )

# --- Main ---
def main():
    print("✅ Bot is starting...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    app.run_polling()

if __name__ == "__main__":
    main()
