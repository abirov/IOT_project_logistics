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
        message = msg.get('text', '').strip().lower()  # Convert to lowercase for consistency

        print(f"🔹 Message received: {message} from {chat_id}")  

        if chat_id not in self.chatIDs:
            self.chatIDs[chat_id] = {"state": None, "driver_id": None}

        #Shortcuts dictionary
        shortcuts = {
            "s": "/start", "st": "/start", "sta": "/start", "star": "/start",
            "d": "/driver_details", "de": "/driver_details", "det": "/driver_details",
            "p": "/pick_package", "pa": "/pick_package", "pan": "/panel", "pane": "/panel"
        }

        #Convert shortcut message to full command
        if message in shortcuts:
            message = shortcuts[message]  # Replace the shortcut with the full command



        if message == "/start":
            print("✅ Start command received!")  
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚗 Driver", callback_data='enter_as_driver')],
                [InlineKeyboardButton(text="🏢 Warehouse User", callback_data='enter_as_warehouse')]
            ])
            self.bot.sendMessage(chat_id, text="Welcome to the Logistics Bot. Please choose your role:", reply_markup=keyboard)
        
        elif message == "/panel":
            driver_id = self.chatIDs.get(chat_id, {}).get("driver_id")
            if driver_id:
                self.driver_panel(chat_id, driver_id)
            else:
                self.bot.sendMessage(chat_id, text="⚠️ You need to log in first. Use /start.")

        elif message == "/pick_package":
            driver_id = self.chatIDs.get(chat_id, {}).get("driver_id")
            if driver_id:
                self.show_available_packages(chat_id, driver_id)
            else:
                self.bot.sendMessage(chat_id, text="⚠️ You need to log in first. Use /start.")

        elif message == "/driver_details":
            driver_id = self.chatIDs.get(chat_id, {}).get("driver_id")
            if driver_id:
                 self.send_driver_details(chat_id)
            else:
                 self.bot.sendMessage(chat_id, text="⚠️ You need to log in first. Use /start.")


        elif self.chatIDs[chat_id]["state"] == "awaiting_driver_id":
            print(f"📡 Fetching driver details for ID: {message}")
            self.fetch_driver_details(chat_id, message)

        elif self.chatIDs[chat_id]["state"] == "awaiting_warehouse_id":
            self.fetch_warehouse_details(chat_id, message)

        elif self.chatIDs[chat_id]["state"] == "awaiting_package_id":
            print(f"📦 Fetching package details for ID: {message}")
            self.track_package(chat_id, message)
            self.chatIDs[chat_id]["state"] = None  # Reset the state after handling the package ID

        else:
            print("⚠️ Unsupported command received.")
            self.bot.sendMessage(chat_id, text="Command not supported. Use /start to begin.")


    def on_callback_query(self, msg):
        """Handles button clicks in Telegram."""
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print(f"🔔 Callback Query Data: {query_data}")

        if from_id not in self.chatIDs:
            self.chatIDs[from_id] = {"state": None, "driver_id": None}

        if query_data == 'track_vehicle':
            # Present options for tracking by Driver ID or Package ID
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Tracking by Driver ID", callback_data='track_driver')],
                [InlineKeyboardButton(text="Tracking by Package ID", callback_data='track_package')]
            ])
            self.bot.sendMessage(from_id, "Select tracking method:", reply_markup=keyboard)

        elif query_data == 'track_driver':
            self.chatIDs[from_id]["state"] = "awaiting_driver_id"  # Set state for expecting driver ID
            self.bot.sendMessage(from_id, text="Please enter the Driver ID:")

        elif query_data == 'track_package':
            self.chatIDs[from_id]["state"] = "awaiting_package_id"  # Set state for expecting package ID
            self.bot.sendMessage(from_id, text="Please enter the Package ID:")

        elif query_data == 'enter_as_driver':
            self.chatIDs[from_id]["state"] = "awaiting_driver_id"
            self.bot.sendMessage(from_id, text="Please enter your Driver ID or Email:")

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

        elif query_data == "driver_panel":
            driver_id = self.chatIDs[from_id]["driver_id"]
            self.driver_panel(from_id, driver_id)

        elif query_data.startswith("confirm_delivery_"):
            package_id = query_data.replace("confirm_delivery_", "")
            self.confirm_package_delivery(from_id, package_id)

        elif query_data.startswith("reassign_order_"):
            data = query_data.split("_")
            package_id = data[2]
            package_name = '_'.join(data[3:])  # Since package names might contain underscores, join the rest
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Yes, Reassign", callback_data=f"confirm_reassign_{package_id}")],
                [InlineKeyboardButton(text="❌ No, Cancel", callback_data="cancel_action")]
            ])
            # Send a confirmation message including the package name
            self.bot.sendMessage(from_id, text=f"⚠️ Are you sure you want to reassign the package '{package_name}'?", reply_markup=keyboard)

        elif query_data.startswith("confirm_reassign_"):
            package_id = query_data.split("_")[2]
            self.cancel_package_assignment(from_id, package_id)

        elif query_data == "cancel_action":
            self.bot.sendMessage(from_id, text="❌ Action canceled.")

        elif query_data == 'enter_as_warehouse':
            self.chatIDs[from_id]["state"] = "awaiting_warehouse_id"
            self.bot.sendMessage(from_id, text="Please enter your Warehouse ID:")

        elif query_data == "view_warehouse_details":
            self.send_warehouse_details(from_id)

        self.bot.answerCallbackQuery(query_id, text="")

    def fetch_driver_details(self, chat_id, identifier):
        """Fetch driver details from the catalog API and determine if the identifier is an email or driver ID."""
        # Determine if the identifier is an email or a driver ID and construct the URL accordingly
        if '@' in identifier:
            url = f"{self.catalog_url}/drivers/drivers?driver_email={identifier}"
        else:
            url = f"{self.catalog_url}/drivers/drivers?driver_id={identifier}"

        try:
           
            response = requests.get(url, timeout=5)
            logging.debug(f"📡 API Response Status: {response.status_code}")

            if response.status_code == 200:
                driver = response.json()
                logging.debug(f"👤 Driver Data: {driver}")

                if driver:
                    # Update the chat state and driver_id
                    self.chatIDs[chat_id] = {"state": "driver_logged_in", "driver_id": driver["_id"]}

                   
                    welcome_message = f"👋 Welcome, **{driver['name']}**!"
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="📝 View My Details", callback_data="view_driver_details")],
                        [InlineKeyboardButton(text="📦 Pick Up a Package", callback_data="show_available_packages")],
                        [InlineKeyboardButton(text="📂 My Panel", callback_data="driver_panel")]
                    ])
                    self.bot.sendMessage(chat_id, text=welcome_message, parse_mode="Markdown")
                    self.bot.sendMessage(chat_id, text="What would you like to do?", reply_markup=keyboard)
                else:
                    
                    self.bot.sendMessage(chat_id, text="⚠️ No driver found with that ID or email.")
            else:
              
                self.bot.sendMessage(chat_id, text="❌ Failed to fetch driver details.")
        except Exception as e:
            # Log and handle exceptions during the HTTP request
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
                        f"🚗 Vehicle: {driver.get('car_model', 'Not provided')}\n"
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

                for package in packages:
                    package_details = self.fetch_package_details(package['_id'])

                    '''# Retrieve and format warehouse information
                    warehouse_info = self.get_warehouse_details(package.get("warehouse_id")) if package.get("warehouse_id") else "Warehouse details not available."
                    package_details = (
                        f"📦 *Package Name:* {package.get('name', 'N/A')}\n"
                        f"⚖️ *Weight:* {package.get('weight', 'N/A')} kg\n"
                        f"📏 *Dimensions:* {package.get('dimensions', {}).get('length', 'N/A')} x "
                        f"{package.get('dimensions', {}).get('width', 'N/A')} x "
                        f"{package.get('dimensions', {}).get('height', 'N/A')} cm\n"
                        f"🏢 *Warehouse Details:* {warehouse_info}\n"
                        f"👤 *Driver Assigned:* {'None' if not package.get('driver_id') else package['driver_id']}\n"
                        f"🚦 *Status:* {package.get('status', 'N/A')}\n"
                        f"📍 *Delivery Address:* {package.get('delivery_address', {}).get('city', 'N/A')}, "
                        f"{package.get('delivery_address', {}).get('street', 'N/A')} "
                        f"({package.get('delivery_address', {}).get('zipcode', 'N/A')})"
                    )'''

                    self.bot.sendMessage(chat_id, text=package_details, parse_mode="Markdown")

                    # Create a keyboard for this specific package
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f"🚚 Pick Package {package['name']}", callback_data=f"pick_package_{package['_id']}")]
                    ])
                    self.bot.sendMessage(chat_id, text="Select this package to pick up:", reply_markup=keyboard)

            else:
                self.bot.sendMessage(chat_id, text="⚠️ Failed to fetch available packages.")
        except Exception as e:
            logging.error(f"❌ Error fetching packages: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while fetching packages please check.")


    def assign_package_to_driver(self, chat_id, package_id, driver_id):
        """Assign the selected package to the driver and provide options to change status or cancel."""
        try:
            package_details_url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
            package_response = requests.get(package_details_url, timeout=5)

            if package_response.status_code == 200:
                package = package_response.json()
            
                if package.get("driver_id") and package["driver_id"] != "":
                    self.bot.sendMessage(chat_id, text="❌ This package has already been assigned to another driver. Please select another package from the list")
                    return  

            # If package is not assigned, do the assignment
            data = {"driver_id": driver_id}
            response = requests.put(package_details_url, json=data, timeout=5)

            if response.status_code == 200:
                warehouse_info = self.get_warehouse_details(package.get("warehouse_id")) if package.get("warehouse_id") else "Warehouse details not available."
                assignment_message = f"✅ Package successfully assigned to you!\n 🚚 Pick it up at *{warehouse_info}*"
                self.bot.sendMessage(chat_id, text=assignment_message, parse_mode="Markdown")

                package_info = self.fetch_package_details(package_id)
            
            
                '''package_info = (
                    f"📦 *Package Details:*\n"
                    f"🆔 *ID:* {package['_id']}\n"
                    f"📦 *Name:* {package.get('name', 'N/A')}\n"
                    f"⚖️ *Weight:* {package.get('weight', 'N/A')} kg\n"
                    f"📏 *Dimensions:* {package.get('dimensions', {}).get('length', 'N/A')} x "
                    f"{package.get('dimensions', {}).get('width', 'N/A')} x "
                    f"{package.get('dimensions', {}).get('height', 'N/A')} cm\n"
                    f"📍 *Delivery Address:* {package.get('delivery_address', {}).get('street', 'N/A')}, "
                    f"{package.get('delivery_address', {}).get('city', 'N/A')} "
                    f"({package.get('delivery_address', {}).get('zipcode', 'N/A')})"
                )'''
            

                self.bot.sendMessage(chat_id, text=package_info, parse_mode="Markdown")

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Confirm Pick-up", callback_data=f"change_status_{package_id}")],
                    [InlineKeyboardButton(text="🚫 Reassigning Order", callback_data=f"reassign_order_{package_id}")]
                ])
                self.bot.sendMessage(chat_id, text="You can change the status after loading or cancel the order by pressing these options", reply_markup=keyboard)
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
        """Send the driver-specific menu, including an option to view assigned packages."""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 View My Details", callback_data="view_driver_details")],
            [InlineKeyboardButton(text="📦 Pick Up a Package", callback_data="show_available_packages")],
            [InlineKeyboardButton(text="📂 My Panel", callback_data="driver_panel")]
        ])
        self.bot.sendMessage(chat_id, text="What would you like to do?", reply_markup=keyboard)



    def driver_panel(self, chat_id, driver_id):
        """Fetch and display all packages assigned to the driver, filtering out delivered packages."""
        url = f"{self.catalog_url}/packages/packages?driver_id={driver_id}"

        try:
            response = requests.get(url, timeout=5)
            logging.debug(f"📡 API Response Status: {response.status_code}")
            logging.debug(f"📦 API Response Content: {response.text}")  # Log the full API response

            if response.status_code == 200:
                packages = response.json()

                if not packages:
                    self.bot.sendMessage(chat_id, text="📦 You have no assigned packages at the moment.")
                    return

                for package in packages:
                    if package.get('status') != 'delivered':
                        package_info = self.fetch_package_details(package['_id'])
                        
                        '''package_info = (
                            f"📦 *Package Details:*\n"
                            f"🆔 *ID:* {package['_id']}\n"
                            f"📦 *Name:* {package.get('name', 'N/A')}\n"
                            f"⚖️ *Weight:* {package.get('weight', 'N/A')} kg\n"
                            f"🏢 *Warehouse:* {package.get('warehouse_id', 'N/A')}\n"
                            f"📍 *Delivery Address:* {package.get('delivery_address', {}).get('street', 'N/A')}, "
                            f"{package.get('delivery_address', {}).get('city', 'N/A')} "
                            f"({package.get('delivery_address', {}).get('zipcode', 'N/A')})\n"
                            f"🚦 *Status:* {package.get('status', 'N/A')}"
                        )'''

                        buttons = []
                        if package.get('status') == 'in transit':
                            buttons.append([InlineKeyboardButton(text="✅ Confirm Delivery", callback_data=f"confirm_delivery_{package['_id']}")])
                        elif package.get('status') == 'in warehouse':
                            buttons.append([InlineKeyboardButton(text="🚚 Confirm Pick-up", callback_data=f"change_status_{package['_id']}")])
                            buttons.append([InlineKeyboardButton(text="🚫 Reassign Order", callback_data=f"reassign_order_{package['_id']}_{package.get('name', 'N/A')}")])

                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_id, text=package_info, parse_mode="Markdown", reply_markup=keyboard)

            else:
                self.bot.sendMessage(chat_id, text="⚠️ Failed to fetch assigned packages. Please try again.")

        except Exception as e:
            logging.error(f"❌ Error fetching assigned packages: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while fetching your assigned packages.")



    def fetch_package_details(self, package_id):
        """Fetch package details from the API and format them into a Markdown string for Telegram messages, including warehouse details."""
        # Construct the URL to fetch package details
        url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
        
        try:
            # Perform the API request for package details
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                package = response.json()
                
                # Fetch and format warehouse details if available
                warehouse_info = self.get_warehouse_details(package.get("warehouse_id")) if package.get("warehouse_id") else "Warehouse details not available."

                # Format the package details
                package_info = (
                    f"📦 *Package Details:*\n"
                    f"🆔 *ID:* {package.get('_id', 'N/A')}\n"
                    f"📦 *Name:* {package.get('name', 'N/A')}\n"
                    f"⚖️ *Weight:* {package.get('weight', 'N/A')} kg\n"
                    f"📏 *Dimensions:* {package.get('dimensions', {}).get('length', 'N/A')} x "
                    f"{package.get('dimensions', {}).get('width', 'N/A')} x "
                    f"{package.get('dimensions', {}).get('height', 'N/A')} cm\n"
                    f"🏢 *Warehouse Details:* {warehouse_info}\n"
                    f"📍 *Delivery Address:* {package.get('delivery_address', {}).get('street', 'N/A')}, "
                    f"{package.get('delivery_address', {}).get('city', 'N/A')} "
                    f"({package.get('delivery_address', {}).get('zipcode', 'N/A')})\n"
                    f"🚦 *Status:* {package.get('status', 'N/A')}"
                )
                return package_info
            else:
                return "Failed to fetch package details."
        except requests.RequestException as e:
            return f"Error fetching package details: {str(e)}"

    def get_driver_info(self, driver_id):
        """Fetch driver details from the API and return a formatted string."""
        driver_url = f"http://127.0.0.1:8080/drivers/drivers?driver_id={driver_id}"
        try:
            response = requests.get(driver_url, timeout=5)
            if response.status_code == 200:
                driver_data = response.json()
                driver_id_value = driver_data.get("_id", "N/A")
                driver_name = driver_data.get("name", "N/A")
                return f"ID: {driver_id_value}, Name: {driver_name}"
            else:
                return "Driver information not available."
        except Exception as e:
            print(f"Error fetching driver info: {str(e)}")
            return "Driver information not available due to an error."

    def get_warehouse_details(self, warehouse_id):
        """Fetches and formats warehouse details from the catalog API using the warehouse ID."""
        warehouse_details_url = f"{self.catalog_url}/warehouses/warehouses?warehouse_id={warehouse_id}"
        try:
            response = requests.get(warehouse_details_url, timeout=5)
            if response.status_code == 200:
                warehouse = response.json()
                warehouse_name = warehouse.get('name', 'N/A')
                warehouse_address = f"{warehouse.get('address', {}).get('street', 'N/A')}, {warehouse.get('address', {}).get('city', 'N/A')}"
                return f"{warehouse_name}, {warehouse_address}"
            else:
                return "Warehouse details not available."
        except requests.RequestException as e:
            logging.error(f"Error fetching warehouse details: {str(e)}")
            return "Warehouse details not available."


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
                       [InlineKeyboardButton(text="📦 Tracking", callback_data="track_vehicle")]
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

    def track_vehicle(self, chat_id):
        """Simulate tracking by sending a location map."""
        # Example coordinates for demonstration
        latitude, longitude = 40.7128, -74.0060  # New York City coordinates for example
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom=15&size=600x300&maptype=roadmap&markers=color:red%7Clabel:V%7C{latitude},{longitude}&key=AIzaSyDnwzgQZ9naw7lZ2XWXanZzFH8bYoP3ZAQ"

        # Fetch the map image from the URL
        response = requests.get(map_url)
        if response.status_code == 200:
            # Write the image to a temporary file
            temp_image_path = 'temp_map.png'
            with open(temp_image_path, 'wb') as f:
                f.write(response.content)
            
            # Send the image to the chat
            with open(temp_image_path, 'rb') as photo:
                self.bot.sendPhoto(chat_id, photo=photo, caption="Current location of the delivery vehicle.")
        else:
            # Print detailed error information if the map retrieval fails
            print("Failed to retrieve map image. Status code:", response.status_code)
            print("Response body:", response.text)  # This will print the error details provided by Google Maps API
            self.bot.sendMessage(chat_id, "Failed to retrieve map image.")

    #def track_vehicle(self, chat_id):
        #"""Send a link to Google Maps showing a location."""
        # Example coordinates for demonstration
        #latitude, longitude = 40.7128, -74.0060  # New York City coordinates
        # Create a URL that opens these coordinates in Google Maps
        #map_url = f"https://www.google.com/maps/?q={latitude},{longitude}"

        # Send the URL as a clickable link in a message
        #self.bot.sendMessage(chat_id, text=f"View the location on Google Maps: {map_url}", disable_web_page_preview=True)

    def track_driver(self, chat_id, driver_id):
        # Implement driver tracking logic here
        print(f"Tracking driver with ID: {driver_id}")
        # Fetch driver details and send to user...
        self.bot.sendMessage(chat_id, text="Driver location: [Location Details Here]")


    

    def track_package(self, chat_id, package_id):
        """Fetch and display package details using the package ID."""
        print(f"📦 Fetching package details for Package ID: {package_id}")
        package_details = self.fetch_package_details(package_id)
        reply_markup = None  # default, no keyboard
        
        # Check if the package is delivered by examining the status in the formatted details
        if package_details and "🚦 *status:* delivered" in package_details.lower():
            # Re-fetch the package JSON to extract additional delivery info
            url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    package_json = response.json()
                    driver_id = package_json.get("driver_id", None)
                    driver_info = ""
                    if driver_id:
                        # Use the get_driver_info method which returns a string like:
                        # "ID: 675897aebdb7c9ebe2fa26ce, Name: Jane Cristina"
                        raw_driver_info = self.get_driver_info(driver_id)
                        parts = raw_driver_info.split(", ")
                        if len(parts) == 2:
                            driver_id_value = parts[0].split(": ")[1] if ": " in parts[0] else parts[0]
                            driver_name_value = parts[1].split(": ")[1] if ": " in parts[1] else parts[1]
                            driver_info = f"\n*ID:* {driver_id_value}\n*Name:* {driver_name_value}"
                        else:
                            driver_info = f"\n{raw_driver_info}"
                    package_details += f"\n\nThe package was *delivered* by driver:{driver_info}."
                else:
                    package_details += "\n\nThe package is marked as delivered, but delivery details are not available."
            except Exception as e:
                print(f"Error fetching delivery details: {str(e)}")
                package_details += "\n\nAn error occurred while fetching delivery details."
        
        # New branch: Check for the "in transit" status
        elif package_details and "🚦 *status:* in transit" in package_details.lower():
            # Re-fetch the package JSON to extract additional transit info (driver info)
            url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    package_json = response.json()
                    driver_id = package_json.get("driver_id", None)
                    driver_info = ""
                    if driver_id:
                        raw_driver_info = self.get_driver_info(driver_id)
                        parts = raw_driver_info.split(", ")
                        if len(parts) == 2:
                            driver_id_value = parts[0].split(": ")[1] if ": " in parts[0] else parts[0]
                            driver_name_value = parts[1].split(": ")[1] if ": " in parts[1] else parts[1]
                            driver_info = f"\n*ID:* {driver_id_value}\n*Name:* {driver_name_value}"
                        else:
                            driver_info = f"\n{raw_driver_info}"
                    package_details += f"\n\nPackage is *in transit* by driver:{driver_info}."
                    # Create inline keyboard with a "Track on the map" button
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Track on the map", callback_data=f"track_on_map_{package_id}")]
                    ])
                else:
                    package_details += "\n\nThe package is marked as in transit, but transit details are not available."
            except Exception as e:
                print(f"Error fetching transit details: {str(e)}")
                package_details += "\n\nAn error occurred while fetching transit details."
        
        # Check for the "in warehouse" status as before
        elif package_details and "🚦 *status:* in warehouse" in package_details.lower():
            package_details += "\n\nThe package is currently *in our warehouse*, awaiting pickup by a driver."
        
        # Send the package details if they exist, otherwise show an error
        if package_details:
            if reply_markup:
                self.bot.sendMessage(chat_id, text=package_details, parse_mode="Markdown", reply_markup=reply_markup)
            else:
                self.bot.sendMessage(chat_id, text=package_details, parse_mode="Markdown")
        else:
            self.bot.sendMessage(chat_id, text="Failed to fetch package details. Please check the Package ID and try again.")


if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = "8159489225:AAGd897nlIv2JkkBuYwfyNXt4nAs15ILUNA"  # Replace with your actual bot token
    CATALOG2_API_URL = "http://127.0.0.1:8080"

    bot = RESTBot(TELEGRAM_BOT_TOKEN, CATALOG2_API_URL)

    # Keep the bot running
    print("🤖 Bot is running. Press Ctrl+C to exit.")
    while True:
        pass
