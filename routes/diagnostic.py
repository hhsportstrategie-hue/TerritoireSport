from fastapi import APIRouter, HTTPException
from db_config import DB_PATH
from models.diagnostic import DiagnosticSubmit, DiagnosticOut, DIAGNOSTIC_QUESTIONS, PROFILES, compute_profile
import uuid, json

router = APIRouter(prefix="/api/diagnostic", tags=["diagnostic"])

@router.get("/questions")
async def get_questions():
    return DIAGNOSTIC_QUESTIONS

@router.post("/submit", response_model=DiagnosticOut, status_code=201)
async def submit_diagnostic(data: DiagnosticSubmit):
    import aiosqlite
    # Calculer le score (0-2 par question, max 20)
    score = sum(data.answers.get(q["id"], 0) for q in DIAGNOSTIC_QUESTIONS)
    profile = compute_profile(score)
    profile_data = PROFILES[profile]
    diag_id = str(uuid.uuid4())
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            "INSERT INTO diagnostics (id, club_id, answers, score, profile) VALUES (?,?,?,?,?)",
            (diag_id, data.club_id, json.dumps(data.answers), score, profile)
        )
        await db.commit()
        async with db.execute("SELECT * FROM diagnostics WHERE id = ?", (diag_id,)) as cur:
            row = dict(await cur.fetchone())
            return {
                **row,
                "profile_label": profile_data["label"],
                "profile_desc":  profile_data["description"],
                "answers":       data.answers,
            }

@router.get("/latest/{club_id}")
async def get_latest_diagnostic(club_id: str):
    import aiosqlite
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM diagnostics WHERE club_id = ? ORDER BY completed_at DESC LIMIT 1",
            (club_id,)
        ) as cur:
            row = await cur.fetchone()
            if not row:
                raise HTTPException(404, "Aucun diagnostic trouvé")
            d = dict(row)
            profile = PROFILES[d["profile"]]
            d["profile_label"] = profile["label"]
            d["profile_desc"]  = profile["description"]
            d["answers"] = json.loads(d["answers"])
            return d
