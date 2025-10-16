"""
Backfill script to evaluate call_success_status using Gemini 2.5 Flash API
for all existing calls that don't have a status yet.

Usage:
    python scripts/backfill_gemini_evaluation.py

Options:
    --batch-size: Number of calls to process at once (default: 5)
    --dry-run: Preview what will be processed without making changes
    --limit: Maximum number of calls to process (for testing)
"""

import asyncio
import argparse
import os
import sys
import time
from datetime import datetime
from sqlalchemy import create_engine, text  # FIXED: Added text import
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import httpx
import google.generativeai as genai

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_test.db import update_call_success_status
from database.db_test import models

# Load environment variables
load_dotenv("/app/.env.local")

# Configuration
DATABASE_URL = os.getenv("POSTGRES_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://mysyara-prod-bk.vaaniresearch.com/api")

if not DATABASE_URL:
    raise ValueError("POSTGRES_URL not found in environment variables")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to .env.local")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Database setup with connection pooling and retry settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=2,
    connect_args={
        "connect_timeout": 10,
        # "options": "-c statement_timeout=30000"
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Statistics
stats = {
    "total_calls": 0,
    "already_evaluated": 0,
    "transcript_not_found": 0,
    "success": 0,
    "failure": 0,
    "undetermined": 0,
    "errors": 0
}

def get_db_with_retry(max_retries=3):
    """Get database session with retry logic"""
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test connection - FIXED: wrap in text()
            db.execute(text("SELECT 1"))
            return db
        except Exception as e:
            print(f"  ⚠️  Database connection attempt {attempt + 1}/{max_retries} failed")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"  ⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                raise
    return None

async def fetch_transcript_via_api(call_id: str) -> str:
    """Fetch transcript using the transcript API endpoint"""
    try:
        url = f"{BASE_URL}/transcript/{call_id}"
        print(f"  📄 Fetching transcript from API: {url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                print(f"  ❌ API returned status code: {response.status_code}")
                return None
            
            data = response.json()
            transcript = data.get("transcript", "")
            
            # Check if transcript is valid
            if not transcript or transcript in [
                "Transcript not found in S3",
                "Transcript is empty",
                "Error fetching transcript",
                "Waiting for Transcription to be available. Please try again after the call is over."
            ]:
                print(f"  ⚠️  Transcript not available: {transcript[:50] if transcript else 'Empty'}...")
                return None
            
            print(f"  ✅ Transcript fetched ({len(transcript)} chars)")
            return transcript
            
    except httpx.TimeoutException:
        print(f"  ❌ Timeout fetching transcript")
        return None
    except Exception as e:
        print(f"  ❌ Error fetching transcript: {e}")
        return None

def evaluate_with_gemini(transcript: str) -> dict:
    """Evaluate call success using Gemini 2.5 Flash"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""You are evaluating a customer service call transcript to determine if it was successful.

Evaluation Criteria:
- Did the conversation go well, primarily from the customer's perspective?
- Were all customer questions answered satisfactorily?
- Were there any unresolved issues or imperfect responses?

Rules:
- Respond with ONLY ONE WORD: "Success", "Failure", or "Undetermined"
- Success: Customer's needs were met, questions answered, positive resolution
- Failure: Customer frustrated, unresolved issues, poor service
- Undetermined: Insufficient information, call dropped early, unclear outcome

Transcript:
{transcript}

Your one-word evaluation:"""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=10,
            )
        )
        
        result_text = response.text.strip()
        valid_statuses = ["Success", "Failure", "Undetermined"]
        
        for status in valid_statuses:
            if status.lower() in result_text.lower():
                return {"status": status, "status_code": 200}
        
        print(f"  ⚠️  Unexpected response from Gemini: {result_text}")
        return {"status": "Undetermined", "status_code": 200}
        
    except Exception as e:
        print(f"  ❌ Error calling Gemini API: {e}")
        return {"status": "Undetermined", "status_code": 400, "error": str(e)}

async def process_call(call, dry_run=False):
    """Process a single call to evaluate success status"""
    call_id = call.call_id
    print(f"\n🔄 Processing call: {call_id}")
    print(f"  Started at: {call.call_started_at}")
    print(f"  Type: {call.call_type}")
    
    transcript = await fetch_transcript_via_api(call_id)
    
    if not transcript:
        print(f"  ⚠️  Transcript not found or empty")
        stats["transcript_not_found"] += 1
        
        if not dry_run:
            update_call_success_status(call_id, "Undetermined")
            print(f"  ✅ Set status to: Undetermined (no transcript)")
            stats["undetermined"] += 1
        else:
            print(f"  [DRY RUN] Would set status to: Undetermined")
        return
    
    try:
        print(f"  🤖 Evaluating with Gemini 2.5 Flash...")
        success_eval = evaluate_with_gemini(transcript)
        
        if success_eval["status_code"] == 200:
            status = success_eval["status"]
            print(f"  ✅ Evaluation result: {status}")
            
            if not dry_run:
                update_call_success_status(call_id, status)
                print(f"  💾 Database updated")
                stats[status.lower()] += 1
            else:
                print(f"  [DRY RUN] Would set status to: {status}")
        else:
            print(f"  ❌ Evaluation failed: {success_eval.get('error')}")
            stats["errors"] += 1
            
            if not dry_run:
                update_call_success_status(call_id, "Undetermined")
                stats["undetermined"] += 1
                
    except Exception as e:
        print(f"  ❌ Error during evaluation: {e}")
        stats["errors"] += 1
        
        if not dry_run:
            update_call_success_status(call_id, "Undetermined")
            stats["undetermined"] += 1

async def backfill_calls(batch_size=5, dry_run=False, limit=None):
    """Main function to backfill all calls"""
    print("=" * 80)
    print("🚀 CALL SUCCESS STATUS BACKFILL SCRIPT (GEMINI 2.5 FLASH)")
    print("=" * 80)
    
    if dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made to database")
    
    print(f"\n📊 Configuration:")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Limit: {limit if limit else 'No limit'}")
    print(f"  - Database: {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'Local'}")
    print(f"  - API Base URL: {BASE_URL}")
    print(f"  - Model: Gemini 2.5 Flash")
    
    print(f"\n🔌 Connecting to database...")
    db = None
    try:
        db = get_db_with_retry(max_retries=3)
        print(f"  ✅ Database connection established")
    except Exception as e:
        print(f"\n❌ Failed to connect to database after 3 attempts")
        print(f"Error: {e}")
        return
    
    try:
        print(f"\n📋 Querying database for unevaluated calls...")
        query = db.query(models.Call).filter(
            models.Call.call_success_status.is_(None)
        ).order_by(models.Call.call_started_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        calls_to_process = query.all()
        stats["total_calls"] = len(calls_to_process)
        
        print(f"  ✅ Found {stats['total_calls']} calls to process")
        
        if stats["total_calls"] == 0:
            print("\n✅ All calls already have success status!")
            return
        
        total_calls_in_db = db.query(models.Call).count()
        already_evaluated = db.query(models.Call).filter(
            models.Call.call_success_status.isnot(None)
        ).count()
        stats["already_evaluated"] = already_evaluated
        
        print(f"\n📊 Database stats:")
        print(f"  - Total calls in DB: {total_calls_in_db}")
        print(f"  - Already evaluated: {already_evaluated}")
        print(f"  - To be processed: {stats['total_calls']}")
        
        if not dry_run:
            confirm = input(f"\n⚠️  Proceed with evaluation of {stats['total_calls']} calls? (yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ Aborted by user")
                return
        
        print(f"\n🔄 Starting evaluation...")
        print("=" * 80)
        
        for i in range(0, len(calls_to_process), batch_size):
            batch = calls_to_process[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(calls_to_process) + batch_size - 1) // batch_size
            
            print(f"\n📦 Batch {batch_num}/{total_batches} ({len(batch)} calls)")
            print("-" * 80)
            
            for call in batch:
                await process_call(call, dry_run)
            
            processed = min(i + batch_size, len(calls_to_process))
            print(f"\n✅ Progress: {processed}/{len(calls_to_process)} calls processed")
            
            if i + batch_size < len(calls_to_process):
                print("⏳ Waiting 3 seconds before next batch...")
                await asyncio.sleep(3)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("💾 Progress has been saved to database")
    except Exception as e:
        print(f"\n❌ Error during backfill: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db:
            db.close()
    
    print("\n" + "=" * 80)
    print("📊 BACKFILL COMPLETE - FINAL STATISTICS")
    print("=" * 80)
    print(f"Total calls processed:        {stats['total_calls']}")
    print(f"Already evaluated (skipped):  {stats['already_evaluated']}")
    print(f"Transcript not found:         {stats['transcript_not_found']}")
    print(f"")
    print(f"Evaluation Results:")
    print(f"  ✅ Success:                 {stats['success']}")
    print(f"  ❌ Failure:                 {stats['failure']}")
    print(f"  ⚠️  Undetermined:           {stats['undetermined']}")
    print(f"  🔥 Errors:                  {stats['errors']}")
    print("=" * 80)
    
    if dry_run:
        print("\n⚠️  This was a DRY RUN - no changes were made")
        print("Run without --dry-run to apply changes")

def main():
    parser = argparse.ArgumentParser(
        description="Backfill call_success_status using Gemini 2.5 Flash"
    )
    parser.add_argument("--batch-size", type=int, default=5, help="Number of calls to process in each batch (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Preview what will be processed without making changes")
    parser.add_argument("--limit", type=int, help="Maximum number of calls to process (for testing)")
    
    args = parser.parse_args()
    
    asyncio.run(backfill_calls(
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        limit=args.limit
    ))

if __name__ == "__main__":
    main()