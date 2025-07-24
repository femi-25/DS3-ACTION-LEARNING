from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
security = HTTPBearer()

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = security):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")

        if email is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        request.state.user = {"email": email, "role": role}
        return request.state.user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def role_required(allowed_roles: list):
    async def wrapper(request: Request, credentials: HTTPAuthorizationCredentials = security):
        user = await get_current_user(request, credentials)
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return user
    return wrapper
