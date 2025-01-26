from kafka import KafkaConsumer
import json

# Create Kafka consumer
consumer = KafkaConsumer(
    'system-events',  # Topic name
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',  # Read from the beginning
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))  # Deserialize JSON messages
)

print("Listening to Kafka topic: system-events")
for message in consumer:
    print(f"Received message: {message.value}")
