import uuid, asyncio
import sys
from telegram.ext import ContextTypes
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8")

async def init_browser(app):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    page = await context.new_page()
    app.bot_data["browser"] = {
        "playwright": playwright,
        "browser": browser,
        "context": context,
        "page": page
    }
    print("✅ Browser ready")

async def shutdown_browser(app):
    bundle = app.bot_data.get("browser")
    if bundle:
        await bundle["context"].close()
        await bundle["browser"].close()
        await bundle["playwright"].stop()
        print("🔒 Browser closed")

async def take_screenshot(chain: str, address: str, bundle) -> str | None:
    page = bundle["page"]
    path = f"/tmp/map_{chain}_{uuid.uuid4().hex[:6]}.png"

    url = f"https://app.bubblemaps.io/{chain}/token/{address}"
    print(f"🌐 Navigating to {url}")
    
    try:
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        print("🟢 Navigation complete")
    except Exception as nav_err:
        print(f"⚠️ Navigation warning: {nav_err}")

    # Targeted close handling for MDC dialog
    async def close_mdc_dialog():
        print("🔍 Targeting MDC dialog structure")
        try:
            # Wait for dialog container
            await page.wait_for_selector("div.mdc-dialog_actions", state="visible", timeout=5000)
            
            # Precise selector for close button
            close_btn = await page.wait_for_selector(
                "xpath=//div[contains(@class, 'mdc-dialog_actions')]//button[.//div[text()='close']]",
                state="visible",
                timeout=3000
            )
            
            # Scroll and click with human-like delay
            await close_btn.scroll_into_view_if_needed()
            await page.mouse.move(
                x=await close_btn.evaluate("el => el.offsetLeft + el.offsetWidth/2"),
                y=await close_btn.evaluate("el => el.offsetTop + el.offsetHeight/2"),
                steps=10
            )
            await close_btn.click(delay=150)
            print("✅ Clicked MDC close button")
            return True
        except Exception as e:
            print(f"⏭ MDC close failed: {str(e)[:100]}")
            return False

    # Execute close sequence
    popup_closed = await close_mdc_dialog()

    # Fallback sequence if primary method fails
    if not popup_closed:
        print("🔧 Attempting fallback methods")
        try:
            # Try alternative selectors
            await page.click("button[data-mdc-dialog-action='discard']", timeout=2000)
            print("✅ Closed using data attribute")
            popup_closed = True
        except:
            print("⏭ Data attribute method failed")

    # Verify closure
    if popup_closed:
        print("🕒 Waiting for dialog dismissal")
        try:
            await page.wait_for_selector("div.mdc-dialog_actions", state="hidden", timeout=3000)
            print("🔍 Verified dialog closed")
        except:
            print("⚠️ Dialog might still be present")

    # Final screenshot capture
    print("📸 Taking screenshot")
    try:
        await page.screenshot(
            path=path,
            full_page=True,
            animations="disabled",
            mask=[page.locator("div.mdc-dialog_actions")]
        )
        print(f"✅ Screenshot saved: {path}")
        return path
    except Exception as shot_err:
        print(f"❌ Screenshot error: {shot_err}")
        return None

async def generate_screenshot(chain, address, context):
    bundle = context.bot_data.get("browser")
    if not bundle:
        return None
    return await take_screenshot(chain, address, bundle)