import time
from pymongo import MongoClient
from passlib.context import CryptContext

# Настройка MongoDB
MONGO_URI = "mongodb://root:pass@mongo:27017/"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["disk"]
mongo_users_collection = mongo_db["users"]

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Проверка существования пользователя перед добавлением
def add_user(id, username, first_name, last_name, email, hashed_password):
    user = mongo_users_collection.find_one({"username": username})
    if not user:
        user = {
            "_id": id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "hashed_password": hashed_password,
        }
        mongo_users_collection.insert_one(user)
    else:
        print('user_exist')


users_to_add = [
    ["0" ,'admin', 'admin', 'admin', 'admin@example.com', 'secret'],
    ["1" ,'user1', 'John', 'Doe', 'john.doe@example.com', 'strong_password'],
    ["2" ,'user2', 'Jane', 'Smith', 'jane.smith@example.com', 'strong_password'],
    ["3" ,'user3', 'Alice', 'Johnson', 'alice.johnson@example.com', 'strong_password'],
    ["4" ,'user4', 'Bob', 'Brown', 'bob.brown@example.com', 'strong_password'],
    ["5" ,'user5', 'Charlie', 'Williams', 'charlie.williams@example.com', 'strong_password'],
    ["6" ,'user6', 'David', 'Jones', 'david.jones@example.com', 'strong_password'],
    ["7" ,'user7', 'Eve', 'Miller', 'eve.miller@example.com', 'strong_password'],
    ["8" ,'user8', 'Frank', 'Taylor', 'frank.taylor@example.com', 'strong_password'],
    ["9" ,'user9', 'Grace', 'Anderson', 'grace.anderson@example.com', 'strong_password'],
    ["10" ,'user10', 'Henry', 'Thomas', 'henry.thomas@example.com', 'strong_password'],
    ["11" ,'user11', 'Ivy', 'Jackson', 'ivy.jackson@example.com', 'strong_password'],
    ["12" ,'user12', 'Jack', 'White', 'jack.white@example.com', 'strong_password'],
    ["13" ,'user13', 'Kelly', 'Harris', 'kelly.harris@example.com', 'strong_password'],
    ["14" ,'user14', 'Leo', 'Martin', 'leo.martin@example.com', 'strong_password'],
    ["15" ,'user15', 'Megan', 'Clark', 'megan.clark@example.com', 'strong_password'],
    ["16" ,'user16', 'Nina', 'Rodriguez', 'nina.rodriguez@example.com', 'strong_password'],
    ["17" ,'user17', 'Oscar', 'Martinez', 'oscar.martinez@example.com', 'strong_password'],
    ["18" ,'user18', 'Paul', 'Davis', 'paul.davis@example.com', 'strong_password'],
    ["19" ,'user19', 'Quincy', 'Lopez', 'quincy.lopez@example.com', 'strong_password'],
    ["20" ,'user20', 'Rachel', 'Gonzalez', 'rachel.gonzalez@example.com', 'strong_password']
]

def wait_for_db(retries=10, delay=5):
    for _ in range(retries):
        try:
            mongo_client.admin.command('ismaster')
            print("Database is ready!")
            return
        except Exception as e:
            print(f"Database not ready yet: {e}")
            time.sleep(delay)
    raise Exception("Could not connect to the database")

if __name__ == "__main__":
    wait_for_db()
    
    for user in users_to_add:
        user[-1] = pwd_context.hash(user[-1])
        add_user(*user)
    
    mongo_users_collection.create_index("username", unique=True)
    mongo_users_collection.create_index("first_name", unique=True)
    mongo_users_collection.create_index("last_name", unique=True)