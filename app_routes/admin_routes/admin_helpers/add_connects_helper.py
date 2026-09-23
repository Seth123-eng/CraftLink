

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time

from app_db_models.connects_model import ConnectsManagement  


async def add_connects(user_id: int, connects_with_cost: list) -> None:
    
    async with make_session() as sess:
        try:

            print(f"connects_with_cost = {connects_with_cost}")

            # Filter out empty strings and invalid formats
            valid_connects = []
            for connect in connects_with_cost:
                if not connect or not connect.strip():  # Skip empty strings
                    print(f"Skipping empty value: '{connect}'")
                    continue
                    
                try:
                    parts = connect.split(":")
                    if len(parts) != 2:
                        print(f"Skipping invalid format: {connect}")
                        continue
                    
                    connects_value = int(parts[0])
                    cost_value = float(parts[1])
                    valid_connects.append((connects_value, cost_value))
                    
                except ValueError as ve:
                    print(f"Invalid numeric value in: {connect} - {ve}")
                    continue

            if not valid_connects:
                print("No valid connects to add")
                return  # Exit early if nothing valid to add

            # Add all valid connects
            for connects_value, cost_value in valid_connects:
                sess.add(
                    ConnectsManagement(
                        user_id=user_id,
                        connects=connects_value,
                        connects_cost=cost_value,
                        date_time=await get_current_time()
                    )
                )

            await sess.commit()
            print(f"Successfully added {len(valid_connects)} connects")
        
        except Exception as e:
            await sess.rollback()
            print(f"Error = {e}")
            print("Error updating connects")