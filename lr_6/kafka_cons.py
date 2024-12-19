from confluent_kafka import Producer, Consumer, KafkaError
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models.alchemy_models as md
import models.pydantic_models as pdmd
import redis


redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

# PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@db/archdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Kafka
KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "created_file"

# Kafka Producer
def get_kafka_producer():
    return Producer({"bootstrap.servers": KAFKA_BROKER})

# Kafka Consumer
def kafka_consumer_service():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "file-group",
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe([KAFKA_TOPIC])

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Kafka error: {msg.error()}")
                break


        file_data = json.loads(msg.value().decode("utf-8"))
        session = SessionLocal()
        try:
            file_to_db = md.File(**file_data)
            session.add(file_to_db)
            session.commit()
            session.refresh(file_to_db)

            # Обновление кеша
            cache_key = f"folder:{file_to_db.id}:file:{file_to_db.name}"
            redis_client.set(cache_key, json.dumps(pdmd.File.from_orm(file_to_db).dict()))
        finally:
            session.close()

    consumer.close()