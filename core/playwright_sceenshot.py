import uuid, asyncio
import sys
from telegram.ext import ContextTypes
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8")

async def init_browser(app):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--single-process',
            '--use-angle=vulkan',
            '--enable-features=Vulkan',
            '--disable-software-rasterizer',
            '--disable-setuid-sandbox',
            '--no-zygote'
        ],
        timeout=60000
    )
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        java_script_enabled=True
    )
    page = await context.new_page()
    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)
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

    try:
        # Hardened navigation
        await page.goto(f"https://app.bubblemaps.io/{chain}/token/{address}", 
                      timeout=60000, 
                      wait_until="networkidle")

        # Retry-based dialog handling
        for attempt in range(3):
            try:
                await page.wait_for_selector('div.mdc-dialog_actions', state='visible', timeout=5000)
                await page.click('button:has-text("close")', timeout=3000)
                await page.wait_for_selector('div.mdc-dialog_actions', state='hidden', timeout=3000)
                break
            except Exception as e:
                if attempt == 2:
                    await page.evaluate('''() => {
                        document.querySelectorAll('.mdc-dialog').forEach(d => d.remove());
                    }''')

        # GPU-accelerated screenshot
        await page.emulate_media(media="screen")
        await page.screenshot(
            path=path,
            full_page=True,
            animations="disabled",
            type="jpeg",
            quality=90,
            timeout=30000
        )
        return path
    except Exception as e:
        print(f"❌ Screenshot failed: {str(e)}")
        return None

async def generate_screenshot(chain, address, context):
    bundle = context.bot_data.get("browser")
    if not bundle:
        return None
    return await take_screenshot(chain, address, bundle)