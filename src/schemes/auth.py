from sqlmodel import SQLModel


class TokenBase(SQLModel):
    access_token: str
    token_type: str = 'bearer'


class AccessTokenResponse(TokenBase):
    pass
