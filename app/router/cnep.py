from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.services.cnep import Cnep
from app.utils.dependencies import get_tools
from app.schemas import BaseCndRequest

router = APIRouter(prefix="/cnep")


@router.post("")
async def cnep(data: BaseCndRequest, tools=Depends(get_tools)):
    page, context = tools
    pdf_bytes = await Cnep.execute_scrap(page=page, context=context, cnpj=data.cnpj)
    return Response(content=pdf_bytes, media_type="application/pdf")
