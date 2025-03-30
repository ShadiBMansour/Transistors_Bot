

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton,Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import os


TOKEN = os.getenv("BOT_TOKEN")
# Define menu structure based on the provided hierarchy
menu_structure = {
    "main": {"📚 السنة الأولى": "year1"},
    "year1": {
        "📖 الفصل الأول": "semester1",
        "📖 الفصل الثاني": "semester2",
        "🔙 رجوع": "main",
    },
    "semester1": {
        "💻 برمجة 1": "programming1",
        "📐 تحليل 1": "analysis1",
        "🔬 الفيزياء": "physics",
        "🖥️ مبادئ الحاسوب": "computers",
        "📝 اللغة الإنجليزية 1": "english1",
        "📊 الجبر العام": "algebra1",
        "🔙 رجوع": "year1",
    },
    "semester2": {
        "💻 برمجة 2": "programming2",
        "📐 تحليل 2": "analysis2",
        "⚡ الدارات الكهربائية والإلكترونية": "circuits",
        "📊 الجبر الخطي": "linear_algebra",
        "📝 اللغة الإنجليزية 2": "english2",
        "📜 اللغة العربية": "arabic",
        "🏛 الثقافة القومية والاشتراكية": "Thaqafa",
        "🔙 رجوع": "year1",
    },
}

# Generate subjects dynamically
subjects = {
    "programming1": "برمجة 1",
    "analysis1": "تحليل 1",
    "physics": "الفيزياء",
    "computers": "مبادئ الحاسوب",
    "english1": "اللغة الإنجليزية 1",
    "algebra1": "الجبر العام",
    "programming2": "برمجة 2",
    "analysis2": "تحليل 2",
    "circuits": "الدارات الكهربائية والإلكترونية",
    "linear_algebra": "الجبر الخطي",
    "english2": "اللغة الإنجليزية 2",
    "arabic": "اللغة العربية",
    "Thaqafa": "الثقافة القومية والاشتراكية",
}

for subject in subjects:
    menu_structure[subject] = {
        "📂 العملي": f"{subject}_practical",
        "📖 النظري": f"{subject}_theory",
        "❓ الأسئلة": f"{subject}_questions",
        "🔙 رجوع": "semester1" if "1" in subject else "semester2",
    }

# Function to generate inline keyboard dynamically
def generate_keyboard(menu):
    if menu not in menu_structure:
        return None  # Prevent errors
    keyboard = [[InlineKeyboardButton(text, callback_data=callback_data)] for text, callback_data in menu_structure[menu].items()]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("اختر السنة الدراسية:", reply_markup=generate_keyboard("main"))

async def menu_navigation(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    next_menu = query.data
    if next_menu in menu_structure:
        await query.edit_message_text("اختر من القائمة:", reply_markup=generate_keyboard(next_menu))
    else:
        # Handle file sending
        file_path = f"files/{next_menu}.pdf"
        if os.path.exists(file_path):
            await query.message.reply_document(document=open(file_path, "rb"), filename=f"{next_menu}.pdf")
        else:
            await query.message.reply_text("⚠️ الملف غير متوفر حاليًا.")

    
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_navigation, pattern='.*'))
    
    print("🚀 بوت تيليجرام يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
