from fastapi import FastAPI
from starlette.responses import RedirectResponse
import httpx

app = FastAPI()

CLIENT_ID = "449018d9e8d20ed29cb7"
CLIENT_SECRET = "69dcc54184a539e2647b84667ea1074ef670434d"


@app.get("/login")
async def github_login():
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}"
    )


@app.get("/github-code")
async def github_code(code: str):
    params = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code}
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url="https://github.com/login/oauth/access_token",
            params=params,
            headers=headers,
        )
    response_json = response.json()
    print(response_json)
    access_token = response_json["access_token"]
    async with httpx.AsyncClient() as client:
        headers.update({"Authorization": f"Bearer {access_token}"})
        response = await client.get("https://api.github.com/user", headers=headers)
    return response.json()
