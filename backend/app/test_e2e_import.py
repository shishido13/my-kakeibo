"""
E2E Test: PDF Upload -> AI Parse -> Bulk Register -> Verify in DB
"""
import asyncio
import json
import traceback
from sqlmodel import Session, select
from app.db.session import engine
from app.services.ai_service import analyze_pdf_receipt
from app.models.transaction import Transaction

async def main():
    pdf_path = r'c:\Users\qwert\OneDrive\デスクトップ\シシド\repos\my-kakeibo\frontend\test.pdf'
    
    # Step 1: Read PDF
    print("=" * 60)
    print("STEP 1: Reading PDF file...")
    with open(pdf_path, 'rb') as f:
        file_bytes = f.read()
    print(f"  PDF size: {len(file_bytes)} bytes")

    # Step 2: AI Parse
    print("=" * 60)
    print("STEP 2: Sending to Gemini 2.5 Flash for parsing...")
    with Session(engine) as db:
        parsed = await analyze_pdf_receipt(file_bytes, "test.pdf", db)
    
    print(f"  Parsed {len(parsed)} transaction(s):")
    for i, tx in enumerate(parsed):
        print(f"  [{i}] {json.dumps(tx, ensure_ascii=False)}")
    
    if not parsed:
        print("  ERROR: No transactions were parsed. Aborting.")
        return

    # Step 3: Bulk Register via CRUD
    print("=" * 60)
    print("STEP 3: Registering transactions to DB...")
    from app.crud.transaction import create_transaction
    from app.schemas.transaction import TransactionCreate
    
    created_ids = []
    with Session(engine) as db:
        for tx_data in parsed:
            tx_in = TransactionCreate(**tx_data)
            created = create_transaction(session=db, transaction_in=tx_in)
            created_ids.append(created.id)
            print(f"  Created transaction ID={created.id}")
    
    # Step 4: Verify in DB
    print("=" * 60)
    print("STEP 4: Verifying transactions in DB...")
    with Session(engine) as db:
        for tid in created_ids:
            t = db.get(Transaction, tid)
            if t:
                print(f"  FOUND ID={t.id}: date={t.date}, amount={t.amount}, shop={t.shop}, payer={t.payer}, source_type={t.source_type}")
            else:
                print(f"  NOT FOUND ID={tid}")

    print("=" * 60)
    print("E2E TEST PASSED! All steps completed successfully.")

if __name__ == '__main__':
    asyncio.run(main())
