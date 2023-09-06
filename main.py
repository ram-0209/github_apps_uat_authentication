from fastapi import FastAPI
from starlette.responses import RedirectResponse, JSONResponse
import httpx
from cachetools import TTLCache
import json

app = FastAPI()

CLIENT_ID = "449018d9e8d20ed29cb7"
CLIENT_SECRET = "69dcc54184a539e2647b84667ea1074ef670434d"


cache = TTLCache(maxsize=100, ttl=1800)


@app.get("/login")
async def github_login():
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo"
    )


@app.get("/github-code")
async def github_code(code: str):
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
    }
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url="https://github.com/login/oauth/access_token",
            params=params,
            headers=headers,
        )
    response_json = response.json()
    access_token = response_json["access_token"]
    cache["access_token"] = access_token
    return JSONResponse(
        content={"detail": response_json, "message": "Access Token is created"}
    )


@app.get("/get_token")
async def get_token():
    cache_token = cache.get("access_token")
    if cache_token:
        return {"token": cache_token}
    else:
        return {"message": "token not found"}


@app.get("/get_user")
async def get_user():
    cache_token = cache.get("access_token")
    async with httpx.AsyncClient() as client:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {cache_token}",
        }
        response = await client.get("https://api.github.com/user", headers=headers)
    response = response.json()


@app.get("/get_repo")
async def get_repo(user_name: str, repo_name: str):
    cache_token = cache.get("access_token")
    headers = {"Accept": "application/json", "Authorization": f"Bearer {cache_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{user_name}/{repo_name}", headers=headers
        )
    return response.json()


@app.get("/create_repo_using_template")
async def create_repo_using_template(user_name: str, repo_name: str):
    cache_token = cache.get("access_token")
    payload = {
        "owner": "ram-0209",
        "name": "Testing_repo_2",
        "description": "Created using template",
        "include_all_branches": False,
        "private": False,
    }
    headers = {"Accept": "application/json", "Authorization": f"Bearer {cache_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/ram-0209/Testing_repo/generate",
            headers=headers,
            data=json.dumps(payload),
        )
    return response.json()
