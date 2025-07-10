import logging
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler
)
import db
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client (optional)
openai_api_key = os.getenv('OPENAI_API_KEY') or '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'
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
    logger.info("OpenAI API подключен успешно.")
else:
    client = None
    logger.warning("OPENAI_API_KEY не установлен. AI-поиск будет недоступен.")

# States for ConversationHandler
(
    MAIN_MENU,
    HELP_MENU,
    ADD_NAME, ADD_JOB, ADD_EXPERIENCE, ADD_HELP, ADD_CONTACTS,
    EDIT_MENU, EDIT_FIELD, EDIT_VALUE,
    NEED_HELP_ASK,
    PROFILE_COMPLETED,
    SEARCH_HELPERS
) = range(13)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.init_db()
    
    # Set up menu commands when bot starts
    await setup_menu_commands(context.application)
    
    keyboard = [
        [InlineKeyboardButton("Я хочу помочь", callback_data="want_to_help")],
        [InlineKeyboardButton("Мне нужна помощь", callback_data="need_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Добро пожаловать! Чем я могу вам помочь?',
        reply_markup=reply_markup
    )
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Операция отменена.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def show_my_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = db.get_helper(user_id)
    if profile:
        text = (f"Ваш профиль:\n\n"
                f"👤 Имя: {profile['name']}\n"
                f"💼 Профессия: {profile['job']}\n"
                f"📅 Опыт: {profile['experience']}\n"
                f"🤝 Чем можете помочь: {profile['help']}\n"
                f"📞 Контакты: {profile['contacts']}")
    else:
        text = "У вас еще нет профиля."
    await update.message.reply_text(text)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "want_to_help":
        keyboard = [
            [InlineKeyboardButton("Добавить профиль", callback_data="add_profile")],
            [InlineKeyboardButton("Редактировать профиль", callback_data="edit_profile")],
            [InlineKeyboardButton("Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text='Выберите действие:',
            reply_markup=reply_markup
        )
        return HELP_MENU
    elif query.data == "need_help":
        await query.edit_message_text('Какая помощь вам нужна?')
        return NEED_HELP_ASK
    else:
        await query.edit_message_text('Пожалуйста, выберите вариант из меню.')
        return MAIN_MENU

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_profile":
        await query.edit_message_text('Как вас зовут?')
        return ADD_NAME
    elif query.data == "edit_profile":
        await query.edit_message_text('Функция редактирования профиля скоро будет доступна!')
        return ConversationHandler.END
    elif query.data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("Я хочу помочь", callback_data="want_to_help")],
            [InlineKeyboardButton("Мне нужна помощь", callback_data="need_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text='Вы вернулись в главное меню.',
            reply_markup=reply_markup
        )
        return MAIN_MENU
    else:
        await query.edit_message_text('Пожалуйста, выберите вариант из меню.')
        return HELP_MENU

async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text('Ваша профессия?')
    return ADD_JOB

async def add_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['job'] = update.message.text
    await update.message.reply_text('Ваш опыт работы?')
    return ADD_EXPERIENCE

async def add_experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['experience'] = update.message.text
    await update.message.reply_text('Чем вы можете помочь?')
    return ADD_HELP

async def add_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['help'] = update.message.text
    await update.message.reply_text('Ваши контакты (телефон, Telegram, email и т.д.)?')
    return ADD_CONTACTS

async def add_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contacts'] = update.message.text
    user_id = update.effective_user.id
    db.add_helper(
        user_id,
        context.user_data['name'],
        context.user_data['job'],
        context.user_data['experience'],
        context.user_data['help'],
        context.user_data['contacts']
    )
    profile_text = (
        'Спасибо за вашу помощь! Вот ваши данные:\n\n'
        f'👤 Имя: {context.user_data["name"]}\n'
        f'💼 Профессия: {context.user_data["job"]}\n'
        f'📅 Опыт: {context.user_data["experience"]}\n'
        f'🤝 Чем можете помочь: {context.user_data["help"]}\n'
        f'📞 Контакты: {context.user_data["contacts"]}\n\n'
        'Что вы хотите сделать дальше?'
    )
    keyboard = [
        [InlineKeyboardButton("🏠 Вернуться в главное меню", callback_data="back_to_main_from_profile")],
        [InlineKeyboardButton("👤 Посмотреть мой профиль", callback_data="show_my_profile")],
        [InlineKeyboardButton("✅ Завершить", callback_data="finish_profile")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        profile_text,
        reply_markup=reply_markup
    )
    return PROFILE_COMPLETED


async def need_help_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_response = update.message.text
    context.user_data['help_request'] = user_response
    
    # Проверяем, есть ли помощники в базе
    helpers_count = db.get_helpers_count()
    if helpers_count == 0:
        await update.message.reply_text(
            f'Спасибо! Вы запросили: "{user_response}"\n\n'
            'К сожалению, пока нет доступных помощников в базе данных. '
            'Ваш запрос будет рассмотрен, когда появятся желающие помочь.'
        )
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("🤖 Найти лучших помощников с AI", callback_data="find_ai_helpers")],
        [InlineKeyboardButton("❌ Отменить поиск", callback_data="cancel_search")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f'Спасибо! Вы запросили: "{user_response}"\n\n'
        f'В базе данных есть {helpers_count} помощников. Хотите найти подходящего помощника с помощью AI?',
        reply_markup=reply_markup
    )
    return SEARCH_HELPERS

async def profile_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_main_from_profile":
        keyboard = [
            [InlineKeyboardButton("Я хочу помочь", callback_data="want_to_help")],
            [InlineKeyboardButton("Мне нужна помощь", callback_data="need_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text='Вы вернулись в главное меню.',
            reply_markup=reply_markup
        )
        return MAIN_MENU
    elif query.data == "show_my_profile":
        user_id = query.from_user.id
        profile = db.get_helper(user_id)
        if profile:
            text = (f"Ваш профиль:\n\n"
                    f"👤 Имя: {profile['name']}\n"
                    f"💼 Профессия: {profile['job']}\n"
                    f"📅 Опыт: {profile['experience']}\n"
                    f"🤝 Чем можете помочь: {profile['help']}\n"
                    f"📞 Контакты: {profile['contacts']}")
        else:
            text = "У вас еще нет профиля."
        await query.edit_message_text(text)
        return ConversationHandler.END
    elif query.data == "finish_profile":
        await query.edit_message_text('Спасибо за использование бота!')
        return ConversationHandler.END
    else:
        await query.edit_message_text('Пожалуйста, выберите вариант из меню.')
        return PROFILE_COMPLETED

async def find_best_helpers_with_ai(help_request: str) -> list:
    """Найти лучших помощников с помощью ChatGPT API"""
    try:
        # Проверяем, доступен ли OpenAI клиент
        if client is None:
            logger.warning("OpenAI API недоступен. Возвращаем всех помощников.")
            all_helpers = db.get_all_helpers()
            return all_helpers[:3]
        
        # Получаем всех помощников из базы данных
        all_helpers = db.get_all_helpers()
        
        if not all_helpers:
            return []
        
        # Формируем промпт для ChatGPT
        helpers_info = []
        for i, helper in enumerate(all_helpers):
            helpers_info.append(f"{i+1}. Имя: {helper['name']}, Профессия: {helper['job']}, Опыт: {helper['experience']}, Может помочь: {helper['help']}")
        
        prompt = f"""
Запрос пользователя: "{help_request}"

Доступные помощники:
{chr(10).join(helpers_info)}

Пожалуйста, проанализируй запрос пользователя и выбери ТОП-3 наиболее подходящих помощников. 
Учитывай профессию, опыт и описание того, чем может помочь каждый помощник.

Верни ответ в формате JSON с массивом индексов (начиная с 0) лучших помощников:
{{"best_helpers": [индекс1, индекс2, индекс3]}}

Например: {{"best_helpers": [0, 2, 1]}}
"""
        
        # Отправляем запрос к ChatGPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощник для анализа запросов и подбора специалистов. Отвечай только в формате JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        # Парсим ответ
        ai_response = response.choices[0].message.content.strip()
        result = json.loads(ai_response)
        
        # Получаем лучших помощников по индексам
        best_helpers = []
        for idx in result.get("best_helpers", []):
            if 0 <= idx < len(all_helpers):
                best_helpers.append(all_helpers[idx])
        
        return best_helpers[:3]  # Возвращаем максимум 3
        
    except Exception as e:
        logger.error(f"Ошибка при поиске помощников с AI: {e}")
        # В случае ошибки возвращаем всех помощников
        all_helpers = db.get_all_helpers()
        return all_helpers[:3]

async def search_helpers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "find_ai_helpers":
        # Получаем запрос пользователя из контекста
        help_request = context.user_data.get('help_request', '')
        
        # Показываем сообщение о том, что AI анализирует запрос
        if client is not None:
            await query.edit_message_text("🤖 AI анализирует ваш запрос и ищет лучших помощников...")
        else:
            await query.edit_message_text("🔍 Ищем подходящих помощников...")
        
        # Ищем лучших помощников с помощью AI
        best_helpers = await find_best_helpers_with_ai(help_request)
        
        if best_helpers:
            if client is not None:
                response = f"🤖 AI проанализировал ваш запрос: \"{help_request}\"\n\n"
                response += "🎯 Вот ТОП-3 наиболее подходящих помощников:\n\n"
            else:
                response = f"📋 Ваш запрос: \"{help_request}\"\n\n"
                response += "👥 Вот доступные помощники:\n\n"
            
            for i, helper in enumerate(best_helpers, 1):
                response += (f"{i}. 👤 {helper['name']}\n"
                           f"   💼 {helper['job']}\n"
                           f"   📅 Опыт: {helper['experience']}\n"
                           f"   🤝 {helper['help']}\n"
                           f"   📞 {helper['contacts']}\n\n")
            
            response += "Вы можете связаться с любым из них напрямую."
        else:
            response = "К сожалению, подходящих помощников не найдено."
        
        keyboard = [
            [InlineKeyboardButton("🏠 Вернуться в главное меню", callback_data="back_to_main_from_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(response, reply_markup=reply_markup)
        return SEARCH_HELPERS
    
    elif query.data == "cancel_search":
        await query.edit_message_text(
            'Поиск отменен. Если вам понадобится помощь, обращайтесь снова!'
        )
        return ConversationHandler.END
    
    elif query.data == "back_to_main_from_search":
        keyboard = [
            [InlineKeyboardButton("Я хочу помочь", callback_data="want_to_help")],
            [InlineKeyboardButton("Мне нужна помощь", callback_data="need_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text='Вы вернулись в главное меню.',
            reply_markup=reply_markup
        )
        return MAIN_MENU
    
    else:
        await query.edit_message_text('Пожалуйста, выберите вариант из меню.')
        return SEARCH_HELPERS

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику базы данных (для администратора)"""
    helpers_count = db.get_helpers_count()
    helpers = db.get_all_helpers()
    
    stats_text = f"📊 Статистика базы данных:\n\n"
    stats_text += f"👥 Всего помощников: {helpers_count}\n\n"
    
    if helpers:
        stats_text += "📋 Список всех помощников:\n"
        for i, helper in enumerate(helpers, 1):
            stats_text += (f"{i}. {helper['name']} - {helper['job']}\n")
    else:
        stats_text += "Пока нет помощников в базе данных."
    
    await update.message.reply_text(stats_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать справку по командам"""
    help_text = """
🤖 **Справка по командам бота:**

/start - Запустить бота и открыть главное меню
/menu - Быстрый доступ к главному меню
/help - Показать эту справку
/show_my_form - Показать ваш профиль помощника
/stats - Статистика базы данных (для администратора)
/cancel - Отменить текущую операцию

**Основные функции:**
• Добавить свой профиль как помощника
• Найти помощников для решения ваших задач
• Просмотреть и отредактировать свой профиль

**Как использовать:**
1. Нажмите /start или /menu для начала работы
2. Выберите "Я хочу помочь" или "Мне нужна помощь"
3. Следуйте инструкциям бота
"""
    await update.message.reply_text(help_text)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Быстрый доступ к главному меню"""
    keyboard = [
        [InlineKeyboardButton("Я хочу помочь", callback_data="want_to_help")],
        [InlineKeyboardButton("Мне нужна помощь", callback_data="need_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Главное меню:',
        reply_markup=reply_markup
    )
    return MAIN_MENU

async def setup_menu_commands(application):
    """Установить команды меню бота"""
    commands = [
        BotCommand("start", "🚀 Запустить бота"),
        BotCommand("menu", "📋 Главное меню"),
        BotCommand("help", "❓ Справка по командам"),
        BotCommand("show_my_form", "👤 Показать мой профиль"),
        BotCommand("stats", "📊 Статистика базы данных"),
        BotCommand("cancel", "❌ Отменить операцию"),
    ]
    await application.bot.set_my_commands(commands)

if __name__ == '__main__':
    TOKEN = os.getenv('TELEGRAM_TOKEN') or '7799371983:AAEa3w1CGc6BwUcWG2MoVxfL5bJOgg8OhJ4'
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('menu', menu_command)],
        states={
            MAIN_MENU: [CallbackQueryHandler(main_menu)],
            HELP_MENU: [CallbackQueryHandler(help_menu)],
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            ADD_JOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_job)],
            ADD_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_experience)],
            ADD_HELP: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_help)],
            ADD_CONTACTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_contacts)],
            NEED_HELP_ASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, need_help_ask)],
            PROFILE_COMPLETED: [CallbackQueryHandler(profile_completed)],
            SEARCH_HELPERS: [CallbackQueryHandler(search_helpers)],
            # To be filled with other state handlers
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=True  # Fix the warning about CallbackQueryHandler tracking
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('cancel', cancel))
    app.add_handler(CommandHandler('show_my_form', show_my_form))
    app.add_handler(CommandHandler('stats', show_stats))
    app.add_handler(CommandHandler('help', help_command))

    app.run_polling() 