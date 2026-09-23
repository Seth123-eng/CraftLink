

from datetime import datetime, timezone

async def get_current_time():
    
    try:
        current_time = datetime.now(timezone.utc)
        print("grabbed the current time")
    except Exception as e:
        print("Failed to grab the current time")
        print(f"Exception = {e}")
        
        
    return current_time