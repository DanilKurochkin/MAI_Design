from pydantic import BaseModel

# Модель пользователя    
class User(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    hashed_password: str
    email: str
    
    class Config:
        from_attributes = True


# Модель данных для папок
class Folder(BaseModel):
    id: int
    name: str
    creator_id: int
    
    class Config:
        from_attributes = True


# Модель данных для файлов
class File(BaseModel):
    id: int
    name: str
    folder_id: int
    
    class Config:
        from_attributes = True