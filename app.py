#!/usr/bin/env python3
"""
Combined web server and Telegram bot for Render deployment
"""
import os
import threading
import logging
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Import bot functions from main.py
from main import (
    start, cancel, show_my_form, main_menu, help_menu,
    add_name, add_job, add_experience, add_help, add_contacts,
    need_help_ask, profile_completed, search_helpers,
    show_stats, help_command, menu_command, setup_menu_commands,
    MAIN_MENU, HELP_MENU, ADD_NAME, ADD_JOB, ADD_EXPERIENCE, 
    ADD_HELP, ADD_CONTACTS, NEED_HELP_ASK, PROFILE_COMPLETED, SEARCH_HELPERS
)

def run_bot():
    """Run the Telegram bot in a separate thread"""
    try:
        # Initialize database
        db.init_db()
        
        # Get token
        TOKEN = os.getenv('TELEGRAM_TOKEN') or '7799371983:AAEa3w1CGc6BwUcWG2MoVxfL5bJOgg8OhJ4'
        
        # Create application
        bot_app = ApplicationBuilder().token(TOKEN).build()

        # Create conversation handler
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
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        # Add handlers
        bot_app.add_handler(conv_handler)
        bot_app.add_handler(CommandHandler('cancel', cancel))
        bot_app.add_handler(CommandHandler('show_my_form', show_my_form))
        bot_app.add_handler(CommandHandler('stats', show_stats))
        bot_app.add_handler(CommandHandler('help', help_command))

        # Setup menu commands
        bot_app.job_queue.run_once(lambda context: setup_menu_commands(bot_app), when=0)
        
        logger.info("Starting Telegram bot...")
        bot_app.run_polling()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

@app.route('/')
def health_check():
    return 'Telegram Bot is running!', 200

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 