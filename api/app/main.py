from fastapi import FastAPI

from api.app.routes.health import router as health_router
from api.app.routes.customers import router as customers_router
from api.app.routes.analytics import router as analytics_router

app = FastAPI(
    title="RetailFlow API",
    version="1.0.0",
    description="RetailFlow e-commerce data platform API",
)

app.include_router(health_router)
app.include_router(customers_router)
app.include_router(analytics_router)
