import asyncio
import os
from dotenv import load_dotenv
from src.scraper_service import ReviewScraperService

load_dotenv()

async def test_scraper():
    # The URL you provided (cleaned up)
    url = "https://www.google.com/maps/place/Domino's+Pizza+%7C+Baner,+Pune/@18.5767913,73.7645254,15z/data=!4m10!1m2!2m1!1sdominos+balewadi!3m6!1s0x3bc2beb510de7101:0x2687696d883315dd!8m2!3d18.5663995!4d73.7692747!15sChBkb21pbm9zIGJhbGV3YWRpWhIiEGRvbWlub3MgYmFsZXdhZGmSARBwaXp6YV9yZXN0YXVyYW50qgFGEAEqCyIHZG9taW5vcygAMh8QASIbWPtLyJbYQPrdlUFf0tpb3GehESQ6I1GVlj3nMhQQAiIQZG9taW5vcyBiYWxld2FkaeABAA!16s%2Fg%2F11ckdygxbp?entry=ttu&g_ep=EgoyMDI1MDkxNi4wIKXMDSoASAFQAw%3D%3D"
    
    print("Testing Google Maps scraper...")
    print(f"URL: {url}")
    print(f"Gemini API Key configured: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
    
    scraper = ReviewScraperService()
    
    try:
        reviews = await scraper.scrape_reviews(url, max_reviews=20)
        
        if reviews:
            print(f"\n✅ SUCCESS: Found {len(reviews)} reviews")
            print(f"Business: {scraper.business_info.get('name', 'Unknown')}")
            
            # Show first few reviews
            for i, review in enumerate(reviews[:3]):
                print(f"\nReview {i+1}:")
                print(f"  Name: {review.get('reviewer_name', 'N/A')}")
                print(f"  Rating: {review.get('rating', 'N/A')}")
                print(f"  Text: {review.get('review_text', 'N/A')[:100]}...")
                print(f"  Date: {review.get('review_date', 'N/A')}")
        else:
            print("\n❌ FAILED: No reviews found")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraper())