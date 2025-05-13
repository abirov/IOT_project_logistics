import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import logging
import json
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class RESTBot:
    def __init__(self, token, catalog_url, influx_api_url, google_maps_key):
        self.tokenBot = token
        self.catalog_url = catalog_url
        self.influx_api_url = influx_api_url
        self.google_maps_key = google_maps_key
        self.bot = telepot.Bot(self.tokenBot)
        self.chatIDs = {}

        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
        logging.info("Bot is running. Waiting for messages...")

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        message = msg.get('text', '').strip().lower()
        print(f"🔹 Message received: {message} from {chat_id}")

        driver_shortcuts = {
            "d": "/driver_details", "de": "/driver_details", "det": "/driver_details",
            "p": "/pick_package", "pa": "/pick_package", "pan": "/panel",
        }
        warehouse_shortcuts = {
            "w": "/warehouse_details", "wa": "/warehouse_details", "war": "/warehouse_details",
            "t": "/tracking_packages", "tr": "/tracking_packages", "tra": "/tracking_packages",
            "r": "/register_package", "re": "/register_package", "reg": "/register_package",

        }

        if chat_id not in self.chatIDs:
            self.chatIDs[chat_id] = {"state": None, "driver_id": None, "warehouse_id": None, "role": None}

        role = self.chatIDs[chat_id].get("role")
        shortcuts = driver_shortcuts if role == "driver" else warehouse_shortcuts if role == "warehouse" else {}

        if message in shortcuts:
            message = shortcuts[message]

        if message == "/start":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚗 Driver", callback_data='enter_as_driver')],
                [InlineKeyboardButton(text="🏢 Warehouse User", callback_data='enter_as_warehouse')]
            ])
            self.bot.sendMessage(chat_id, text="Welcome to the Logistics Bot. Please choose your role:", reply_markup=keyboard)

        elif message == "/panel":
            driver_id = self.chatIDs[chat_id].get("driver_id")
            if driver_id:
                self.driver_panel(chat_id, driver_id)
            else:
                self.bot.sendMessage(chat_id, text="⚠️ You need to log in first. Use /start.")

        elif message == "/pick_package":
            driver_id = self.chatIDs[chat_id].get("driver_id")
            if driver_id:
                self.show_available_packages(chat_id, driver_id)
            else:
                self.bot.sendMessage(chat_id, text="⚠️ You need to log in first. Use /start.")

        elif message == "/driver_details":
            driver_id = self.chatIDs[chat_id].get("driver_id")
            if driver_id:
                self.send_driver_details(chat_id)
            else:
                self.bot.sendMessage(chat_id, text="⚠️ You need to log in first. Use /start.")

        elif self.chatIDs[chat_id]["state"] == "awaiting_package_id":
            self.track_package(chat_id, message)
            self.chatIDs[chat_id]["state"] = None

        elif message == "/warehouse_details":
            warehouse_id = self.chatIDs[chat_id].get("warehouse_id")
            if warehouse_id:
                self.send_warehouse_details(chat_id)
            else:
                self.bot.sendMessage(chat_id, text="⚠️ You need to log in first. Use /start.")

        elif message == "/tracking_packages":
            warehouse_id = self.chatIDs[chat_id].get("warehouse_id")
            if warehouse_id:
                self.show_in_transit_packages_for_warehouse(chat_id, warehouse_id)
            else:
                self.bot.sendMessage(chat_id, text="⚠️ You need to log in first. Use /start.")

        elif message == "/register_package":
            warehouse_id = self.chatIDs[chat_id].get("warehouse_id")
            if warehouse_id:
                # Trigger the registration process
                self.chatIDs[chat_id]["register_package_step"] = "start"
                self.chatIDs[chat_id]["register_package_data"] = {}
                self.chatIDs[chat_id]["package_submitted"] = False  # Reset in case of new registration
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="▶️ Start Registration", callback_data="start_register_package")]
                ])
                self.bot.sendMessage(chat_id, text="📦 Ready to register a new package.\nPlease enter each field carefully.", reply_markup=keyboard)
            else:
                self.bot.sendMessage(chat_id, text="⚠️ You need to log in first as Warehouse User. Use /start.")


        elif self.chatIDs[chat_id]["state"] == "awaiting_track_package_id":
            self.track_package(chat_id, message)
            self.chatIDs[chat_id]["state"] = None

        elif self.chatIDs[chat_id]["state"] == "awaiting_driver_id":
            self.fetch_driver_details(chat_id, message)

        elif self.chatIDs[chat_id]["state"] == "awaiting_warehouse_id":
            self.fetch_warehouse_details(chat_id, message)

        elif self.chatIDs[chat_id].get("register_package_step") == "name":
            self.chatIDs[chat_id]["register_package_data"]["name"] = message
            self.chatIDs[chat_id]["register_package_step"] = "confirm_name"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✔️ Confirm and Continue", callback_data="confirm_name")]])
            self.bot.sendMessage(chat_id, text=f"Selected: 📦 {message}", reply_markup=keyboard)

        elif self.chatIDs[chat_id].get("register_package_step") == "weight":
            try:
                weight = float(message)
                self.chatIDs[chat_id]["register_package_data"]["weight"] = weight
                self.chatIDs[chat_id]["register_package_step"] = "confirm_weight"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✔️ Confirm and Continue", callback_data="confirm_weight")]])
                self.bot.sendMessage(chat_id, text=f"Selected: ⚖️ {weight} kg", reply_markup=keyboard)
            except:
                self.bot.sendMessage(chat_id, text="❌ Invalid weight. Please enter a number.")

        elif self.chatIDs[chat_id].get("register_package_step") == "dimensions":
            try:
                dims = [float(x) for x in message.split(",")]
                self.chatIDs[chat_id]["register_package_data"]["dimensions"] = {"length": dims[0], "width": dims[1], "height": dims[2]}
                self.chatIDs[chat_id]["register_package_step"] = "confirm_dimensions"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✔️ Confirm and Continue", callback_data="confirm_dimensions")]])
                self.bot.sendMessage(chat_id, text=f"Selected: 📏 L:{dims[0]} W:{dims[1]} H:{dims[2]}", reply_markup=keyboard)
            except:
                self.bot.sendMessage(chat_id, text="❌ Invalid format. Please enter as length,width,height.")

        #elif self.chatIDs[chat_id].get("register_package_step") == "address":
            #self.chatIDs[chat_id]["register_package_data"]["delivery_address"] = message
            #self.chatIDs[chat_id]["register_package_step"] = "review"
            #keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Submit Package", callback_data="submit_package")]])
            #self.bot.sendMessage(chat_id, text=f"Selected: 📍 {message}\n\nReady to submit.", reply_markup=keyboard)
        
        elif self.chatIDs.get(chat_id, {}).get("register_package_step") == "address":
            self.chatIDs[chat_id]["register_package_data"]["delivery_address"] = message
            self.chatIDs[chat_id]["register_package_step"] = "review"
            self.show_package_review(chat_id)


        else:
            self.bot.sendMessage(chat_id, text="⚠️ Unsupported command. Use /start to begin.")

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print(f" Callback Query Data: {query_data}")

        if from_id not in self.chatIDs:
            self.chatIDs[from_id] = {"state": None, "driver_id": None}

        if query_data == 'track_package':
            self.chatIDs[from_id]["state"] = "awaiting_track_package_id"
            self.bot.sendMessage(from_id, text="Please enter the Package ID to track:")

        elif query_data == 'enter_as_driver':
            self.chatIDs[from_id]["state"] = "awaiting_driver_id"
            self.chatIDs[from_id]["role"] = "driver"
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
            package_id = query_data.split("_")[2]
            package_name = '_'.join(query_data.split("_")[3:])
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Yes, Reassign", callback_data=f"confirm_reassign_{package_id}")],
                [InlineKeyboardButton(text="❌ No, Cancel", callback_data="cancel_action")]
            ])
            self.bot.sendMessage(from_id, text=f"⚠️ Are you sure you want to reassign '{package_name}'?", reply_markup=keyboard)

        elif query_data.startswith("confirm_reassign_"):
            package_id = query_data.split("_")[2]
            self.cancel_package_assignment(from_id, package_id)

        elif query_data == "cancel_action":
            self.bot.sendMessage(from_id, text="❌ Action canceled.")

        elif query_data == 'enter_as_warehouse':
            self.chatIDs[from_id]["state"] = "awaiting_warehouse_id"
            self.chatIDs[from_id]["role"] = "warehouse"
            self.bot.sendMessage(from_id, text="Please enter the Warehouse Email or ID:")

        elif query_data == "view_warehouse_details":
            self.send_warehouse_details(from_id)

        elif query_data == "warehouse_tracking_packages":
            warehouse_id = self.chatIDs.get(from_id, {}).get("warehouse_id")
            if warehouse_id:
                self.show_in_transit_packages_for_warehouse(from_id, warehouse_id)
            else:
                self.bot.sendMessage(from_id, text="⚠️ You need to log in first. Use /start.")

        elif query_data.startswith("track_on_map_"):
            package_id = query_data.replace("track_on_map_", "")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Google Maps Link", callback_data=f"map_link_{package_id}")],
                [InlineKeyboardButton(text="🖼 Static Map Image", callback_data=f"map_static_{package_id}")]
            ])
            self.bot.sendMessage(from_id, text="How would you like to view it?", reply_markup=keyboard)

        elif query_data.startswith("map_link_"):
            package_id = query_data.replace("map_link_", "")
            self._send_maps_link(from_id, package_id)

        elif query_data.startswith("map_static_"):
            package_id = query_data.replace("map_static_", "")
            self._send_static_map(from_id, package_id)

        elif query_data.startswith("warehouse_pkg_details_"):
            package_id = query_data.replace("warehouse_pkg_details_", "")
            self.track_package(from_id, package_id)

        elif query_data == "warehouse_track_by_id":
            self.chatIDs[from_id]["state"] = "awaiting_track_package_id"
            self.bot.sendMessage(from_id, text="Please enter the Package ID to track:")

        elif query_data == "warehouse_register_package":
            self.chatIDs[from_id]["register_package_step"] = "start"
            self.chatIDs[from_id]["register_package_data"] = {}
            self.chatIDs[from_id]["package_submitted"] = False  # Reset submission flag
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="▶️ Start Registration", callback_data="start_register_package")]
            ])
            self.bot.sendMessage(from_id, text="Please enter each field carefully.", reply_markup=keyboard)

        elif query_data == "start_register_package":

            # Block edit package if already submitted
            if self.chatIDs.get(from_id, {}).get("package_submitted"):
                self.bot.sendMessage(from_id, text="✅ Package already submitted. Registration already completed.")
                return

            self.chatIDs[from_id]["register_package_step"] = "name"
            self.bot.sendMessage(from_id, text="Step 1/4 → Please enter the Package Name:")

        elif query_data == "confirm_name":
            self.chatIDs[from_id]["register_package_step"] = "weight"
            self.bot.sendMessage(from_id, text="Step 2/4 → Please enter the Package Weight (kg):")

        elif query_data == "confirm_weight":
            self.chatIDs[from_id]["register_package_step"] = "dimensions"
            self.bot.sendMessage(from_id, text="Step 3/4 → Please enter the Package Dimensions (L,W,H):")

        elif query_data == "confirm_dimensions":
            self.chatIDs[from_id]["register_package_step"] = "address"
            self.bot.sendMessage(from_id, text="Step 4/4 → Please enter the Delivery Address:")

        elif query_data == "submit_package":
            data = self.chatIDs[from_id]["register_package_data"]
            warehouse_id = self.chatIDs[from_id]["warehouse_id"]
            
            payload = {
                "name": data["name"],
                "weight": data["weight"],
                "dimensions": data["dimensions"],
                "warehouse_id": warehouse_id,
                "driver_id": None,
                "delivery_address": data["delivery_address"]
            }

            response = requests.post(f"{self.catalog_url}/packages/packages", json=payload)

            if response.status_code == 200:
                text_message = f"""✅ <b>PACKAGE REGISTERED SUCCESSFULLY</b> ✅

                📦 <b>Name:</b> {data['name']}
                ⚖️ <b>Weight:</b> {data['weight']} kg
                📏 <b>Dimensions:</b> {data['dimensions']}
                📍 <b>Address:</b> {data['delivery_address']}
                🏢 <b>Warehouse ID:</b> {warehouse_id}
                🚚 <b>Status:</b> in warehouse"""
                
                self.bot.sendMessage(from_id, text=text_message, parse_mode="HTML")

                # Mark as submitted to block further edits
                self.chatIDs[from_id]["package_submitted"] = True

            else:
                self.bot.sendMessage(from_id, text="❌ Failed to register package.")

            self.chatIDs[from_id]["register_package_step"] = None
            self.chatIDs[from_id]["register_package_data"] = {}

        #EDIT OPTIONS 
        elif query_data == "edit_name":

            if self.chatIDs.get(from_id, {}).get("package_submitted"):
                self.bot.sendMessage(from_id, text="✅ Package already submitted. Editing is not allowed.")
                return

            self.chatIDs[from_id]["register_package_step"] = "name"
            self.bot.sendMessage(from_id, text="✏️ Please enter the new Package Name:")

        elif query_data == "edit_weight":

            if self.chatIDs.get(from_id, {}).get("package_submitted"):
                self.bot.sendMessage(from_id, text="✅ Package already submitted. Editing is not allowed.")
                return

            self.chatIDs[from_id]["register_package_step"] = "weight"
            self.bot.sendMessage(from_id, text="✏️ Please enter the new Package Weight (kg):")

        elif query_data == "edit_dimensions":

            if self.chatIDs.get(from_id, {}).get("package_submitted"):
                self.bot.sendMessage(from_id, text="✅ Package already submitted. Editing is not allowed.")
                return

            self.chatIDs[from_id]["register_package_step"] = "dimensions"
            self.bot.sendMessage(from_id, text="✏️ Please enter the new Package Dimensions (L,W,H):")

        elif query_data == "edit_address":

            if self.chatIDs.get(from_id, {}).get("package_submitted"):
                self.bot.sendMessage(from_id, text="✅ Package already submitted. Editing is not allowed.")
                return

            self.chatIDs[from_id]["register_package_step"] = "address"
            self.bot.sendMessage(from_id, text="✏️ Please enter the new Delivery Address:")

        else:
            self.bot.sendMessage(from_id, text="❓ I didn't understand that action.")

        self.bot.answerCallbackQuery(query_id, text="")


    def fetch_driver_details(self, chat_id, identifier):
        """Fetch driver details from the catalog API and determine if the identifier is an email or driver ID."""
        identifier = identifier.strip()
        is_email   = "@" in identifier
        
        if is_email:
            url = f"{self.catalog_url}/drivers/drivers?driver_email={identifier}"
        else:
            url = f"{self.catalog_url}/drivers/drivers?driver_id={identifier}"

        try:
           
            response = requests.get(url, timeout=5)
            #logging.debug(f"API Response Status: {response.status_code}")

            if response.status_code == 200:
                driver = response.json()
                #logging.debug(f" Driver Data: {driver}")

                #do a case-insensitive 
                if is_email and not driver:
                    all_resp = requests.get(f"{self.catalog_url}/drivers/drivers", timeout=5)
                    if all_resp.status_code == 200:
                        for d in all_resp.json() or []:
                            if d.get('email','').lower() == identifier.lower():
                                driver = d
                                #logging.debug(f"Fallback matched driver: {driver}")
                                break

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
                    package_details = self.fetch_package_details(str(package['_id']))

                    '''# OLD FORMAT
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
            
                 #Old format
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
        """Change the package status from 'in warehouse' to 'in-transit'."""

        url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
        new_status = {"status": "in-transit"}

        try:
            response = requests.put(url, json=new_status, timeout=5)

            if response.status_code in [200, 201]:
                
                 self.chatIDs[chat_id]["package_status"] = "in-transit"
                 self.bot.sendMessage(chat_id, text="✅ Package status updated to 'in-transit'! 🚚")

                 
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
        """Change the package status from 'in-transit' to 'Delivered '."""

        url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
        new_status = {"status": "delivered"}

        try:
            response = requests.put(url, json=new_status, timeout=5)

            if response.status_code in [200, 201]:
                self.bot.sendMessage(chat_id, text="✅  Package successfully delivered! 🎉")
                self.send_driver_menu(chat_id)  


            else:
                self.bot.sendMessage(chat_id, text="⚠️ Failed to confirm delivery. Please try again.")

        except Exception as e:
            logging.error(f"❌ Error confirming package delivery: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ An unexpected error occurred while confirming delivery.")


        def cancel_package_assignment(self, chat_id, package_id):
        """Set the driver_id to None in the package document in MongoDB."""

        url = f"{self.catalog_url}/packages/packages?package_id={package_id}"

        
        try:
            package_resp = requests.get(url, timeout=5)
            if package_resp.status_code == 200:
                package = package_resp.json()
                status = package.get("status", "").lower()

                if status == "in-transit":
                    self.bot.sendMessage(chat_id, text="⚠️ The package is already 'in-transit' and cannot be reassigned.")
                    return
            else:
                self.bot.sendMessage(chat_id, text="❌ Failed to fetch package status from database.")
                return
        except Exception as e:
            logging.error(f"❌ Error checking package status: {str(e)}")
            self.bot.sendMessage(chat_id, text="⚠️ Could not verify package status. Please try again.")
            return

        # reassignement 
        data = {"driver_id": None}

        try:
            response = requests.put(url, json=data, timeout=5)
            if response.status_code in [200, 204]:
                self.bot.sendMessage(chat_id, text="🔄 Order has been cancelled and is now available for other Drivers.")
                self.send_driver_menu(chat_id)
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
        """Send the driver-specific menu to user."""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 View My Details", callback_data="view_driver_details")],
            [InlineKeyboardButton(text="📦 Pick Up a Package", callback_data="show_available_packages")],
            [InlineKeyboardButton(text="📂 My Panel", callback_data="driver_panel")]
        ])
        self.bot.sendMessage(chat_id, text="What would you like to do?", reply_markup=keyboard)


    def driver_panel(self, chat_id, driver_id):
        """Fetch and display all packages assigned to the driver, filtering out delivered packages."""
        url = f"{self.catalog_url}/packages/packages?driver_id={str(driver_id)}"

        try:
            response = requests.get(url, timeout=5)
            #logging.debug(f"API Response Status: {response.status_code}")
            #logging.debug(f"API Response Content: {response.text}")  

            if response.status_code == 200:
                try:
                    packages = response.json()

                    # Ensure packages is always a list of dicts
                    if not isinstance(packages, list):
                        packages = [packages]

                    # Filter out non-dict items
                    packages = [p for p in packages if isinstance(p, dict)]

                except Exception as e:
                    packages = []

                if not packages:
                    self.bot.sendMessage(chat_id, text="📦 You have no assigned packages at the moment.")
                    return

                for package in packages:
                    if package.get('status') != 'delivered':
                        package_info = self.fetch_package_details(package['_id'])
                        
                        #Old format
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
                        if package.get('status') == 'in-transit':
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
        url = f"{self.catalog_url}/packages/packages?package_id={package_id}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            package = response.json()
            if isinstance(package, str):
                package = json.loads(package)
            if not package:
                return 

            # Normalize address into a single string:
            addr = package.get("delivery_address")    #ADR COULD BE: a dict, a string or None
            if isinstance(addr, dict):                #if addr is a diet then:
                city   = addr.get("city",   "N/A")
                street = addr.get("street", "N/A")
                zipc   = addr.get("zipcode","N/A")
                delivery_addr = f"{city}, {street} ({zipc})"    # now delivery_addr is guaranteed to be a string like

            else:
                # could be None or already a string
                delivery_addr = addr or "N/A"

            warehouse_info = self.get_warehouse_details(str(package.get("warehouse_id"))) \
                            if package.get("warehouse_id") else "Warehouse details not available."

            package_info = (
                f"📦 *Package Details:*\n"
                f"🆔 *ID:* {package.get('_id','N/A')}\n"
                f"📦 *Name:* {package.get('name','N/A')}\n"
                f"⚖️ *Weight:* {package.get('weight','N/A')} kg\n"
                f"📏 *Dimensions:* "
                f"{package.get('dimensions',{}).get('length','N/A')} x "
                f"{package.get('dimensions',{}).get('width','N/A')} x "
                f"{package.get('dimensions',{}).get('height','N/A')} cm\n"
                f"🏢 *Warehouse:* {warehouse_info}\n"
                f"📍 *Delivery Address:* {delivery_addr}\n"
                f"🚦 *Status:* {package.get('status','N/A')}"
            )
            return package_info

        except requests.RequestException as e:
            return f"Error fetching package details: {e}"
        except Exception as e:
            logging.error(f"Error in fetch_package_details formatting: {e}")
            return "Package details not available."


    def get_warehouse_details(self, warehouse_id):
        """Fetches warehouse details from the catalog API using the warehouse ID."""
        warehouse_details_url = f"{self.catalog_url}/warehouses/warehouses?warehouse_id={str(warehouse_id)}"
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


    def fetch_warehouse_details(self, chat_id, identifier):
        """Fetch warehouse details from the catalog API using ID or email."""
        identifier = identifier.strip()
        is_email   = '@' in identifier

        if is_email:
            url = f"{self.catalog_url}/warehouses/warehouses?warehouse_email={identifier}"
        else:
            url = f"{self.catalog_url}/warehouses/warehouses?warehouse_id={identifier}"

        try:
            response = requests.get(url, timeout=5)
            #logging.debug(f"API Response Status (Warehouse): {response.status_code}")

            if response.status_code == 200:
                warehouse = response.json()
                logging.debug(f" Warehouse Data: {warehouse}")
                
             
                if is_email and not warehouse:
                    all_resp = requests.get(f"{self.catalog_url}/warehouses/warehouses", timeout=5)
                    if all_resp.status_code == 200:
                        candidates = all_resp.json() or []
                        #logging.debug(f" Warehouse fallback fetched {len(candidates)} records")
                        for w in candidates:
                            if w.get('email','').lower() == identifier.lower():
                                warehouse = w
                                #logging.debug(f"Warehouse fallback matched: {warehouse}")
                                break

                if warehouse:
                    self.chatIDs[chat_id] = {"state": "warehouse_logged_in", "warehouse_id": warehouse["_id"]}

                    welcome_message = f"🏢 Welcome to *{warehouse['name']}*!\n"
                    self.bot.sendMessage(chat_id, text=welcome_message, parse_mode="Markdown")

                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="📜 View Warehouse Details", callback_data="view_warehouse_details")],
                        [InlineKeyboardButton(text="📦 Track Packages [NEW]", callback_data='warehouse_tracking_packages')],
                        [InlineKeyboardButton(text="➕ Register Package", callback_data='warehouse_register_package')]
                    ])
                    self.bot.sendMessage(chat_id, text="What would you like to do?", reply_markup=keyboard)

                else:
                    self.bot.sendMessage(chat_id, text="⚠️ No warehouse found with that ID or email.")
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

        url = f"{self.catalog_url}/warehouses/warehouses?warehouse_id={str(warehouse_id)}"

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


    def track_package(self, chat_id, package_id):
        """Fetch and display package details using the package ID."""
        #print(f"📦 Fetching package details for Package ID: {package_id}")
        package_details = self.fetch_package_details(package_id)
        reply_markup = None 
        
        # if package is delivered:
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
        
        # if package is: "in transit"
        elif package_details and "🚦 *status:* in-transit" in package_details.lower():

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
                    package_details += f"\n\nPackage is *in-transit* by driver:{driver_info}."
                   
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Track on the map", callback_data=f"track_on_map_{package_id}")]
                    ])
                else:
                    package_details += "\n\nThe package is marked as in-transit, but transit details are not available."
            except Exception as e:
                print(f"Error fetching transit details: {str(e)}")
                package_details += "\n\nAn error occurred while fetching transit details."
        
        # if package "in warehouse" 
        elif package_details and "🚦 *status:* in warehouse" in package_details.lower():
            package_details += "\n\nThe package is currently *in our warehouse*, awaiting pickup by a driver."
  
        if package_details:
            if reply_markup:
                self.bot.sendMessage(chat_id, text=package_details, parse_mode="Markdown", reply_markup=reply_markup)
            else:
                self.bot.sendMessage(chat_id, text=package_details, parse_mode="Markdown")
        else:
            self.bot.sendMessage(chat_id, text="Failed to fetch package details. Please check the Package ID and try again.")
    

    def get_driver_info(self, driver_id):
        """Fetch a drivers basic info (ID & name) from the API jst for using above def"""
        url = f"{self.catalog_url}/drivers/drivers?driver_id={driver_id}"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            d = resp.json() or {}
            # build  the string 
            return f"ID: {d.get('_id','N/A')}, Name: {d.get('name','N/A')}"
        except Exception:
            return "ID: N/A, Name: N/A"
    

    def show_in_transit_packages_for_warehouse(self, chat_id, warehouse_id):
        """Fetch and display all in-transit packages for a warehouse with buttons."""
        url = f"{self.catalog_url}/packages/packages?warehouse_id={warehouse_id}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            packages = response.json()
            if isinstance(packages, dict):
                packages = [packages]  # handle single package case

            # Filter in transit packages
            in_transit_packages = [p for p in packages if p.get("status", "").lower() == "in-transit"]

            if in_transit_packages:
                # Build buttons
                buttons = []
                for pkg in in_transit_packages:
                    pkg_id = pkg.get("_id", "N/A")
                    pkg_name = pkg.get("name", "Unnamed")
                    buttons.append([InlineKeyboardButton(text=f"📦 {pkg_name} ({pkg_id})", callback_data=f"warehouse_pkg_details_{pkg_id}")])

                # extra button for delivered/warehouse/global
                buttons.append([InlineKeyboardButton(text="➡️ Track Delivered / Global Search", callback_data="warehouse_track_by_id")])

                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_id, text="📦 *In-Transit Packages:*", parse_mode="Markdown", reply_markup=keyboard)

            else:
                self.bot.sendMessage(chat_id, text="No in-transit packages found for your warehouse.")

        except Exception as e:
            print(f"Error fetching packages: {e}")
            self.bot.sendMessage(chat_id, text="Failed to fetch package list. Please try again later.")


    def register_package(self, chat_id, package_data):
        """Send package data to backend to create package"""
        url = f"{self.catalog_url}/packages/packages"
        try:
            response = requests.post(url, json=package_data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                package_id = result.get("package_id")
                self.bot.sendMessage(chat_id, text=f"✅ Package registered successfully! Package ID: {package_id}")
            else:
                self.bot.sendMessage(chat_id, text="❌ Failed to register package.")
        except Exception as e:
            self.bot.sendMessage(chat_id, text=f"⚠️ Error occurred: {str(e)}")


    def show_package_review(self, chat_id):
        data = self.chatIDs[chat_id]["register_package_data"]

        summary = (
            f"📦 Package Registration Review:\n\n"
            f"Name: {data.get('name', '❌ Not set')}\n"
            f"Weight: {data.get('weight', '❌ Not set')} kg\n"
            f"Dimensions: {data.get('dimensions', '❌ Not set')}\n"
            f"Address: {data.get('delivery_address', '❌ Not set')}\n"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Edit Name", callback_data="edit_name")],
            [InlineKeyboardButton(text="✏️ Edit Weight", callback_data="edit_weight")],
            [InlineKeyboardButton(text="✏️ Edit Dimensions", callback_data="edit_dimensions")],
            [InlineKeyboardButton(text="✏️ Edit Address", callback_data="edit_address")],
            [InlineKeyboardButton(text="✅ Submit Package", callback_data="submit_package")],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_action")]
        ])

        self.bot.sendMessage(chat_id, text=summary, reply_markup=keyboard)


    def _send_maps_link(self, chat_id, package_id):
        
        #print(f"[DEBUG] ▶️ Start _send_maps_link for package_id={package_id}")

        # 1) Get driver_id from package
        pkg_resp = requests.get(
            f"{self.catalog_url}/packages/packages?package_id={package_id}",
            timeout=5
        )
        #print(f"[DEBUG] pkg HTTP {pkg_resp.status_code}: {pkg_resp.text}")
        try:
            pkg = pkg_resp.json()
        except ValueError as e:
            print(f"[ERROR] cannot parse pkg JSON: {e}")
            return self.bot.sendMessage(chat_id, "❌ Failed to parse package response.")

        driver_id = pkg.get("driver_id")
        #print(f"[DEBUG] driver_id = {driver_id!r}")
        if not driver_id:
            return self.bot.sendMessage(chat_id, "❌ That package has no driver assigned.")

        # 2) Get vehicle_id from driver record
        drv_resp = requests.get(
            f"{self.catalog_url}/drivers/drivers?driver_id={driver_id}",
            timeout=5
        )
        #print(f"[DEBUG] drv HTTP {drv_resp.status_code}: {drv_resp.text}")
        try:
            drv = drv_resp.json()
        except ValueError as e:
            print(f"[ERROR] cannot parse driver JSON: {e}")
            return self.bot.sendMessage(chat_id, "❌ Failed to parse driver response.")

        vehicle_id = drv.get("vehicle_id")
        #print(f"[DEBUG] vehicle_id = {vehicle_id!r}")
        if not vehicle_id:
            return self.bot.sendMessage(chat_id, "❌ No vehicle_id found for that driver.")

        # 3) get Influx data
        influx_resp = requests.get(
            f"{self.influx_api_url}/location",
            params={"vehicle_id": vehicle_id, "period": "1000h"},
            timeout=5
        )
        #print(f"[DEBUG] influx HTTP {influx_resp.status_code}: {influx_resp.text[:200]}…")
        pts = influx_resp.text

        # handle possible string payload
        if isinstance(pts, str):
            try:
                pts = json.loads(pts)
            except json.JSONDecodeError as e:
                print(f"[ERROR] cannot decode influx JSON: {e}")
                return self.bot.sendMessage(chat_id, "❌ Unexpected response format from location service.")
        #print(f"[DEBUG] parsed pts list length = {len(pts) if isinstance(pts, list) else 'not a list'}")

        if not pts:
            return self.bot.sendMessage(chat_id, "ℹ️ No location data stored yet.")

        # 4) Newest point is first element
        latest = pts[0]
        print(f"[DEBUG] latest point = {latest}")
        lat, lon = latest.get("latitude"), latest.get("longitude")
        #print(f"[DEBUG] lat, lon = {lat}, {lon}")

        # 5) Send live Google Maps link
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        self.bot.sendMessage(
            chat_id,
            f"🔗 Last stored location of package *{package_id}*:\n"
            f"`{lat:.6f}, {lon:.6f}`\n"
            f"[Open in Google Maps]({maps_link})",
            parse_mode="Markdown"
        )
        print("[DEBUG] ✅ map link sent")



    def _send_static_map(self, chat_id, package_id):
        """
        1) Fetch package → driver_id
        2) Fetch driver  → vehicle_id
     
        """
        # 1) Get driver_id from package
        pkg = requests.get(
            f"{self.catalog_url}/packages/packages?package_id={package_id}",
            timeout=5
        ).json()
        driver_id = pkg.get("driver_id")
        if not driver_id:
            return self.bot.sendMessage(chat_id,
                "❌ That package has no driver assigned.")

        # 2) Get vehicle_id from driver
        drv = requests.get(
            f"{self.catalog_url}/drivers/drivers?driver_id={driver_id}",
            timeout=5
        ).json()
        vehicle_id = drv.get("vehicle_id")
        if not vehicle_id:
            return self.bot.sendMessage(chat_id,
                "❌ No vehicle_id found for that driver.")

        # 3) Fetch Influx data
        resp = requests.get(
            f"{self.influx_api_url}/location",
            params={"vehicle_id": vehicle_id, "period": "10000h"},
            timeout=5
        )
        pts = resp.json()

        # unwrap stringified JSON if necessary
        if isinstance(pts, str):
            try:
                pts = json.loads(pts)
            except json.JSONDecodeError:
                return self.bot.sendMessage(chat_id, "❌ Unexpected format from location service.")

        if not pts:
            return self.bot.sendMessage(chat_id, "ℹ️ No location data stored yet.")


        # 4) Extract newest coords
        lat, lon = pts[0]["latitude"], pts[0]["longitude"]

        # 5) Build Static Map URL
        static_url = (
            "https://maps.googleapis.com/maps/api/staticmap"
            f"?center={lat},{lon}&zoom=15&size=600x300"
            f"&markers=color:red|label:P|{lat},{lon}"
            f"&key={self.google_maps_key}"
        )
        logging.debug(f"🔑 Using Google Maps key: {self.google_maps_key}")

        # 5a) Fetch and validate
        map_resp = requests.get(static_url, timeout=5)
        if map_resp.status_code != 200 or 'image' not in map_resp.headers.get('Content-Type', ''):
            #logging.error(f"Static Maps error {map_resp.status_code}: {map_resp.text}")
            return self.bot.sendMessage(
                chat_id,
                "❌ Could not fetch map image. Check your Google API key & Static Maps settings."
            )
        img_data = map_resp.content

        
        # 6) Save & send the image
        temp_path = "pkg_loc.png"
        with open(temp_path, "wb") as f:
            f.write(img_data)
        with open(temp_path, "rb") as f:
            self.bot.sendPhoto(
                chat_id,
                f,
                caption=f"🖼 Last stored location of package *{package_id}*",
                parse_mode="Markdown"
            )



if __name__ == "__main__":
    
    config_path = os.path.join(os.path.dirname(__file__), "botconfig.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    TELEGRAM_BOT_TOKEN = config["telegram_token"]
    CATALOG2_API_URL   = config["catalog_api_url"]
    INFLUX_API_URL     = config["influx_api_url"]
    GOOGLE_MAPS_KEY    = config["google_maps_key"]

    # Start bot
    bot = RESTBot(
        TELEGRAM_BOT_TOKEN,
        CATALOG2_API_URL,
        INFLUX_API_URL,
        GOOGLE_MAPS_KEY
    )

    print("Bot is running. Press Ctrl+C to exit.")
    while True:
        pass
