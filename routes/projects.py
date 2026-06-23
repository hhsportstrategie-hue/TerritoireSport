from fastapi import APIRouter, HTTPException
from models.project import ClubProjectCreate, ClubProjectUpdate, ClubProjectOut
import uuid, json
from pathlib import Path

router = APIRouter(prefix="/api/projects", tags=["projects"])

def load_library():
    path = Path("data/projects_library.json")
    return json.loads(path.read_text(encoding="utf-8"))

@router.get("/library")
async def get_library(theme: str = None):
    projects = load_library()
    if theme:
        projects = [p for p in projects if p["theme"] == theme]
    return projects

@router.get("/library/{project_id}")
async def get_project(project_id: str):
    projects = load_library()
    p = next((p for p in projects if p["id"] == project_id), None)
    if not p:
        raise HTTPException(404, "Projet non trouvé")
    return p

@router.post("/club", response_model=ClubProjectOut, status_code=201)
async def add_club_project(data: ClubProjectCreate):
    import aiosqlite
    # Vérifier que le projet existe dans la bibliothèque
    projects = load_library()
    if not any(p["id"] == data.project_id for p in projects):
        raise HTTPException(404, "Projet non trouvé dans la bibliothèque")
    cp_id = str(uuid.uuid4())
    async with aiosqlite.connect("territoiresport.db") as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            "INSERT INTO club_projects (id, club_id, project_id, notes, started_at) VALUES (?,?,?,?,datetime('now'))",
            (cp_id, data.club_id, data.project_id, data.notes)
        )
        await db.commit()
        async with db.execute("SELECT * FROM club_projects WHERE id = ?", (cp_id,)) as cur:
            return dict(await cur.fetchone())

@router.get("/club/{club_id}")
async def get_club_projects(club_id: str):
    import aiosqlite
    library = {p["id"]: p for p in load_library()}
    async with aiosqlite.connect("territoiresport.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM club_projects WHERE club_id = ? ORDER BY updated_at DESC",
            (club_id,)
        ) as cur:
            rows = await cur.fetchall()
            result = []
            for row in rows:
                d = dict(row)
                d["project_details"] = library.get(d["project_id"], {})
                result.append(d)
            return result

@router.patch("/club/{cp_id}", response_model=ClubProjectOut)
async def update_club_project(cp_id: str, data: ClubProjectUpdate):
    import aiosqlite
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "Aucun champ")
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [cp_id]
    async with aiosqlite.connect("territoiresport.db") as db:
        db.row_factory = aiosqlite.Row
        await db.execute(f"UPDATE club_projects SET {set_clause}, updated_at = datetime('now') WHERE id = ?", values)
        await db.commit()
        async with db.execute("SELECT * FROM club_projects WHERE id = ?", (cp_id,)) as cur:
            return dict(await cur.fetchone())
