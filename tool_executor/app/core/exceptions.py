from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self, detail="Recurso no encontrado"):
        super().__init__(status_code=404, detail=detail)


class ToolExecutionException(HTTPException):
    def __init__(self, detail="Error al ejecutar la herramienta"):
        super().__init__(status_code=500, detail=detail)
