from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.services.trabalhista import Trabalhista
from app.utils.dependencies import get_tools
from app.schemas import BaseCndRequest

router = APIRouter(prefix="/trabalhista")


@router.post("")
async def trabalhista(data: BaseCndRequest, tools=Depends(get_tools)):
    page, context = tools
    pdf_bytes = await Trabalhista.execute_scrap(page=page, context=context, cnpj=data.cnpj)
    return Response(content=pdf_bytes, media_type="application/pdf")
