import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler

class VehicleStatusBot:
    def __init__(self, token, api_url):
        self.token = token
        self.api_url = api_url  # Base URL for your catalog REST API
        self.application = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("status", self.ask_for_filter_choice))
        self.application.add_handler(CallbackQueryHandler(self.handle_filter_choice))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_filter_input))

    async def start(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text('Hello! Use /status to filter by driver ID or package ID.')

    async def ask_for_filter_choice(self, update: Update, context: CallbackContext) -> None:
        keyboard = [
            [InlineKeyboardButton("Driver ID", callback_data='driver_id')],
            [InlineKeyboardButton("Package ID", callback_data='package_id')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Would you like to filter by driver ID or package ID?', reply_markup=reply_markup)

    async def handle_filter_choice(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        await query.answer()

        filter_mode = query.data
        context.user_data['filter_mode'] = filter_mode

        if filter_mode == 'driver_id':
            await query.edit_message_text('Please enter the driver ID to filter the data.')
        elif filter_mode == 'package_id':
            await query.edit_message_text('Please enter the package ID to filter the data.')

    async def handle_filter_input(self, update: Update, context: CallbackContext) -> None:
        filter_mode = context.user_data.get('filter_mode')

        if filter_mode == 'driver_id':
            await self.filter_by_driver_id(update, context)
        elif filter_mode == 'package_id':
            await self.filter_by_package_id(update, context)

    # Fetching data using REST API for driver_id
    async def filter_by_driver_id(self, update: Update, context: CallbackContext) -> None:
        driver_id = update.message.text.strip()
        url = f"{self.api_url}/drivers?driver_id={driver_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            drivers_data = response.json()

            if drivers_data:
                status_message = "\n".join([f"Driver {d['driver_id']} - From {d['source']} to {d['destination']}: {d['status']}" for d in drivers_data])
            else:
                status_message = f"No data available for driver ID: {driver_id}"
        except requests.RequestException as e:
            status_message = f"Error fetching data: {e}"

        await update.message.reply_text(status_message)

    # Fetching data using REST API for package_id
    async def filter_by_package_id(self, update: Update, context: CallbackContext) -> None:
        package_id = update.message.text.strip()
        url = f"{self.api_url}/logistics_points/{package_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            package_data = response.json()

            if package_data:
                status_message = (
                    f"Package ID: {package_data['package_id']}\n"
                    f"Driver ID: {package_data['driver_id']}\n"
                    f"From {package_data['source']} to {package_data['destination']}: {package_data['status']}"
                )
            else:
                status_message = f"No data available for package ID: {package_id}"
        except requests.RequestException as e:
            status_message = f"Error fetching data: {e}"

        await update.message.reply_text(status_message)

    def run(self):
        self.application.run_polling()

if __name__ == '__main__':
    TELEGRAM_API_TOKEN = "6998616059:AAFEB07QcjFw-twXCqdgm_NYNZBMXZRx9h4"
    API_BASE_URL = "http://localhost:8080"  # Base URL for the catalog service

    bot = VehicleStatusBot(TELEGRAM_API_TOKEN, API_BASE_URL)
    bot.run()
