from ninja import NinjaAPI
from society.api import router as society_router

api = NinjaAPI(title="Somtam Society API")

api.add_router("", society_router)
