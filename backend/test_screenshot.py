from playwright.sync_api import sync_playwright

print("Starting screenshot debug script...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    print("Navigating...")
    page.goto("https://www.google.com/maps/place/Domino's+Pizza")
    page.wait_for_timeout(5000)
    
    # Accept cookies dialog if present
    try:
        page.locator("button >> text='Accept all'").click(timeout=2000)
        page.wait_for_timeout(2000)
    except:
        pass
        
    print("Taking initial screenshot...")
    page.screenshot(path="maps_debug.png", full_page=True)
    
    print("Attempting to click reviews...")
    # Click Reviews tab robustly
    try:
        # Standard localization text locator
        page.locator("button[role='tab'] >> text='Reviews'").click(timeout=3000)
    except:
        pass
            
    page.wait_for_timeout(3000)
    print("Taking explicit click screenshot...")
    page.screenshot(path="maps_debug_after_click.png", full_page=True)
    
    # Let's count reviews just to see
    count = page.locator(".jftiEf").count()
    print("Reviews found:", count)
    
    browser.close()
    print("Done")
