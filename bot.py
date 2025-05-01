import os
import torch
import logging
import psycopg2
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext

# Переменные окружения
TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Путь к модели
MODEL_PATH = "tetianamohorian/hate_speech_model"

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler()
    ]
)

# Сохранение нарушителя в PostgreSQL
def save_violator(username, message):
    """Сохраняет нарушителя в Supabase PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        query = "INSERT INTO violators (username, message) VALUES (%s, %s)"
        cursor.execute(query, (username, message))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("✅ Нарушитель сохранён в базу.")
    except Exception as err:
        logging.error(f"❗ Ошибка PostgreSQL: {err}")

# Загрузка модели и токенизатора
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH).to(device)

# Классификация текста
def classify_text(text):
    model.eval()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    pred = torch.argmax(logits, dim=-1).item()
    result = "🛑 Nenávistná reč" if pred == 1 else "✅ OK"
    logging.info(f"🎯 Классификация: \"{text}\" → {result}")
    return result

# Обработка входящих сообщений
async def check_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    result = classify_text(message_text)
    if result == "🛑 Nenávistná reč":
        username = update.message.from_user.username or "unknown"
        await update.message.reply_text("⚠️ Upozornenie! Dodržiavajte kultúru komunikácie.")
        await update.message.delete()
        logging.warning(f"Toxická správa от {username}: {message_text}")
        logging.info("📥 Сохраняем нарушителя в базу...")
        save_violator(username, message_text)

# Команда /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Ahoj! Sledujem kultúru komunikácie v chate!")

# Запуск Telegram бота
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    logging.info("✅ Bot started successfully!")

    # Тестовая вставка в базу данных
    try:
        logging.info("🧪 Выполняется тестовая вставка в базу...")
        save_violator("test_user", "тестовая запись из Railway")
    except Exception as e:
        logging.error(f"❌ Ошибка при тестовой вставке: {e}")

    app.run_polling()

# Перезапуск при ошибке
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.error(f"❗ Bot crashed with error: {e}")
        finally:
            import time
            logging.info("♻️ Restarting bot in 10 seconds...")
            time.sleep(10)
