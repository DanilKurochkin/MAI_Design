from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel

import models as md

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(BaseModel):
    id: int
    username : str
    first_name: str
    last_name: str
    email: str
    password: str

# Модель данных для папок
class Folder(BaseModel):
    id: int
    name: str
    creator_id: int

# Модель данных для файлов
class File(BaseModel):
    id: int
    name: str
    folder_id: int


app = FastAPI()
# Создание сессии
engine = create_engine("postgresql+psycopg2://postgres:postgres@db/archdb")
Session = sessionmaker(bind=engine)
session = Session()
# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(session : sessionmaker, username:str) -> md.User:
    return session.query(md.User).filter(md.User.username == username).first()

# Зависимости для получения текущего пользователя
async def get_current_client(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


# Создание и проверка JWT токенов
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Маршрут для получения токена
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    password_check = False
    user = get_user(session, form_data.username)
    if user:
        password = form_data.password
        #print(f"\n{pwd_context.hash(password)}\n{user.password}")
        if pwd_context.verify(password, user.password):
            password_check = True

    if password_check:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        print(user.password)
        raise HTTPException(
            
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Создать нового пользователя
@app.post("/users", response_model=User)
def create_user(
    user: User, current_user: str = Depends(get_current_client)
) -> User:
    user_to_db = md.User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=user.password
    )
    session.add(user_to_db)
    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=404, detail="Failed to create user")
    
    return user

# Получение списка всех пользователей
@app.get("/users", response_model=List[User])
def get_users(
    current_user: str = Depends(get_current_client)
) -> List[User]:
    return session.query(md.User).all()


# Поиск пользователя по логину
@app.get("/users/{username}", response_model=User)
def get_user_by_username(
    username: str, current_user: str = Depends(get_current_client)
) -> User:
    user = session.query(md.User).filter(md.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Поиск пользователя по по маске имя+фамилия
@app.get("/users/", response_model=List[User])
def get_user_by_username(
    first_name: str, last_name: str,
    current_user: str = Depends(get_current_client)
) -> List[User]:
    user = (
        session.query(md.User)
        .filter(md.User.first_name == first_name)
        .filter(md.User.last_name == last_name)
        .all()
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Создание папки
@app.post("/folders", response_model=Folder)
def create_folder(
    folder: Folder, current_user: str = Depends(get_current_client)
) -> Folder:
    folder_to_db = md.Folder(
        name=folder.name,
        creator_id=folder.creator_id
    )
    session.add(folder_to_db)
    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=404, detail="Failed to create folder")
    
    return folder


# Получение списка всех папок
@app.get("/folders", response_model=List[Folder])
def get_folders(current_user: str = Depends(get_current_client)) -> List[Folder]:
    return session.query(md.Folder).all()


# Создание файла в папке
@app.post("/folders/{folder_id}/", response_model=File)
def create_file_in_folder(
    file: File, folder_id: int, current_user: str = Depends(get_current_client)
) -> File:
    file_to_db = md.File(
        name=file.name,
        folder_id=folder_id
    )
    session.add(file_to_db)
    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=404, detail="Failed to create file")
    
    return file
    

# Получение файла по имени
@app.get("/folders/{folder_id}/{filename}", response_model=File)
def get_file_by_name(
    filename: str, folder_id: int, current_user: str = Depends(get_current_client)
) -> File:
    files = session.query(md.File).filter(md.File.folder_id == folder_id).all()
    if len(files) == 0:
        raise HTTPException(status_code=404, detail="Folder is empty or dont exist")
    
    for file in files:
        if file.name == filename:
            return file
    else:
        raise HTTPException(status_code=404, detail="File dont exist")
    

# Удаление файла
@app.delete("/folders/{folder_id}/{filename}", response_model=File)
def delete_file_by_name(
    filename: str, folder_id: int, current_user: str = Depends(get_current_client)
) -> File:
    file_to_delete = (
        session.query(md.File)
        .filter(md.File.name == filename, md.File.folder_id == folder_id)
        .first()
    )
    if file_to_delete is None:
        raise HTTPException(status_code=404, detail="File not found in the folder")

    session.delete(file_to_delete)
    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=404, detail="Failed to delete file")

    return file_to_delete


# Удаление папки
@app.delete("/folders/{folder_id}", response_model=Folder)
def delete_folder(
    folder_id: int, current_user: str = Depends(get_current_client)
) -> Folder:
    folder = session.query(md.Folder).filter(md.Folder.id == folder_id).first()
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")

    session.delete(folder)
    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=404, detail="Failed to delete folder")

    return folder


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)