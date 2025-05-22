from sqlmodel import SQLModel


class TokenBase(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TokenResponse(TokenBase):
    pass
