from dotenv import load_dotenv
from fastapi import FastAPI
from api.endpoints import root, users, auth, products


app = FastAPI()
load_dotenv()

app.include_router(root.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
