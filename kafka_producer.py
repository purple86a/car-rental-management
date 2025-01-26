from kafka import KafkaProducer
import json

class KafkaEventProducer:
    def __init__(self, topic: str, bootstrap_servers: str = "localhost:9092"):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def send_event(self, event: dict):
        try:
            self.producer.send(self.topic, value=event)
            print(f"Event sent to topic {self.topic}: {event}")
        except Exception as e:
            print(f"Failed to send event: {str(e)}")


