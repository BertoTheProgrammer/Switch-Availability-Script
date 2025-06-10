import os
from playwright.sync_api import sync_playwright
import requests

WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def notify(product, quantity):
    if not WEBHOOK_URL:
        print("❌ Discord webhook not set.")
        return

    data = {
        "content": f"🚨 {product} has quantity {quantity}!"
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print(f"✅ Notification sent for {product}")
    else:
        print(f"❌ Failed to send notification (status {response.status_code})")

def check_inventory():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.switchsniper.com/current-inventory")

        page.wait_for_selector("select")

        # Select Arizona using its value attribute
        page.select_option("select", value="AZ")

        # Optional: Wait for page to update (if it's dynamic)
        page.wait_for_timeout(3000)

        print("Arizona selected!")

        try:
            page.wait_for_selector("table tbody tr", timeout=10000)
        except Exception:
            print("❌ Table not found or took too long to load.")
            return

        rows = page.query_selector_all("table tbody tr")
        print(f"✅ Found {len(rows)} rows.")

        found = False

        for row in rows:
            cols = row.query_selector_all("td")
            if len(cols) >= 7:
                product = cols[0].inner_text().strip()
                quantity_text = cols[6].inner_text().strip()
                try:
                    quantity = int(quantity_text)
                    if quantity == 1:
                        print(f"🔔 {product}: {quantity}")
                        notify(product, quantity)
                        found = True
                except ValueError:
                    print(f"⚠️ Could not parse quantity: {quantity_text}")

        if not found:
            print("ℹ️ No products with quantity > 1")

        browser.close()

if __name__ == "__main__":
    check_inventory()
