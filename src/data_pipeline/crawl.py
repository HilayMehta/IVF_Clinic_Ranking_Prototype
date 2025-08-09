from playwright.sync_api import sync_playwright
import time
import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  

def crawl_fertilityiq(output_path):
    base_url = "https://www.fertilityiq.com/fertilityiq/provider_search?location_type=all_us&type=clinic"
    clinic_links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base_url)

        
        page.wait_for_selector("a[href*='/fertilityiq/clinics/']", timeout=10000)

        
        prev_height = 0
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.5) 
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == prev_height:
                break
            prev_height = new_height

        
        links = page.query_selector_all("a[href*='/fertilityiq/clinics/']")
        for link in links:
            href = link.get_attribute("href")
            if href:
                full_url = "https://www.fertilityiq.com" + href
                clinic_links.add(full_url)

        browser.close()

    print("Found", len(clinic_links), "clinic links:")
    for link in clinic_links:
        print(link)

    with open(output_path, "w") as f:
        json.dump(list(clinic_links), f, indent=2)

    
if __name__ == "__main__":
    OUTPUT = os.path.join(ROOT_DIR, "data", "clinics_links.json")
    crawl_fertilityiq(OUTPUT)
