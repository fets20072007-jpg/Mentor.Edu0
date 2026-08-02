from fastapi import APIRouter

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.get("/")
def chat():
    return {
        "mensagem": "Chat funcionando"
    }
    