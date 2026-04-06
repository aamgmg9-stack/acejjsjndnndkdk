import telebot
import sqlite3
import random
import time
from telebot import types
from datetime import datetime

# --- CONFIGURATION ---
API_TOKEN = '8592945751:AAFFu9HlBQ4JmrTMejihTXHPYPWwuffgKoU'
ADMIN_ID = 7986980396  
ADMIN_PASSWORD = "demonACE" 
ADMIN_USERNAME = "@Ace_TM" 

bot = telebot.TeleBot(API_TOKEN)

# --- COURSE DATA ---
COURSES = {
    "1": {"name": "Sketchware for Phisher", "coins": 1500},
    "2": {"name": "Android Hacking", "coins": 3000},
    "3": {"name": "Termux For Hackers", "coins": 5000},
    "4": {"name": "Malicious For Legends", "coins": 5000},
    "5": {"name": "Python For Hackers", "coins": 5000}
}

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('cyber_lab_pro.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, username TEXT, coins INTEGER DEFAULT 0, 
                       referred_by INTEGER, last_checkin TEXT, status TEXT DEFAULT 'active')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, bet_num TEXT, 
                       result_num TEXT, amount INTEGER, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- KEYBOARDS ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🕹 Start Game", callback_data="play_game"),
        types.InlineKeyboardButton("💰 Balance", callback_data="check_balance"),
        types.InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus"),
        types.InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
        types.InlineKeyboardButton("👥 Referral", callback_data="referral"),
        types.InlineKeyboardButton("📜 History", callback_data="history"),
        types.InlineKeyboardButton("🎓 Courses", callback_data="courses"),
        types.InlineKeyboardButton("❓ Help", callback_data="help")
    )
    return markup

def admin_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("📊 User Stats", callback_data="admin_stats"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")
    )
    return markup

# --- SLOT ANIMATION ---
def run_slot_animation(chat_id, user_num, bot_result):
    msg = bot.send_message(chat_id, "🎰 <b>Rolling...</b>\n[ ❓ ] [ ❓ ] [ ❓ ]", parse_mode="HTML")
    time.sleep(1)
    bot.edit_message_text(f"🎰 <b>Rolling...</b>\n[ {bot_result[0]} ] [ ❓ ] [ ❓ ]", chat_id, msg.message_id, parse_mode="HTML")
    time.sleep(0.8)
    bot.edit_message_text(f"🎰 <b>Rolling...</b>\n[ {bot_result[0]} ] [ {bot_result[1]} ] [ ❓ ]", chat_id, msg.message_id, parse_mode="HTML")
    time.sleep(0.8)
    
    final_text = (
        f"🎰 <b>Game Result</b>\n"
        f"------------------\n"
        f"ထွက်ဂဏန်း: [ {bot_result[0]} ] [ {bot_result[1]} ] [ {bot_result[2]} ]\n"
        f"သင့်ဂဏန်း: <b>{user_num}</b>\n"
        f"------------------\n"
        f"❌ ကံမကောင်းပါဘူး! နောက်တစ်ကြိမ် ထပ်ကြိုးစားပါ။"
    )
    bot.edit_message_text(final_text, chat_id, msg.message_id, parse_mode="HTML", reply_markup=main_menu())

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    
    # Referral Logic
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 and args[1].isdigit() else None

    conn = sqlite3.connect('cyber_lab_pro.db')
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (id, username, referred_by) VALUES (?, ?, ?)", (user_id, username, referrer_id))
        if referrer_id:
            cursor.execute("UPDATE users SET coins = coins + 50 WHERE id = ?", (int(referrer_id),))
            try: bot.send_message(referrer_id, "👥 <b>Referral Alert!</b>\nလူသစ်ခေါ်ယူမှုအတွက် 50 Coins ရရှိပါပြီ!", parse_mode="HTML")
            except: pass
    
    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, f"🛡 <b>Cyber Lab 3D PRO</b>\n\nမင်္ဂလာပါ {username}!\nဂိမ်းကစားပြီး Cyber Security သင်တန်းများ ရယူပါ။", 
                     parse_mode="HTML", reply_markup=main_menu())

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠 <b>Admin Dashboard</b>", parse_mode="HTML", reply_markup=admin_menu())

@bot.message_handler(commands=['bet'])
def bet_cmd(message):
    user_id = message.from_user.id
    try:
        _, num, amount = message.text.split()
        amount = int(amount)
        if len(num) != 3 or not num.isdigit(): return

        conn = sqlite3.connect('cyber_lab_pro.db')
        cursor = conn.cursor()
        cursor.execute("SELECT coins FROM users WHERE id = ?", (user_id,))
        res = cursor.fetchone()
        coins = res[0] if res else 0

        if coins >= amount:
            cursor.execute("UPDATE users SET coins = coins - ? WHERE id = ?", (amount, user_id))
            all_nums = [str(i).zfill(3) for i in range(1000)]
            if num in all_nums: all_nums.remove(num)
            res_num = random.choice(all_nums)

            cursor.execute("INSERT INTO history (user_id, bet_num, result_num, amount, date) VALUES (?, ?, ?, ?, ?)",
                           (user_id, num, res_num, amount, datetime.now().strftime("%d/%m %I:%M%p")))
            conn.commit()
            conn.close()
            run_slot_animation(message.chat.id, num, res_num)
        else:
            bot.reply_to(message, "💸 Coin မလုံလောက်ပါ။ Admin ဆီမှာ ဝယ်ယူပါ။")
    except:
        bot.reply_to(message, "⚠️ Usage: <code>/bet 123 500</code>", parse_mode="HTML")

@bot.message_handler(commands=['addcoin'])
def add_coin(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        if len(parts) != 4:
            bot.reply_to(message, "⚠️ Usage: `/addcoin ID Amount Password`")
            return
        tid, amt, pswd = parts[1], parts[2], parts[3]
        if pswd == ADMIN_PASSWORD:
            conn = sqlite3.connect('cyber_lab_pro.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET coins = coins + ? WHERE id = ?", (int(amt), int(tid)))
            conn.commit()
            conn.close()
            bot.reply_to(message, f"✅ User {tid} ဆီသို့ {amt} Coins ထည့်ပြီးပါပြီ။")
    except: pass

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    uid = call.from_user.id
    conn = sqlite3.connect('cyber_lab_pro.db')
    cursor = conn.cursor()

    if call.data == "back_to_main":
        bot.edit_message_text("🛡 <b>Main Menu</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=main_menu())

    elif call.data == "play_game":
        bot.send_message(call.message.chat.id, "🕹 <b>ဂိမ်းကစားရန်:</b>\n\n<code>/bet [ဂဏန်း၃လုံး] [ပမာဏ]</code>\nဥပမာ- <code>/bet 123 500</code>", parse_mode="HTML")

    elif call.data == "daily_bonus":
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT last_checkin FROM users WHERE id = ?", (uid,))
        res = cursor.fetchone()
        last = res[0] if res else None
        if last != today:
            cursor.execute("UPDATE users SET coins = coins + 10, last_checkin = ? WHERE id = ?", (today, uid))
            conn.commit()
            bot.answer_callback_query(call.id, "🎁 Daily Bonus 10 Coins ရရှိပါပြီ!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ ဒီနေ့အတွက် ယူပြီးပါပြီ။", show_alert=True)

    elif call.data == "leaderboard":
        cursor.execute("SELECT username, coins FROM users ORDER BY coins DESC LIMIT 10")
        rows = cursor.fetchall()
        text = "🏆 <b>Top 10 Leaderboard</b>\n\n"
        for i, r in enumerate(rows, 1): text += f"{i}. {r[0]} - {r[1]}c\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=main_menu())

    elif call.data == "referral":
        bot_info = bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={uid}"
        bot.edit_message_text(f"👥 <b>Referral System</b>\n\nLink ဖြင့် လူခေါ်လျှင် တစ်ယောက်ကို 50 Coins ရပါမယ်!\nLink: <code>{link}</code>", 
                              call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=main_menu())

    elif call.data == "history":
        cursor.execute("SELECT bet_num, result_num, amount, date FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 5", (uid,))
        rows = cursor.fetchall()
        text = "📜 <b>နောက်ဆုံးမှတ်တမ်း ၅ ခု</b>\n\n"
        if rows:
            for r in rows: text += f"📅 {r[3]}\nထိုး: {r[0]} | ထွက်: {r[1]} | {r[2]}c\n---\n"
        else: text += "မှတ်တမ်းမရှိသေးပါ။"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=main_menu())

    elif call.data == "check_balance":
        cursor.execute("SELECT coins FROM users WHERE id = ?", (uid,))
        res = cursor.fetchone()
        bot.answer_callback_query(call.id, f"💰 လက်ကျန်: {res[0] if res else 0} Coins", show_alert=True)

    elif call.data == "courses":
        text = "<b>🎓 Available Courses</b>\n\n"
        for cid, data in COURSES.items(): text += f"{cid}. {data['name']} - {data['coins']}c\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=main_menu())

    elif call.data == "help":
        txt = "<b>❓ အသုံးပြုပုံ</b>\n\n1. /bet [ဂဏန်း] [ပမာဏ] ဖြင့်ကစားပါ။\n2. Button များကို အသုံးပြုပါ။\n3. Coin ပြည့်လျှင် Admin ကို ဆက်သွယ်ပါ။"
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=main_menu())

    # --- ADMIN CALLBACKS ---
    elif call.data == "admin_stats":
        if uid == ADMIN_ID:
            cursor.execute("SELECT COUNT(*), SUM(coins) FROM users")
            res = cursor.fetchone()
            bot.edit_message_text(f"📊 <b>Bot Stats</b>\n\nUsers: {res[0]}\nTotal System Coins: {res[1] or 0}", 
                                  call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=admin_menu())

    elif call.data == "admin_broadcast":
        if uid == ADMIN_ID:
            msg = bot.send_message(call.message.chat.id, "📢 Broadcast လုပ်မည့်စာသား ပို့ပေးပါ။")
            bot.register_next_step_handler(msg, exec_broadcast)

    conn.close()

def exec_broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    conn = sqlite3.connect('cyber_lab_pro.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    conn.close()
    count = 0
    for u in users:
        try:
            bot.send_message(u[0], f"📢 <b>Broadcast Message</b>\n\n{message.text}", parse_mode="HTML")
            count += 1
        except: pass
    bot.send_message(message.chat.id, f"✅ User {count} ယောက်ကို ပို့ပြီးပါပြီ။")

print("Cyber Lab PRO Final is Running...")
bot.polling()
