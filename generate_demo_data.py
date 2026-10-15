import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(42)

records = []
start_time = datetime(
    2026, 10, 14, 8, 0, tzinfo=timezone.utc
)

for i in range(120):
    timestamp = start_time + timedelta(minutes=i)

    temperature = round(random.uniform(22, 39), 2)
    humidity = round(random.uniform(35, 82), 2)
    air_quality = random.randint(35, 170)
    co2 = random.randint(500, 1450)

    records.append({
        "device_id": {"S": "IoT_Sensor_001"},
        "timestamp": {"S": timestamp.isoformat()},
        "temperature": {"N": str(temperature)},
        "humidity": {"N": str(humidity)},
        "air_quality": {"N": str(air_quality)},
        "co2": {"N": str(co2)}
    })

payload = {
    "Items": records,
    "Count": len(records),
    "ScannedCount": len(records)
}

output = Path(__file__).resolve().parent / "sensor_data.json"

with open(output, "w", encoding="utf-8") as file:
    json.dump(payload, file, indent=4)

print(f"Successfully generated {len(records)} demo readings.")