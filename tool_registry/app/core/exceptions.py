from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self, detail="Recurso no encontrado"):
        super().__init__(status_code=404, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail="Recurso ya existe"):
        super().__init__(status_code=409, detail=detail)
