import os
import bcrypt
import streamlit as st
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("缺少 Supabase 配置")
        st.stop()
    return create_client(url, key)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(email: str, password: str) -> dict:
    sb = get_supabase()
    email = email.strip().lower()
    existing = sb.table("users").select("id").eq("email", email).execute()
    if existing.data:
        return {"ok": False, "msg": "该邮箱已注册，请直接登录"}
    if len(password) < 6:
        return {"ok": False, "msg": "密码至少需要6位"}
    trial_end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    sb.table("users").insert({
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "trial_end": trial_end,
        "is_paid": False,
    }).execute()
    return {"ok": True}

def login_user(email: str, password: str) -> dict:
    sb = get_supabase()
    email = email.strip().lower()
    res = sb.table("users").select("*").eq("email", email).execute()
    if not res.data:
        return {"ok": False, "msg": "邮箱或密码错误"}
    user = res.data[0]
    if not verify_password(password, user["password"]):
        return {"ok": False, "msg": "邮箱或密码错误"}
    return {"ok": True, "user": user}

def save_session(user: dict):
    st.session_state["user"] = user
    st.session_state["logged_in"] = True

def clear_session():
    st.session_state["user"] = None
    st.session_state["logged_in"] = False

def current_user():
    return st.session_state.get("user")

def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)

def get_user_status(user: dict) -> dict:
    is_paid = user.get("is_paid", False)
    trial_end_str = user.get("trial_end")
    now = datetime.now(timezone.utc)
    if trial_end_str:
        trial_end = datetime.fromisoformat(trial_end_str)
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        in_trial = now < trial_end
        days_left = max(0, (trial_end - now).days)
    else:
        in_trial = False
        days_left = 0
    if is_paid:
        access = "full"
    elif in_trial:
        access = "trial"
    else:
        access = "locked"
    return {"is_paid": is_paid, "in_trial": in_trial, "trial_days_left": days_left, "access": access}

def mark_user_paid(email: str) -> bool:
    sb = get_supabase()
    res = sb.table("users").update({"is_paid": True}).eq("email", email).execute()
    return bool(res.data)
