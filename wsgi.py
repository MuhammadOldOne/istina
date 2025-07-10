# WSGI entry point for Render
# This file is for compatibility with web servers
# The main bot runs directly from main.py

def application(environ, start_response):
    """WSGI application for Render compatibility"""
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b'Telegram Bot is running']

if __name__ == "__main__":
    # Import and run the bot
    from main import *
    import main 