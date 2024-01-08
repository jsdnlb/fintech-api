from dotenv import load_dotenv
from fastapi import FastAPI
from api.routers import (
    credit_line,
    payment,
    product,
    root,
    simulate_credit_line,
    user,
    auth,
    balance,
)


app = FastAPI()
load_dotenv()

app.include_router(root.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(product.router)
app.include_router(credit_line.router)
app.include_router(simulate_credit_line.router)
app.include_router(payment.router)
app.include_router(balance.router)
