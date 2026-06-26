"""
Export CSV des résultats
"""
import csv
import io
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/export", tags=["export"])

@router.get("/clubs.csv")
async def export_clubs_csv():
    """Export CSV de tous les clubs."""
    import aiosqlite
    from main import DB_PATH

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM clubs") as cur:
            rows = await cur.fetchall()

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=dict(rows[0]).keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=clubs.csv"}
    )

@router.get("/partners.csv")
async def export_partners_csv():
    """Export CSV de tous les partenaires."""
    import aiosqlite
    from main import DB_PATH

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM partners") as cur:
            rows = await cur.fetchall()

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=dict(rows[0]).keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=partners.csv"}
    )
