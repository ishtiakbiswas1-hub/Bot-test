import logging
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "👋 Welcome to the Phone Number Info Bot!\n\n"
        "Send me any phone number with its country code (e.g., `+14155552671` or `+8801712345678`), "
        "and I will fetch its details and provide a Google Maps link."
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

# Handle incoming text messages (looking up phone numbers)
async def lookup_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_input = update.message.text.strip()

    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(text_input)

        # Check if the number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            await update.message.reply_text("❌ Invalid phone number or format. Make sure to include the country code (e.g., +1...).")
            return

        # Extract details
        country_loc = geocoder.description_for_number(parsed_number, "en")
        service_provider = carrier.name_for_number(parsed_number, "en")
        tz_info = timezone.time_zones_for_number(parsed_number)
        
        # Get international formatting
        intl_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        
        # Approximate latitude and longitude mapping trick based on country/region text
        # (For robust coordinate lookup, you can integrate a geocoding API like OpenCage or Nominatim)
        lat, lon = get_approximate_coordinates(country_loc)
        
        # Construct Google Maps Link
        if lat and lon:
            map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        else:
            map_link = f"https://www.google.com/maps/search/?api=1&query={country_loc.replace(' ', '+')}"

        # Build response text
        response = (
            f"📞 **Phone Info Results:**\n\n"
            f"• **Number:** `{intl_format}`\n"
            f"• **Country/Location:** {country_loc if country_loc else 'Unknown'}\n"
            f"• **Carrier:** {service_provider if service_provider else 'Unknown / Ported'}\n"
            f"• **Time Zone:** {', '.join(tz_info) if tz_info else 'Unknown'}\n\n"
            f"🗺️ [View Region on Google Map]({map_link})"
        )

        await update.message.reply_text(response, parse_mode="Markdown", disable_web_page_preview=False)

    except phonenumbers.NumberParseException:
        await update.message.reply_text("⚠️ Could not parse text as a phone number. Please send a valid number including '+' and country code.")

# Helper function to assign fallback approximate coordinates for country regions
def get_approximate_coordinates(country_name):
    # A lightweight mapping dictionary for demonstration 
    # (You can replace this or expand it using geocoding libraries)
    coordinates = {
        "United States": (37.0902, -95.7129),
        "Bangladesh": (23.6850, 90.3563),
        "United Kingdom": (55.3781, -3.4360),
        "India": (20.5937, 78.9629),
        "Canada": (56.1304, -106.3468),
    }
    return coordinates.get(country_name, (None, None))

def main():
    # Replace with your actual Telegram Bot Token from BotFather
    TOKEN = "8593503484:AAH9sC7aCeCY1bM-EStBRr66J3fdUAPthvg"

    application = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), lookup_number))

    # Run the bot
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
