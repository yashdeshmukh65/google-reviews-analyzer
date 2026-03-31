import time
from scraper import get_google_reviews

# Highly specific URL to avoid Maps disambiguation
url = "https://www.google.com/maps/place/Golden+Gate+Bridge/@37.8199286,-122.4804438,17z/data=!3m1!4b1!4m6!3m5!1s0x808586e145c08615:0x5e0248f7dff78fb2!8m2!3d37.8199286!4d-122.4782551!16zL20vMDM1ZjA=?"

print("Starting scrape test with highly specific URL...")
start = time.time()
reviews = get_google_reviews(url, max_reviews=20)
end = time.time()
print(f"Scrape completed in {end-start:.2f} seconds.")
print(f"Found {len(reviews)} reviews.")
if reviews:
    print("Sample:", reviews[0])
