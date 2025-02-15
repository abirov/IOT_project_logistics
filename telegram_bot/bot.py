import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class RESTBot:
    def __init__(self, token, catalog_url):
        self.tokenBot = token
        self.catalog_url = catalog_url  # Base URL for catalog API
        self.bot = telepot.Bot(self.tokenBot)
        self.chatIDs = {}

        
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
        logging.info("🤖 Bot is running. Waiting for messages...")

    def on_chat_message(self, msg):
        """Handles incoming text messages."""
        content_type, chat_type, chat_id = telepot.glance(msg)
        message = msg.get('text', '')

        print(f"🔹 Message received: {message} from {chat_id}")  

        if chat_id not in self.chatIDs:
            self.chatIDs[chat_id] = {"state": None, "driver_id": None}

        if message == "/start":
            print("✅ Start command received!")  
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚗 Driver", callback_data='enter_as_driver')],
                [InlineKeyboardButton(text="🏢 Warehouse User", callback_data='enter_as_warehouse')]
            ])
            self.bot.sendMessage(chat_id, text="Welcome to the Logistics Bot. Please choose your role:", reply_markup=keyboard)

        elif self.chatIDs[chat_id]["state"] == "awaiting_driver_id":
            print(f"📡 Fetching driver details for ID: {message}")
            self.fetch_driver_details(chat_id, message)

        elif self.chatIDs[chat_id]["state"] == "awaiting_warehouse_id":
            self.fetch_warehouse_details(chat_id, message)


        else:
            print("⚠️ Unsupported command received.")
            self.bot.sendMessage(chat_id, text="Command not supported. Use /start to begin.")

    def on_callback_query(self, msg):
        """Handles button clicks in Telegram."""
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print(f"🔔 Callback Query Data: {query_data}")

        if from_id not in self.chatIDs:
            self.chatIDs[from_id] = {"state": None, "driver_id": None}

        if query_data == 'enter_as_driver':
            self.chatIDs[from_id]["state"] = "awaiting_driver_id"
            self.bot.sendMessage(from_id, text="Please enter your Driver ID:")

        elif query_data == "view_driver_details":
            self.send_driver_details(from_id)

        elif query_data == "show_available_packages":
            driver_id = self.chatIDs[from_id]["driver_id"]
            self.show_available_packages(from_id, driver_id)

        elif query_data.startswith("pick_package_"):  
            package_id = query_data.replace("pick_package_", "")
            driver_id = self.chatIDs[from_id]["driver_id"]
            self.assign_package_to_driver(from_id, package_id, driver_id)

        elif query_data.startswith("change_status_"):
            package_id = query_data.replace("change_status_", "")
            self.change_package_status(from_id, package_id)

        elif query_data.startswith("confirm_delivery_"):
            package_id = query_data.replace("confirm_delivery_", "")
            self.confirm_package_delivery(from_id, package_id)
        
        elif query_data.startswith("reassign_order_"):  
            package_id = query_data.split("_")[-1]
            self.cancel_package_assignment(from_id, package_id)
        
        
        elif query_data == 'enter_as_warehouse':
            self.chatIDs[from_id]["state"] = "awaiting_warehouse_id"
            self.bot.sendMessage(from_id, text="Please enter your Warehouse ID:")

        elif query_data == "view_warehouse_details":
            self.send_warehouse_details(from_id)



        self.bot.answerCallbackQuery(query_id, text="")

    def fetch_driver_details(self, chat_id, driver_id):
        """Fetch driver details from `catalog2` API and store them."""
        url = f"{self.catalog_url}/drivers/drivers?driver_id={driver_id}"

        try:
            response = requests.get(url, timeout=5)
            logging.debug(f"📡 API Response Status: {response.status_code}")

            if response.status_code == 200:
                driver = response.json()
                logging.debug(f"👤 Driver Data: {driver}")

                if driver:
                    self.chatIDs[chat_id] = {"state": "driver_logged_in", "driver_id": driver["_id"]}

                    welcome_message = f"👋 Welcome, **{driver['name']}**!"
                    self.bot.sendMessage(chat_id, text=welcome_message, parse_mode="Markdown")

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="📝 View My Details", callback_data="view_driver_details")],
                        [InlineKeyboardButton(text="📦 Pick Up a Package", callback_data="show_available_packages")]
                    ])
                    self.bot.sendMessage(chat_id, text="What would you like to do?", reply_markup=keyboard)
                else:
                    self.bot.sendMessage(chat_id, text="⚠️ No driver found with that ID.")
            else:
                self.bot.sendMessage(chat_id, text="❌ Failed to fetch driver details.")

        except Exception as e:
            logging.error(f"❌ Error fetching driver details: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred.")

    def send_driver_details(self, chat_id):
        """Fetch and display driver details when the user selects 'View My Details'."""
        driver_id = self.chatIDs.get(chat_id, {}).get("driver_id")

        if not driver_id:
            self.bot.sendMessage(chat_id, text="⚠️ No driver ID found. Please log in again using /start.")
            return

        url = f"{self.catalog_url}/drivers/drivers?driver_id={driver_id}"

        try:
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                driver = response.json()

                if driver:
                    details = (
                        f"👤 *Driver Details*\n"
                        f"🆔 ID: {driver['_id']}\n"
                        f"👨‍💼 Name: {driver['name']}\n"
                        f"📧 Email: {driver['email']}\n"
                        f"📞 Phone: {driver['phone']}\n"
                        f"🚗 Vehicle: {driver.get('vehicle', 'Not provided')}\n"
                    )
                    self.bot.sendMessage(chat_id, text=details, parse_mode="Markdown")
                else:
                    self.bot.sendMessage(chat_id, text="⚠️ No details found for this driver.")

            else:
                self.bot.sendMessage(chat_id, text="❌ Failed to retrieve driver details.")

        except Exception as e:
            logging.error(f"❌ Error retrieving driver details: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while retrieving driver details.")

    def show_available_packages(self, chat_id, driver_id):
        """Show available packages for pickup."""
        url = f"{self.catalog_url}/packages/packages?no_driver"

        try:
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                packages = response.json()

                if not packages:
                    self.bot.sendMessage(chat_id, text="📦 No packages are available for pickup right now.")
                    return

                keyboard = []
                for package in packages:
                    package_details = (
                        f"📦 *Package Name:* {package.get('name', 'N/A')}\n"
                        f"⚖️ *Weight:* {package.get('weight', 'N/A')} kg\n"
                        f"📏 *Dimensions:* {package.get('dimensions', {}).get('length', 'N/A')} x "
                        f"{package.get('dimensions', {}).get('width', 'N/A')} x "
                        f"{package.get('dimensions', {}).get('height', 'N/A')} cm\n"
                        f"🏢 *Warehouse ID:* {package.get('warehouse_id', 'N/A')}\n"
                        f"👤 *Driver Assigned:* {'None' if not package.get('driver_id') else package['driver_id']}\n"
                        f"🚦 *Status:* {package.get('status', 'N/A')}\n"
                        f"📍 *Delivery Address:* {package.get('delivery_address', {}).get('city', 'N/A')}, "
                        f"{package.get('delivery_address', {}).get('street', 'N/A')} "
                        f"({package.get('delivery_address', {}).get('zipcode', 'N/A')})\n"
                    )

                    self.bot.sendMessage(chat_id, text=package_details, parse_mode="Markdown")

                    keyboard.append([InlineKeyboardButton(text=f"🚚 Pick Package {package['name']}", callback_data=f"pick_package_{package['_id']}")])

                reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                self.bot.sendMessage(chat_id, text="Select a package to pick up:", reply_markup=reply_markup)

            else:
                self.bot.sendMessage(chat_id, text="⚠️ Failed to fetch available packages.")

        except Exception as e:
            logging.error(f"❌ Error fetching packages: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while fetching packages.")

    def assign_package_to_driver(self, chat_id, package_id, driver_id):
        """Assign the selected package to the driver and provide options to change status or cancel."""
        url = f"{self.catalog_url}/packages/assign_driver?package_id={package_id}&driver_id={driver_id}"

        try:
            # Check if package is already assigned
            package_details_url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
            package_response = requests.get(package_details_url, timeout=5)
 
            if package_response.status_code == 200:
                package = package_response.json()
        
                if package.get("driver_id"):  # If driver_id is not None
                    self.bot.sendMessage(chat_id, text="❌ This package has already been assigned to another driver. Please select another package from the list")
                    return  # Stop further execution

            # If package is not assigned, proceed with assignment
            data = {"driver_id": driver_id}
            response = requests.put(url, json=data, timeout=5)

            if response.status_code == 200:
                self.bot.sendMessage(chat_id, text="✅ Package successfully assigned to you! 🚚\nYou can now go to the warehouse to pick it up!")

                package_details_url = f"{self.catalog_url}/packages/packages?package_id={package_id}"

                try:
                    package_response = requests.get(package_details_url, timeout=5)

                    if package_response.status_code == 200:
                        package = package_response.json()

                        # package details
                        package_info = (
                            f"📦 *Package Details:*\n"
                            f"🆔 *ID:* {package['_id']}\n"
                            f"📦 *Name:* {package.get('name', 'N/A')}\n"
                            f"⚖️ *Weight:* {package.get('weight', 'N/A')} kg\n"
                            f"📏 *Dimensions:* {package.get('dimensions', {}).get('length', 'N/A')} x "
                            f"{package.get('dimensions', {}).get('width', 'N/A')} x "
                            f"{package.get('dimensions', {}).get('height', 'N/A')} cm\n"
                            f"📍 *Delivery Address:* {package.get('delivery_address', {}).get('street', 'N/A')}, "
                            f"{package.get('delivery_address', {}).get('city', 'N/A')} "
                            f"({package.get('delivery_address', {}).get('zipcode', 'N/A')})\n"
                            
                        )

                    
                        self.bot.sendMessage(chat_id, text=package_info, parse_mode="Markdown")

                    else:
                        self.bot.sendMessage(chat_id, text="⚠️ Could not fetch package details. Please try again.")

                except Exception as e:
                    logging.error(f"❌ Error fetching package details: {str(e)}")
                    self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while retrieving package details.")

                       
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Status Changing", callback_data=f"change_status_{package_id}")],
                    [InlineKeyboardButton(text="🚫 Reassigning Order", callback_data=f"reassign_order_{package_id}")]
                ])
                self.bot.sendMessage(chat_id, text="You can change the status after loading or cancel the order by pressing this option:", reply_markup=keyboard)

            else:
                 self.bot.sendMessage(chat_id, text="⚠️ Failed to assign package.")
        except Exception as e:
            logging.error(f"❌ Error assigning package: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while assigning the package.")

    
    
    def change_package_status(self, chat_id, package_id):
        """Change the package status from 'in warehouse' to 'in transit'."""

        url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
        new_status = {"status": "in transit"}

        try:
            response = requests.put(url, json=new_status, timeout=5)

            if response.status_code in [200, 201]:
                
                 self.chatIDs[chat_id]["package_status"] = "in transit"
                 self.bot.sendMessage(chat_id, text="✅ Package status updated to 'in transit'! 🚚")

                 
                 keyboard = InlineKeyboardMarkup(inline_keyboard=[
                     [InlineKeyboardButton(text="✅ Confirm Delivery", callback_data=f"confirm_delivery_{package_id}")]
                 ])
                 self.bot.sendMessage(chat_id, text="📦 After delivering, please select this button:", reply_markup=keyboard)

            else:
                 self.bot.sendMessage(chat_id, text="⚠️ Failed to update package status. Please try again.")

        except Exception as e:
            logging.error(f"❌ Error updating package status: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while updating package status.")


    def confirm_package_delivery(self, chat_id, package_id):
        """Change the package status from 'in transit' to 'Delivered '."""

        url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
        new_status = {"status": "delivered"}

        try:
            response = requests.put(url, json=new_status, timeout=5)

            if response.status_code in [200, 201]:
                self.bot.sendMessage(chat_id, text="✅  Package successfully delivered! 🎉")
                self.send_driver_menu(chat_id)  # Redirect to driver-specific menu


            else:
                self.bot.sendMessage(chat_id, text="⚠️ Failed to confirm delivery. Please try again.")

        except Exception as e:
            logging.error(f"❌ Error confirming package delivery: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while confirming delivery.")


    def cancel_package_assignment(self, chat_id, package_id):
        """Set the driver_id to None in the package document in MongoDB."""

        # Check if package is already in transit
        if self.chatIDs[chat_id].get("package_status") == "in transit":
           self.bot.sendMessage(chat_id, text="⚠️ The package is already 'in transit' and cannot be reassigned.")
       
           return  
        
        url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
        data = {"driver_id": None}  # Set driver_id to None

        try:
            response = requests.put(url, json=data, timeout=5)

            if response.status_code in [200, 204]:  # Assuming 200 OK or 204 No Content as successful
             self.bot.sendMessage(chat_id, text="🔄 Order has been cancelled and is now available for other Drivers.")
             self.send_driver_menu(chat_id)  # Redirect to driver-specific menu

            else:
             self.bot.sendMessage(chat_id, text="⚠️ Failed to cancel the order. Please try again.")

        except Exception as e:
           logging.error(f"❌ Error cancelling order: {str(e)}")
           self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while cancelling the order.")

    
    def send_start_menu(self, chat_id):
        """Send the start menu to the user."""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚗 Driver", callback_data='enter_as_driver')],
            [InlineKeyboardButton(text="🏢 Warehouse User", callback_data='enter_as_warehouse')]
        ])
        self.bot.sendMessage(chat_id, text="Welcome to the Logistics Bot. Please choose your role:", reply_markup=keyboard)

    def send_driver_menu(self, chat_id):
        """Send the driver-specific menu."""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
             [InlineKeyboardButton(text="📋 View My Details", callback_data="view_driver_details")],
             [InlineKeyboardButton(text="📦 Pick Up a Package", callback_data="show_available_packages")]
        ])
        self.bot.sendMessage(chat_id, text="What would you like to do?", reply_markup=keyboard)

    def fetch_warehouse_details(self, chat_id, warehouse_id):
        """Fetch warehouse details from the catalog API."""
        url = f"{self.catalog_url}/warehouses/warehouses?warehouse_id={warehouse_id}"
  
        try:
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                warehouse = response.json()

                if warehouse:
                   self.chatIDs[chat_id] = {"state": "warehouse_logged_in", "warehouse_id": warehouse["_id"]}

                   # Send welcome message
                   welcome_message = f"🏢 Welcome to *{warehouse['name']}*!\n"
                   self.bot.sendMessage(chat_id, text=welcome_message, parse_mode="Markdown")

                   # Show options
                   keyboard = InlineKeyboardMarkup(inline_keyboard=[
                       [InlineKeyboardButton(text="📜 View Warehouse Details", callback_data="view_warehouse_details")],
                       [InlineKeyboardButton(text="📦 Tracking", callback_data="tracking")]
                    ])
                   self.bot.sendMessage(chat_id, text="What would you like to do?", reply_markup=keyboard)

                else:
                    self.bot.sendMessage(chat_id, text="⚠️ No warehouse found with that ID.")

            else:
                self.bot.sendMessage(chat_id, text="❌ Failed to fetch warehouse details.")

        except Exception as e:
            logging.error(f"❌ Error fetching warehouse details: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred.")

    def send_warehouse_details(self, chat_id):
        """Fetch and display warehouse details."""
        warehouse_id = self.chatIDs.get(chat_id, {}).get("warehouse_id")

        if not warehouse_id:
            self.bot.sendMessage(chat_id, text="⚠️ No warehouse ID found. Please log in again using /start.")
            return

        url = f"{self.catalog_url}/warehouses/warehouses?warehouse_id={warehouse_id}"

        try:
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                warehouse = response.json()

                if warehouse:
                        details = (
                           f"🏢 *Warehouse Details*\n"
                           f"🆔 ID: {warehouse['_id']}\n"
                           f"🏠 Name: {warehouse['name']}\n"
                           f"📍 Address: {warehouse['address']['street']}, {warehouse['address']['city']}, "
                           f"{warehouse['address']['state']} ({warehouse['address']['zip']})\n"
                           f"📞 Phone: {warehouse['phone']}\n"
                           f"📧 Email: {warehouse['email']}\n"
                        )
                        self.bot.sendMessage(chat_id, text=details, parse_mode="Markdown")
                else:
                        self.bot.sendMessage(chat_id, text="⚠️ No details found for this warehouse.")
  
            else:
                 self.bot.sendMessage(chat_id, text="❌ Failed to retrieve warehouse details.")

        except Exception as e:
             logging.error(f"❌ Error retrieving warehouse details: {str(e)}")
             self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while retrieving warehouse details.")





if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = "8159489225:AAGd897nlIv2JkkBuYwfyNXt4nAs15ILUNA"  # Replace with your actual bot token
    CATALOG2_API_URL = "http://127.0.0.1:8080"

    bot = RESTBot(TELEGRAM_BOT_TOKEN, CATALOG2_API_URL)

    # Keep the bot running
    print("🤖 Bot is running. Press Ctrl+C to exit.")
    while True:
        pass











