from fastapi import APIRouter, HTTPException, Depends
from models.club import ClubCreate, ClubUpdate, ClubOut, ClubLogin
from typing import List
import hashlib, uuid, json

router = APIRouter(prefix="/api/clubs", tags=["clubs"])

def get_db():
    import aiosqlite
    return aiosqlite

def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

@router.post("/register", response_model=ClubOut, status_code=201)
async def register_club(data: ClubCreate):
    import aiosqlite
    async with aiosqlite.connect("territoiresport.db") as db:
        db.row_factory = aiosqlite.Row
        # Vérifier email unique
        async with db.execute("SELECT id FROM clubs WHERE email = ?", (data.email,)) as cur:
            if await cur.fetchone():
                raise HTTPException(400, "Email déjà utilisé")
        club_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO clubs (id,name,email,password_hash,sport,city,department,region,size,members_count,description,website) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (club_id, data.name, data.email, hash_password(data.password),
             data.sport, data.city, data.department, data.region,
             data.size.value, data.members_count, data.description, data.website)
        )
        await db.commit()
        async with db.execute("SELECT * FROM clubs WHERE id = ?", (club_id,)) as cur:
            row = await cur.fetchone()
            return dict(row)

@router.post("/login")
async def login(data: ClubLogin):
    import aiosqlite
    async with aiosqlite.connect("territoiresport.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM clubs WHERE email = ? AND password_hash = ?",
            (data.email, hash_password(data.password))
        ) as cur:
            row = await cur.fetchone()
            if not row:
                raise HTTPException(401, "Email ou mot de passe incorrect")
            club = dict(row)
            club.pop("password_hash", None)
            return {"token": club["id"], "club": club}  # token simplifié (UUID = session token)

@router.get("/{club_id}", response_model=ClubOut)
async def get_club(club_id: str):
    import aiosqlite
    async with aiosqlite.connect("territoiresport.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM clubs WHERE id = ?", (club_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                raise HTTPException(404, "Club non trouvé")
            return dict(row)

@router.patch("/{club_id}", response_model=ClubOut)
async def update_club(club_id: str, data: ClubUpdate):
    import aiosqlite
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "Aucun champ à mettre à jour")
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [club_id]
    async with aiosqlite.connect("territoiresport.db") as db:
        db.row_factory = aiosqlite.Row
        await db.execute(f"UPDATE clubs SET {set_clause}, updated_at = datetime('now') WHERE id = ?", values)
        await db.commit()
        async with db.execute("SELECT * FROM clubs WHERE id = ?", (club_id,)) as cur:
            return dict(await cur.fetchone())
