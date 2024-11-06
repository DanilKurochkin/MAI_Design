from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Модель данных для пользователя
class User(BaseModel):
    id: int
    username : str
    first_name: str
    last_name: str
    email: str
    hashed_password: str

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


# Временное хранилище для пользователей
users_db = []
folders_db = []
files_db = []

# Псевдо-база данных пользователей
admin_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # hashed "secret"
    }
}

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Создание и проверка JWT токенов
def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
)->str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Получение пользователя из псевдо-базы данных
def get_user_from_db(fake_db, username: str)->User:
    if username in fake_db:
        user_dict = fake_db[username]
        return User(**user_dict)


# Аутентификация пользователя
def authenticate_user(fake_db, username: str, password: str) -> User:
    user = get_user_from_db(fake_db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


# Зависимости для получения текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
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
    except JWTError:
        print('jwt error')
        raise credentials_exception
    user = get_user_from_db(admin_db, username=username)
    if user is None:
        raise credentials_exception
    return user


# Маршрут для получения токена
@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict:
    user = authenticate_user(admin_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Создать нового пользователя
@app.post("/users", response_model=User)
def create_user(
    user: User, current_user: User = Depends(get_current_user)
) -> User:
    for user_db in users_db:
        if user_db.id == user.id:
            raise HTTPException(status_code=404, detail="User already exist")
    users_db.append(user)
    return user


# Получение списка всех пользователей
@app.get("/users", response_model=List[User])
def get_users(
    current_user: User = Depends(get_current_user)
) -> List[User]:
    return users_db


# Поиск пользователя по логину
@app.get("/users/{username}", response_model=User)
def get_user_by_username(
    username: str, current_user: User = Depends(get_current_user)
) -> User:
    for user in users_db:
        if user.username == username:
            return user
    raise HTTPException(status_code=404, detail="User not found")


# Поиск пользователя по по маске имя+фамилия
@app.get("/users/", response_model=List[User])
def get_user_by_username(
    first_name: str, last_name: str,
    current_user: User = Depends(get_current_user)
) -> List[User]:
    matching_users = [
        user
        for user in users_db
        if first_name.lower() in user.first_name.lower() and
        last_name.lower() in user.last_name.lower()
    ]
    if len(matching_users) == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return matching_users


# Создание папки
@app.post("/folders", response_model=Folder)
def create_folder(
    folder: Folder, current_user: User = Depends(get_current_user)
) -> Folder:
    for folder_db in folders_db:
        if folder_db.id == folder.id:
            raise HTTPException(status_code=404, detail="Folder already exist")
    folders_db.append(folder)
    return folder


# Получение списка всех папок
@app.get("/folders", response_model=List[Folder])
def get_folders(current_user: User = Depends(get_current_user)) -> List[Folder]:
    return folders_db


# Создание файла в папке
@app.post("/folders/{folder_id}/", response_model=File)
def create_file_in_folder(
    file: File, folder_id: int, current_user: User = Depends(get_current_user)
) -> File:
    for iter_folder in folders_db:
        if iter_folder.id ==folder_id:
            folder: Folder = iter_folder
            break
    else:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if current_user.id != folder.creator_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    folder_files: List[File] = [
        folder_file
        for folder_file in files_db
        if folder_file.folder_id == folder.id
    ]
    if file.name in [folder_file.name for folder_file in folder_files]:
        raise HTTPException(status_code=405, detail="File with this name already exist")
    
    files_db.append(file)
    return file


# Получение файла по имени
@app.get("/folders/{folder_id}/{filename}", response_model=File)
def get_file_by_name(
    filename: str, folder_id: int, current_user: User = Depends(get_current_user)
) -> File:
    for iter_folder in folders_db:
        if iter_folder.id ==folder_id:
            folder: Folder = iter_folder
            break
    else:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if current_user.id != folder.creator_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    folder_files: List[File] = [
        folder_file
        for folder_file in files_db
        if folder_file.folder_id == folder.id
    ]
    
    for file in folder_files:
        if file.name == filename:
            return file
    else:
        raise HTTPException(status_code=404, detail="File not found")


# Удаление файла
@app.delete("/folders/{folder_id}/{filename}", response_model=File)
def delete_file_by_name(
    filename: str, folder_id: int, current_user: User = Depends(get_current_user)
) -> File:
    for iter_folder in folders_db:
        if iter_folder.id ==folder_id:
            folder: Folder = iter_folder
            break
    else:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if current_user.id != folder.creator_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    folder_files: List[File] = [
        folder_file
        for folder_file in files_db
        if folder_file.folder_id == folder.id
    ]
    
    for index, file in enumerate(folder_files):
        if file.name == filename:
            deleted_file = files_db.pop(index)
            return deleted_file
    else:
        raise HTTPException(status_code=404, detail="File not found")


# Удаление папки
@app.delete("/folders/{folder_id}", response_model=Folder)
def delete_folder(
    folder_id: int, current_user: User = Depends(get_current_user)
) -> Folder:
    for iter_folder in folders_db:
        if iter_folder.id ==folder_id:
            folder: Folder = iter_folder
            break
    else:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if current_user.id != folder.creator_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    global files_db
    
    files_db = [
        folder_file
        for folder_file in files_db
        if folder_file.folder_id != folder.id
    ]
    
    for index, folder_from_db in enumerate(folders_db):
        if folder_from_db == folder:
            deleted_folder = folders_db.pop(index)
            return deleted_folder


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)