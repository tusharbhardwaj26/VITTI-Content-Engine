import os
import json
from datetime import datetime

base_dir = r"c:\Users\tusha\Desktop\Mini_Projects\raindrop-ideas-main\web\logs"
folders = ['ceo', 'posts', 'ideas']

for folder in folders:
    path = os.path.join(base_dir, folder)
    os.makedirs(path, exist_ok=True)
    print(f"Created/Verified: {path}")
    
    # Create a test file
    test_file = os.path.join(path, "test.json")
    with open(test_file, "w") as f:
        json.dump({"test": True, "time": datetime.now().isoformat()}, f)
    print(f"Created test file: {test_file}")
