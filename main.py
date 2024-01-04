from dotenv import load_dotenv
from fastapi import FastAPI
from api.routers import loan, payment, product, root, user, auth, simulate_loan


app = FastAPI()
load_dotenv()

app.include_router(root.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(product.router)
app.include_router(loan.router)
app.include_router(simulate_loan.router)
app.include_router(payment.router)
