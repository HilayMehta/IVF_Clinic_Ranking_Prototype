import re, statistics, asyncio, json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  

async def extract_clinic_data(page, url) -> dict:
    
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

   
    def clean(txt):
        return re.sub(r"\s+", " ", txt or "").strip()

    def num(x):
        try:
            return float(re.sub(r"[^\d.]", "", x))
        except ValueError:
            return None

    ## Clinic Name
    name = soup.find("h1", class_="provider__title").get_text(strip=True)
    
    ## Number of Doctors
    doctors_title = soup.find("div", class_="clinic-doctors__title").get_text(" ", strip=True)
    num_doctors_match = re.search(r"(\d+)\s+doctor", doctors_title, re.I)
    num_doctors = int(num_doctors_match.group(1)) if num_doctors_match else None

    ## Average doctor score 
    score_tag = soup.select_one(
    ".clinic-doctors__title figure.nps-badge.colors--doctor"
    )

    avg_doctor_score = None
    if score_tag:
        raw = score_tag.get_text(strip=True)        
        m = re.search(r"([\d.]+)", raw)             
        if m:
            avg_doctor_score = float(m.group(1))

    ## Annual Cycles
    annual_cycles = None
    cycles_tag = soup.find("div", class_="label", string=re.compile(r"Annual Cycles", re.I))
    if cycles_tag:
        count_div = cycles_tag.find_next_sibling("div", class_="count")
        if count_div:
            raw_cycles = re.sub(r"[^\d]", "", count_div.get_text(strip=True))
            if raw_cycles:                     
                annual_cycles = int(raw_cycles)

    ## National Annual Cycles
    national_annual_cycles = None
    nat_cycles_tag = soup.find("div", class_="label", string=re.compile(r"National Avg", re.I))
    if nat_cycles_tag:
        nat_count_div = nat_cycles_tag.find_next_sibling("div", class_="count")
        if nat_count_div:
            raw_nat_cycles = re.sub(r"[^\d]", "", nat_count_div.get_text(strip=True))
            if raw_nat_cycles:
                national_annual_cycles = int(raw_nat_cycles)

    ## Average Rating 
    avg_rating = None
    rating_fig = soup.select_one("figure.nps-chart.nps-chart--clinic")
    if rating_fig:
        raw_caption = rating_fig.find("figcaption")
        raw_text = rating_fig.find("text")
        combined = ""
        if raw_caption:
            combined += raw_caption.get_text(strip=True)
        if raw_text:
            combined += " " + raw_text.get_text(strip=True)
        m = re.search(r"([\d.]+)", combined)
        if m:
            avg_rating = float(m.group(1))

    ## Clinic Address
    address_div = soup.find("div", class_="branch-address")
    full_address = None
    if address_div:
        street = address_div.find("div", class_="branch-address__street")
        cityzip = address_div.find("div", class_="branch-address__city-zip")
        if street and cityzip:
            full_address = f"{street.get_text(strip=True)}, {cityzip.get_text(strip=True)}"


    ## Number of Reviews
    reviews_tag = soup.find("h3", class_="reviews-summary__count")
    num_reviews = None
    reviews_tag = soup.find("h3", class_="reviews-summary__count")
    if reviews_tag:
        m = re.search(r"(\d+)", reviews_tag.get_text(strip=True))
        if m:
            num_reviews = int(m.group(1))

    ## CDC Success Rates 
    age_bands = ["<35", "35-37", "38-40", ">40"]
    cdc_success_rates = {}

    bars = soup.select(".success-rates-chart__chart .bar--clinic")
    for idx, bar in enumerate(bars):
        m = re.search(r"height:(\d+(\.\d+)?)%", bar.get("style", ""))
        cdc_success_rates[age_bands[idx]] = float(m.group(1)) / 100 if m else None

    ## Mean of CDC Success Rates across age groups
    valid_rates = [v for v in cdc_success_rates.values() if v is not None]
    avg_cdc_success_rate = sum(valid_rates) / len(valid_rates) if valid_rates else None

    ## National CDC Success Rates

    bars_nat = soup.select(".success-rates-chart__chart .bar--national")
    national_cdc_rates = {}
    for idx, bar in enumerate(bars_nat):
        m = re.search(r"height:(\d+(\.\d+)?)%", bar.get("style", ""))
        national_cdc_rates[age_bands[idx]] = float(m.group(1)) / 100 if m else None
    
    ## Mean of National CDC Success Rates across age groups
    valid_nat = [v for v in national_cdc_rates.values() if v is not None]
    avg_national_cdc_success_rate = sum(valid_nat) / len(valid_nat) if valid_nat else None

    return {
        "name": name,
        "url": url,
        "number_of_doctors": num_doctors,
        "avg_doctor_score": avg_doctor_score,
        "annual_cycles": annual_cycles,
        "national_annual_cycles":national_annual_cycles,
        "avg_rating": avg_rating,
        "address": full_address,
        "num_reviews": num_reviews,
        "cdc_success_rates": cdc_success_rates,
        "avg_cdc_success_rate": avg_cdc_success_rate,
        "national_cdc_success_rates": national_cdc_rates,
        "avg_national_cdc_success_rate": avg_national_cdc_success_rate
    }


async def scrap(input_path, output_path):
    results = []

    with open(input_path, "r") as f:
        Clinic_Links = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        for url in Clinic_Links:
            page = await context.new_page()
            print("Scraping", url)
            try:
                await page.goto(url, timeout=60_000)
                await page.wait_for_selector("h1.provider__title", timeout=60_000)
                data = await extract_clinic_data(page, url)
                results.append(data)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)

            except Exception as e:
                print("Error scraping", url , ":", e)
            await page.close()
        await browser.close()

    print("Finished", len(results),  "clinics saved to scraped_clinics.json" )


if __name__ == "__main__":
    INPUT = os.path.join(ROOT_DIR, "data", "clinics_links.json")
    OUTPUT = os.path.join(ROOT_DIR, "data", "clinics_scrapped.json")
    asyncio.run(scrap(INPUT, OUTPUT))