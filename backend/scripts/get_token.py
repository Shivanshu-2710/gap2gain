"""Print an access token for the demo user, for testing in /docs.  Run: python -m scripts.get_token"""
from supabase import create_client
from app.config import get_settings

s = get_settings()
client = create_client(s.supabase_url, s.supabase_service_role_key)  # separate client, only used here
res = client.auth.sign_in_with_password({"email": s.demo_email, "password": s.demo_password})
print(res.session.access_token)