"""Bakaláři API client — port z původního index.js.

Logika zachována beze změny:
- findWorkingEndpoint: zkouší prefixy, detekuje 400/401
- authenticateBakalari: POST /api/login s form-encoded tělem
- fetchMarks: GET /api/3/marks, filtruje podle last_check_date
- processMark: idempotentní, ignoruje duplikáty
"""
import httpx
from datetime import datetime
from typing import Optional

POSSIBLE_PREFIXES = ['', '/bakalari', '/bakaweb', '/webrodice', '/dm', '/mobile']


async def find_working_endpoint(base_url: str) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        for prefix in POSSIBLE_PREFIXES:
            test_url = f"{base_url}{prefix}/api/login"
            try:
                await client.post(test_url, data={
                    'client_id': 'ANDR', 'grant_type': 'password',
                    'username': 'test', 'password': 'test'
                })
            except httpx.RequestError:
                continue
            except Exception as e:
                # httpx raises on non-2xx too — kontrolujeme status
                pass
            # Pokud jsme dostali odpověď (i 400/401) → endpoint existuje
            try:
                r = await client.post(test_url, data={
                    'client_id': 'ANDR', 'grant_type': 'password',
                    'username': 'test', 'password': 'test'
                })
                if r.status_code in (400, 401):
                    return f"{base_url}{prefix}/api"
            except Exception:
                continue
    raise ValueError(f"Funkční Bakaláři API endpoint nenalezen na {base_url}")


async def authenticate(base_url: str, username: str, password: str) -> str:
    api_base = await find_working_endpoint(base_url)
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{api_base}/login", data={
            'client_id': 'ANDR', 'grant_type': 'password',
            'username': username, 'password': password
        })
        r.raise_for_status()
        token = r.json().get('access_token')
        if not token:
            raise ValueError("Bakaláři nevrátili access_token")
        return token, api_base


async def fetch_marks(base_url: str, username: str, password: str,
                      since: datetime) -> list[dict]:
    token, api_base = await authenticate(base_url, username, password)
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{api_base}/3/marks",
                             headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        data = r.json()

    marks = []
    subjects = data.get('Subjects') or data.get('Marks') or []
    for subject in subjects:
        subject_name = (subject.get('Caption') or subject.get('Name')
                        or subject.get('SubjectName') or 'Neznámý předmět')
        for mark in subject.get('Marks', []):
            mark_date = datetime.fromisoformat(
                (mark.get('Date') or mark.get('MarkDate', '')).replace('Z', '+00:00')
            )
            if mark_date > since and mark.get('MarkText'):
                marks.append({
                    'date': mark_date,
                    'value': mark['MarkText'].strip(),
                    'subject': subject_name,
                })
    return marks
