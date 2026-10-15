
import random
import json
from datetime import datetime, timezone

def generate_sensor_data():
    data = {
        "device_id": "IoT_Sensor_001",
        "temperature": round(random.uniform(20, 40), 2),
        "humidity": round(random.uniform(30, 80), 2),
        "air_quality": random.randint(20, 150),
        "co2": random.randint(350, 1200),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return data

if __name__ == "__main__":
    sensor_data = generate_sensor_data()
    print(json.dumps(sensor_data, indent=4))
