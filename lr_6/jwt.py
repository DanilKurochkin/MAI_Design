import json
import threading

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import redis

from kafka_cons import get_kafka_producer, kafka_consumer_service
import models.alchemy_models as md
import models.pydantic_models as pdmd

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@db/archdb"
MONGO_URI = "mongodb://root:pass@mongo:27017/"
REDIS_URL = "redis://redis:6379"
KAFKA_BROKER = "kafka:9092"

# Создание приложения
app = FastAPI()
# Создание сессии
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Подключение к MongoDB
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["disk"]
mongo_users_collection = mongo_db["users"]
# Подключение к Redis
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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


# зависимость для получения сессии
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    user = mongo_users_collection.find_one({"username": form_data.username})
    if user and pwd_context.verify(form_data.password, user["hashed_password"]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Создание нового пользователя
@app.post("/users", response_model=pdmd.User)
def create_user(user: pdmd.User, current_user: str = Depends(get_current_client)):
    user_dict = user.dict()
    user_dict["hashed_password"] = pwd_context.hash(user_dict["hashed_password"])
    user_id = mongo_users_collection.insert_one(user_dict).inserted_id
    user_dict["id"] = str(user_id)
    return user_dict


# Поиск пользователя по логину
@app.get("/users/{username}", response_model=pdmd.User)
def get_user_by_username(username: str, current_user: str = Depends(get_current_client)):
    user = mongo_users_collection.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")


# Поиск пользователя по маске имени и фамилии
@app.get("/users", response_model=List[pdmd.User])
def search_users_by_name(
    first_name: str, last_name: str, current_user: str = Depends(get_current_client)
):
    users = list(
        mongo_users_collection
        .find(
            {
                "first_name": {"$regex": first_name, "$options": "i"},
                "last_name": {"$regex": last_name, "$options": "i"}
            }
        )
    )
    for user in users:
        user["id"] = str(user["_id"])
    return users


# Создание папки
@app.post("/folders", response_model=pdmd.Folder)
def create_folder(
    folder: pdmd.Folder,
    current_user: str = Depends(get_current_client),
    session: Session = Depends(get_session)
) -> pdmd.Folder:
    folder_to_db = md.Folder(**folder.dict())
    session.add(folder_to_db)    
    session.commit()
    session.refresh(folder_to_db)
    return folder


# Получение списка всех папок
@app.get("/folders", response_model=List[pdmd.Folder])
def get_folders(
    current_user: str = Depends(get_current_client),
    session: Session = Depends(get_session)
) -> List[pdmd.Folder]:
    folders = session.query(md.Folder).all()
    return folders


# Создание файла в папке
@app.post("/folders/{folder_id}/", response_model=pdmd.File)
def create_file_in_folder(
    file: pdmd.File, folder_id: int,
    current_user: str = Depends(get_current_client),
    producer: Session = Depends(get_kafka_producer)
) -> pdmd.File:
    producer.produce("created_file", key=str(file.id), value=json.dumps(file.dict()).encode("utf-8"))
    producer.flush()
    return file
    

# Получение файла по имени
@app.get("/folders/{folder_id}/{filename}", response_model=pdmd.File)
def get_file_by_name(
    filename: str, folder_id: int,
    current_user: str = Depends(get_current_client),
    session: Session = Depends(get_session)
) -> pdmd.File:
    cache_key = f"folder:{folder_id}:file:{filename}"
    cached_file = redis_client.get(cache_key)
    
    if cached_file:
        return cached_file
    
    files = session.query(md.File).filter(md.File.folder_id == folder_id).all()
    
    if len(files) == 0:
        raise HTTPException(status_code=404, detail="Folder is empty or dont exist")
    
    for file in files:
        if file.name == filename:
            redis_client.set(cache_key, json.dumps(pdmd.File.from_orm(file).dict()))
            return file
    else:
        raise HTTPException(status_code=404, detail="File dont exist")
    

# Удаление файла
@app.delete("/folders/{folder_id}/{filename}", response_model=pdmd.File)
def delete_file_by_name(
    filename: str, folder_id: int,
    current_user: str = Depends(get_current_client),
    session: Session = Depends(get_session)
) -> pdmd.File:
    cache_key = f"folder:{folder_id}:file:{filename}"
    cached_file = redis_client.get(cache_key)
    if cached_file:
        redis_client.delete(cache_key)
    
    file_to_delete = (
        session.query(md.File)
        .filter(md.File.name == filename, md.File.folder_id == folder_id)
        .first()
    )
    if file_to_delete is None:
        raise HTTPException(status_code=404, detail="File not found in the folder")

    session.delete(file_to_delete)
    return file_to_delete


# Удаление папки
@app.delete("/folders/{folder_id}", response_model=pdmd.Folder)
def delete_folder(
    folder_id: int,
    current_user: str = Depends(get_current_client),
    session: Session = Depends(get_session)
) -> pdmd.Folder:
    folder = session.query(md.Folder).filter(md.Folder.id == folder_id).first()
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")

    session.delete(folder)
    return folder


def start_kafka_consumer():
    thread = threading.Thread(target=kafka_consumer_service, daemon=True)
    thread.start()


start_kafka_consumer()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)