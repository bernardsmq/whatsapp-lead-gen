from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from auth import hash_password, verify_password, create_access_token, verify_token
from database import supabase
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "admin"  # admin or sales_guy

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    try:
        # Fetch user from Supabase
        response = supabase.table("users").select("*").eq("email", request.email).execute()

        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = response.data[0]

        # Verify password
        try:
            is_valid = verify_password(request.password, user["password_hash"])
        except Exception as pwd_error:
            print(f"Password verification error: {pwd_error}")
            raise HTTPException(status_code=500, detail=f"Password verification failed: {str(pwd_error)}")

        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create JWT token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user["id"]},
            expires_delta=access_token_expires
        )

        response_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["id"]
        }
        print(f"✓ Login successful for {request.email}: returning {response_data.keys()}")
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/register")
async def register(request: RegisterRequest):
    try:
        # Check if user already exists
        response = supabase.table("users").select("*").eq("email", request.email).execute()
        if response.data:
            raise HTTPException(status_code=400, detail="User already exists")

        # Hash password
        hashed_password = hash_password(request.password)

        # Insert user into Supabase
        new_user = {
            "email": request.email,
            "password_hash": hashed_password,
            "name": request.name,
            "role": request.role
        }

        response = supabase.table("users").insert(new_user).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create user")

        return {"message": "User created successfully", "user_id": response.data[0]["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user(user_id: str = Depends(verify_token)):
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify")
async def verify_token_endpoint(user_id: str = Depends(verify_token)):
    """Verify if current token is valid"""
    try:
        return {
            "valid": True,
            "user_id": user_id,
            "message": "Token is valid"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token is invalid")

@router.get("/init-admin")
async def init_admin():
    """Create or reset admin user for first-time setup"""
    try:
        # Check if admin exists
        response = supabase.table("users").select("*").eq("email", "admin@example.com").execute()

        new_hash = hash_password("password")

        if response.data:
            # Admin exists, just reset password
            supabase.table("users").update({
                "password_hash": new_hash
            }).eq("email", "admin@example.com").execute()
            return {"message": "Admin password reset to 'password'", "created": False}
        else:
            # Create admin user
            supabase.table("users").insert({
                "email": "admin@example.com",
                "password_hash": new_hash,
                "name": "Admin",
                "role": "admin"
            }).execute()
            return {"message": "Admin user created with password 'password'", "created": True}
    except Exception as e:
        print(f"Init admin error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reset-admin-password")
async def reset_admin_password():
    """Temporary endpoint to reset admin password to 'password'"""
    try:
        new_hash = hash_password("password")
        response = supabase.table("users").update({
            "password_hash": new_hash
        }).eq("email", "admin@example.com").execute()

        if response.data:
            return {"message": "Admin password reset to 'password'"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset password")
    except Exception as e:
        print(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
