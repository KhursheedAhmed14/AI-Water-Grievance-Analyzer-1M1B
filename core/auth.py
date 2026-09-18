"""
core/auth.py
Prototype session-based authentication helper supporting dual roles:
1. Citizen Role (Public water grievance submission & status tracking)
2. Municipal Team Role (Protected municipal triage, review, priority, & assignment)
"""

import os
import streamlit as st
from core.database import authenticate_user, create_user, get_user_by_username
from core.ui_icons import get_icon_svg


from datetime import datetime, timedelta
import secrets

# Server-side active session store mapping opaque_token -> session_dict
_ACTIVE_SERVER_SESSIONS: dict[str, dict] = {}


def _create_server_session(user_id: int, user_name: str, user_role: str) -> str:
    """Generate a cryptographically secure token and store session server-side."""
    token = secrets.token_urlsafe(32)
    _ACTIVE_SERVER_SESSIONS[token] = {
        "user_id": user_id,
        "user_name": user_name,
        "user_role": user_role,
        "expires_at": datetime.utcnow() + timedelta(hours=12),
    }
    return token


def _validate_server_session(token: str) -> dict | None:
    """Validate server-side token; return session dict if valid and unexpired."""
    if not token or not isinstance(token, str):
        return None
    session_data = _ACTIVE_SERVER_SESSIONS.get(token)
    if not session_data:
        return None
    if session_data.get("expires_at", datetime.min) < datetime.utcnow():
        _ACTIVE_SERVER_SESSIONS.pop(token, None)
        return None
    return session_data


def get_current_role() -> str | None:
    """Return active session role derived from authenticated session state or validated server token."""
    role = st.session_state.get("user_role", None)
    if role in ("citizen", "municipal"):
        return role

    # Validate opaque session token from URL query params (never trust raw role/user_id from URL)
    token = st.query_params.get("session")
    if token:
        session_data = _validate_server_session(token)
        if session_data:
            role = session_data["user_role"]
            st.session_state["user_role"] = role
            st.session_state["user_name"] = session_data["user_name"]
            st.session_state["user_id"] = session_data["user_id"]
            st.session_state["session_token"] = token
            return role

    # Purge unauthenticated or legacy query parameters if invalid
    if any(k in st.query_params for k in ("role", "user", "uid")):
        st.query_params.clear()

    return None


def get_current_user_id() -> int | None:
    """Return the integer user_id of the active session user from SQLite."""
    get_current_role()  # Ensure session role restoration from validated server token if needed
    return st.session_state.get("user_id", None)


def is_citizen_authenticated() -> bool:
    """Return True if an active Citizen session is present."""
    return get_current_role() == "citizen"


def is_municipal_authenticated() -> bool:
    """Return True if an active Municipal Officer session is present."""
    return get_current_role() == "municipal"


def get_authenticated_user() -> str | None:
    """Return the display username/email of the active session user."""
    get_current_role()  # Ensure session role restoration from validated server token if needed
    return st.session_state.get("user_name", None)


def login_citizen(user_or_email: str, password: str) -> tuple[bool, str]:
    """
    Authenticate citizen user against SQLite users table.
    Issues a server-side session token on successful authentication.
    """
    u_clean = user_or_email.strip().lower()
    p_clean = password.strip()

    if not u_clean or not p_clean:
        return False, "Please enter both username/email and password."

    user = authenticate_user(u_clean, p_clean)
    if user:
        if user["role"] != "citizen":
            return False, "This account is registered for Municipal Officer access."
        token = _create_server_session(user["id"], user["username"], "citizen")
        st.session_state["user_role"] = "citizen"
        st.session_state["user_name"] = user["username"]
        st.session_state["user_id"] = user["id"]
        st.session_state["session_token"] = token
        st.query_params.clear()
        st.query_params["session"] = token
        return True, f"Welcome back, {user['username']}!"

    # Check if account exists with wrong password
    existing = get_user_by_username(u_clean)
    if existing:
        return False, "Invalid password for this citizen account."

    # Auto-register new citizen user in SQLite if non-existent for seamless testing
    success, msg, new_id = create_user(u_clean, p_clean, role="citizen", full_name="Citizen User")
    if success:
        token = _create_server_session(new_id, u_clean, "citizen")
        st.session_state["user_role"] = "citizen"
        st.session_state["user_name"] = u_clean
        st.session_state["user_id"] = new_id
        st.session_state["session_token"] = token
        st.query_params.clear()
        st.query_params["session"] = token
        return True, f"Citizen account created! Welcome, {u_clean}."

    return False, msg


def login_municipal(username: str, password: str) -> tuple[bool, str]:
    """
    Authenticate municipal officer against SQLite users table.
    Issues a server-side session token on successful authentication.
    """
    u_clean = username.strip().lower()
    p_clean = password.strip()

    if not u_clean or not p_clean:
        return False, "Please enter both officer ID/username and password."

    user = authenticate_user(u_clean, p_clean, required_role="municipal")
    if user:
        token = _create_server_session(user["id"], user["username"], "municipal")
        st.session_state["user_role"] = "municipal"
        st.session_state["user_name"] = user["username"]
        st.session_state["user_id"] = user["id"]
        st.session_state["session_token"] = token
        st.query_params.clear()
        st.query_params["session"] = token
        return True, "Login successful."

    return False, "Invalid credentials. Demo Officer Login: officer / water2026"


def register_citizen(username: str, password: str, full_name: str = "") -> tuple[bool, str]:
    """Register a new citizen in SQLite users table."""
    success, msg, new_id = create_user(username, password, role="citizen", full_name=full_name)
    if success:
        u_clean = username.strip().lower()
        token = _create_server_session(new_id, u_clean, "citizen")
        st.session_state["user_role"] = "citizen"
        st.session_state["user_name"] = u_clean
        st.session_state["user_id"] = new_id
        st.session_state["session_token"] = token
        st.query_params.clear()
        st.query_params["session"] = token
    return success, msg


def logout() -> None:
    """Revoke server-side session token and clear active session state."""
    token = st.session_state.get("session_token") or st.query_params.get("session")
    if token:
        _ACTIVE_SERVER_SESSIONS.pop(token, None)

    st.session_state.pop("user_role", None)
    st.session_state.pop("user_name", None)
    st.session_state.pop("user_id", None)
    st.session_state.pop("session_token", None)
    st.session_state.pop("municipal_authenticated", None)
    st.session_state.pop("municipal_user", None)
    st.query_params.clear()


# Backward compatibility aliases
def logout_user() -> None:
    logout()


def is_authenticated() -> bool:
    return is_municipal_authenticated()


def render_citizen_login_form() -> None:
    """Render prototype login & registration tabs for citizens."""
    icon_accent = "#38bdf8"

    st.markdown(
        f"""
        <div class="content-card" style="max-width: 520px; margin: 1rem auto; padding: 2rem;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
                <div class="card-icon-box">{get_icon_svg("user", color=icon_accent, size=20)}</div>
                <h2 style="margin: 0; font-size: 1.3rem;">Citizen Login Portal</h2>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1.2rem;">
                Sign in to submit water complaints and track resolution status in real-time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_signin, tab_signup = st.tabs(["Sign In", "Register Citizen Account"])

    with tab_signin:
        with st.form("citizen_signin_form", clear_on_submit=False):
            u_input = st.text_input("Username or Email", placeholder="citizen@example.com")
            p_input = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Continue as Citizen", type="primary", use_container_width=True)

            if submitted:
                success, msg = login_citizen(u_input, p_input)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_signup:
        with st.form("citizen_signup_form", clear_on_submit=False):
            reg_name = st.text_input("Full Name", placeholder="Jane Resident")
            reg_email = st.text_input("Email Address", placeholder="citizen@example.com")
            reg_pass = st.text_input("Create Password", type="password", placeholder="••••••••")
            reg_submit = st.form_submit_button("Create Account & Sign In", type="primary", use_container_width=True)

            if reg_submit:
                success, msg = register_citizen(reg_email, reg_pass, full_name=reg_name)
                if success:
                    st.success(f"Account created for {reg_email}! Redirecting...")
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown(
        """
        <div style="max-width: 520px; margin: 0.8rem auto; font-size: 0.82rem; color: var(--text-muted); background: var(--bg-card-subtle); padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid var(--border-color);">
            <strong>Demo Citizen Login:</strong><br>
            • Email: <code>citizen@example.com</code> | Password: <code>citizen123</code><br>
            • Or register a new account or enter any email/password.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_municipal_login_form() -> None:
    """Render prototype login form for authorized municipal officers."""
    icon_accent = "#38bdf8"

    st.markdown(
        f"""
        <div class="content-card" style="max-width: 520px; margin: 1rem auto; padding: 2rem;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
                <div class="card-icon-box">{get_icon_svg("lock", color=icon_accent, size=20)}</div>
                <h2 style="margin: 0; font-size: 1.3rem;">Municipal Team Login</h2>
            </div>
            <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1.2rem;">
                Sign in to access municipal grievance queues, human review, and dispatch operations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("municipal_login_form", clear_on_submit=False):
        user_input = st.text_input(
            "Municipal Officer ID / Username",
            placeholder="officer",
            help="Demo username: officer",
        )
        pass_input = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••",
            help="Demo password: water2026",
        )

        st.caption("Authorized Municipal Personnel Only — Prototype Role Separation")

        submitted = st.form_submit_button(
            "Sign In as Municipal Officer",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            success, msg = login_municipal(user_input, pass_input)
            if success:
                st.success(f"Authenticated as Municipal Officer {get_authenticated_user()}. Redirecting...")
                st.rerun()
            else:
                st.error(msg)

    st.markdown(
        """
        <div style="max-width: 520px; margin: 0.8rem auto; font-size: 0.82rem; color: var(--text-muted); background: var(--bg-card-subtle); padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid var(--border-color);">
            <strong>Demo Municipal Credentials:</strong><br>
            • Officer Username: <code>officer</code> | Password: <code>water2026</code><br>
            • Admin Username: <code>admin</code> | Password: <code>admin123</code>
        </div>
        """,
        unsafe_allow_html=True,
    )


def require_role(required_role: str) -> None:
    """
    Page guard enforcing role-based access control.
    Stops page execution if caller does not possess the required session role.
    """
    current = get_current_role()
    if current != required_role:
        role_title = "Municipal Team" if required_role == "municipal" else "Citizen"
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 1.2rem 1.4rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 14px;">
                {get_icon_svg("lock", color="#f87171", size=24)}
                <div>
                    <h4 style="margin: 0; color: #f87171 !important; font-size: 1.05rem;">Access Restricted — {role_title} Session Required</h4>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.88rem; color: var(--text-secondary);">
                        This page is part of the protected <strong>{role_title} Portal</strong>. Please sign in below to continue.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if required_role == "municipal":
            render_municipal_login_form()
        else:
            render_citizen_login_form()

        st.stop()


# Backward compatibility guard alias
def require_municipal_auth() -> None:
    require_role("municipal")
