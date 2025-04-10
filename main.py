from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import os
import json

# استبدل التوكن الخاص بك هنا
TOKEN = os.getenv("BOT_TOKEN")

# تحميل ملف JSON
with open("content_map.json", encoding="utf-8") as f:
    content_map = json.load(f)

# تعريف بنية القوائم
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
        "📊 الجبر الخطي": "algebra2",
        "📝 اللغة الإنجليزية 2": "english2",
        "📜 اللغة العربية": "arabic",
        "🏛 الثقافة القومية والاشتراكية": "national",
        "🔙 رجوع": "year1",
    },
}

# المواد والتفرعات
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
    "algebra2": "الجبر الخطي",
    "english2": "اللغة الإنجليزية 2",
    "arabic": "اللغة العربية",
    "national": "الثقافة القومية والاشتراكية",
}

# بناء القوائم الفرعية
for subject in subjects:
    if subject == "physics":
        menu_structure[subject] = {
            "📖 المحاضرات": f"{subject}_lectures",
            "📝 الملخصات": f"{subject}_summaries",
            "❓ الأسئلة": f"{subject}_questions",
            "🔙 رجوع": "semester1",
        }
    elif subject == "circuits":
        menu_structure[subject] = {
            "📖 المحاضرات": f"{subject}_lectures",
            "❓ الأسئلة": f"{subject}_questions",
            "🔙 رجوع": "semester2",
        }
    elif subject in ["english1", "english2"]:
        menu_structure[subject] = {
            "📘 المقرر": f"{subject}_curriculum",
            "📖 محاضرات RBCs": f"{subject}_rbcs",
            "❓ الأسئلة": f"{subject}_questions",
            "🔙 رجوع": "semester1" if subject == "english1" else "semester2",
        }
    elif subject in ["arabic", "national"]:
        menu_structure[subject] = {
            "📘 المقرر": f"{subject}_curriculum",
            "🔙 رجوع": "semester2",
        }
    elif subject in ["programming1", "programming2"]:
        menu_structure[subject] = {
            "📂 عملي TD": f"{subject}_practical_td",
            "🧪 عملي مخابر": f"{subject}_practical_laporatores",
            "📖 النظري": f"{subject}_theoretical",
            # "❓ الأسئلة": f"{subject}_questions",
            "❓ نماذج دورات": f"{subject}_questionspatterns",
            "🔙 رجوع": "semester1" if subject == "programming1" else "semester2",
        }
    elif subject == "computers":
        menu_structure[subject] = {
            "📂 العملي": f"{subject}_practical",
            "📖 النظري": f"{subject}_theoretical",
            #"❓ الأسئلة": f"{subject}_questions",
            "🔙 رجوع": "semester1",
        }
    else:
        menu_structure[subject] = {
            "📂 العملي": f"{subject}_practical",
            "📖 النظري": f"{subject}_theoretical",
            "❓ الأسئلة": f"{subject}_questions",
            "🔙 رجوع": "semester1" if "1" in subject else "semester2",
        }

# توليد الأزرار
def generate_keyboard(menu):
    if menu not in menu_structure:
        return None
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in menu_structure[menu].items()]
    return InlineKeyboardMarkup(keyboard)

# أمر البدء
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("📚 اختر السنة الدراسية:", reply_markup=generate_keyboard("main"))

# التعامل مع القوائم والبيانات من JSON
async def menu_navigation(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    next_menu = query.data

    if next_menu in content_map:
        entry = content_map[next_menu]
        entry_type = entry["type"]

        # يدعم نوع مزدوج ["file", "forward"]
        if isinstance(entry_type, list):
            if "file" in entry_type and "files" in entry:
                for file in entry["files"]:
                    path = f"files/{file}.pdf"
                    if os.path.exists(path):
                        await query.message.reply_document(document=open(path, "rb"))
            if "forward" in entry_type and "message_ids" in entry:
                for msg_id in entry["message_ids"]:
                    await context.bot.copy_message(
                        chat_id=query.message.chat_id,
                        from_chat_id=entry["chat_id"],
                        message_id=msg_id,
                    )
            return

        # إرسال ملفات PDF من مجلد files/
        if entry_type == "file":
            for file in entry["files"]:
                file_path = f"files/{file}.pdf"
                if os.path.exists(file_path):
                    await query.message.reply_document(document=open(file_path, "rb"))
                else:
                    await query.message.reply_text("⚠️هذا الملف غير متوفر حاليا.")
            return

        # إعادة توجيه رسائل
        if entry_type == "forward":
            for msg_id in entry["message_ids"]:
                await context.bot.copy_message(
                    chat_id=query.message.chat_id,
                    from_chat_id=entry["chat_id"],
                    message_id=msg_id,
                )
            return

    if next_menu in menu_structure:
        await query.edit_message_text("📂 اختر من القائمة:", reply_markup=generate_keyboard(next_menu))
    else:
        await query.message.reply_text("⚠️ هذا الخيار غير مدعوم أو غير معروف.")

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_navigation, pattern=".*"))
    print("✅ البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
