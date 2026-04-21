import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.user import User
from app.auth.security import hash_password
from app.auth.deps import get_current_user
from app.schemas.admin import AdminBootstrapIn, UserOut

router = APIRouter(prefix="/api/admin", tags=["admin"])

ADMIN_BOOTSTRAP_SECRET = os.getenv("ADMIN_BOOTSTRAP_SECRET", "").strip()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# -------------------------
# 1) Bootstrap admin
# -------------------------
@router.post("/bootstrap", response_model=UserOut)
async def bootstrap_admin(
    payload: AdminBootstrapIn,
    db: AsyncSession = Depends(get_db),
):
    if not ADMIN_BOOTSTRAP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_BOOTSTRAP_SECRET is not set"
        )

    if payload.secret.strip() != ADMIN_BOOTSTRAP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bad secret"
        )

    if not payload.email and not payload.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide email or phone"
        )

    if payload.email:
        existing_email = await db.scalar(
            select(User).where(User.email == payload.email)
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already used"
            )

    if payload.phone:
        existing_phone = await db.scalar(
            select(User).where(User.phone == payload.phone)
        )
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone already used"
            )

    user = User(
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role="admin",
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


# -------------------------
# 2) Current admin profile
# -------------------------
@router.get("/me", response_model=UserOut)
async def admin_me(admin: User = Depends(get_current_admin)):
    return admin


# -------------------------
# 3) Get all users
# -------------------------
@router.get("/users", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(User).order_by(User.id.desc()))
    return result.scalars().all()


# -------------------------
# 4) Get user by id
# -------------------------
@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# -------------------------
# 5) Delete user by id
# -------------------------
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await db.delete(user)
    await db.commit()

    return {"ok": True, "deleted_id": user_id}