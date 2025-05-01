import os
import torch
import logging
import psycopg2
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext

# Загрузка токена и подключения к базе из переменных окружения
TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

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

# Функция для создания таблицы, если её нет
def create_table_if_not_exists():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violators (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("✅ Таблица violators проверена/создана.")
    except Exception as err:
        logging.error(f"❗ Ошибка при создании таблицы: {err}")

# Сохранение нарушителя
def save_violator(username, message):
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

# Загрузка модели
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH).to(device)

def classify_text(text):
    model.eval()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    pred = torch.argmax(logits, dim=-1).item()
    return "🛑 Nenávistná reč" if pred == 1 else "✅ OK"

async def check_message(update: Update, context: CallbackContext):
    message_text = update.message.text
    result = classify_text(message_text)

    if result == "🛑 Nenávistná reč":
        username = update.message.from_user.username or "unknown"
        await update.message.reply_text("⚠️ Upozornenie! Dodržiavajte kultúru komunikácie.")
        await update.message.delete()
        logging.warning(f"Toxická správa od {username}: {message_text}")
        save_violator(username, message_text)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Ahoj! Sledujem kultúru komunikácie v chate!")

def main():
    create_table_if_not_exists()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    logging.info("✅ Bot started successfully!")
    logging.info("🧪 Выполняется тестовая вставка в базу...")
    save_violator("test_user", "test message")

    app.run_polling()

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
