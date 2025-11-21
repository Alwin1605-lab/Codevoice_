from fastapi import APIRouter, Form, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import json
import hashlib
import time

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"users": []}, f)


def load_users():
    ensure_storage()
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class ProfileUpdate(BaseModel):
    name: str | None = None
    disability: str | None = None
    canType: bool | None = None
    preferredInputMethod: str | None = None
    typingSpeed: str | None = None
    additionalNeeds: str | None = None
    programmingExperience: str | None = None
    preferredLanguages: list[str] | None = None
    assistiveTechnologies: dict | None = None


@router.post('/auth/register')
async def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    data = load_users()
    users = data.get('users', [])
    if any(u.get('email') == email for u in users):
        raise HTTPException(status_code=400, detail='User already exists')
    user_id = str(int(time.time() * 1000))
    user = {
        'id': user_id,
        'name': name,
        'email': email,
        'password': hash_password(password),
        # default profile fields
        'disability': '',
        'canType': False,
        'preferredInputMethod': '',
        'typingSpeed': '',
        'additionalNeeds': '',
        'programmingExperience': '',
        'preferredLanguages': [],
        'assistiveTechnologies': {
            'screenReader': False,
            'voiceControl': False,
            'switchControl': False,
            'other': ''
        }
    }
    users.append(user)
    data['users'] = users
    save_users(data)
    user_public = {k: v for k, v in user.items() if k != 'password'}
    return JSONResponse(user_public)


@router.post('/auth/login')
async def login(email: str = Form(...), password: str = Form(...)):
    data = load_users()
    users = data.get('users', [])
    pwd_hash = hash_password(password)
    for u in users:
        if u.get('email') == email and u.get('password') == pwd_hash:
            user_public = {k: v for k, v in u.items() if k != 'password'}
            return JSONResponse(user_public)
    raise HTTPException(status_code=401, detail='Invalid credentials')


@router.get('/users/{user_id}')
async def get_user(user_id: str):
    data = load_users()
    users = data.get('users', [])
    for u in users:
        if u.get('id') == user_id:
            return JSONResponse({k: v for k, v in u.items() if k != 'password'})
    raise HTTPException(status_code=404, detail='User not found')


@router.put('/users/{user_id}')
async def update_user(user_id: str, profile: ProfileUpdate = Body(...)):
    data = load_users()
    users = data.get('users', [])
    for idx, u in enumerate(users):
        if u.get('id') == user_id:
            updated = u.copy()
            for k, v in profile.dict(exclude_none=True).items():
                updated[k] = v
            users[idx] = updated
            data['users'] = users
            save_users(data)
            return JSONResponse({k: v for k, v in updated.items() if k != 'password'})
    raise HTTPException(status_code=404, detail='User not found')
