

from quart import (
    Blueprint, jsonify, url_for
)

from quart_auth import current_user

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    login_required
)
from helper_tools.web_security import (
    decode_with_itsdangerous
)

from app_db_models.rating_model import RatingsTable

from sqlalchemy import select



ratings_bp = Blueprint('ratings_bp', __name__)


@ratings_bp.get("/add/rating/<user_rated_id>/<rating>")
@login_required
async def add_rating(user_rated_id, rating):
    
    if await current_user.is_authenticated and current_user.auth_id is not None:
        
        async with make_session() as sess:

            user_rated_id_ = decode_with_itsdangerous(user_rated_id)

            if not user_rated_id_:
                return jsonify({
                    "success": False,
                    "msg": "Error occurred while processing the request."
                })
            
            try:

                new_rating = RatingsTable(
                    rating=int(rating),
                    user_id=int(current_user.auth_id),
                    user_rated_id = int(user_rated_id_)
                )

                sess.add(new_rating)

                await sess.commit()

                return jsonify({
                    "success" : True,
                    "msg" : "Rating added successfully"
                })
            
            except Exception as e:
                
                print(f"Exception = {e}")
                
                return jsonify({
                    "success" : False,
                    "msg" : "Ensure you have a rating"
                })
        
    else:
        
        return jsonify({
            "success" : False,
            "redirect" : url_for("login_logout_bp.handle_logout")
        })
    

@ratings_bp.get("/get/ratings/<user_rated_id>")
@login_required
async def get_ratings(user_rated_id):
    
    if await current_user.is_authenticated and current_user.auth_id is not None:
        
        async with make_session() as sess:

            user_rated_id_ = decode_with_itsdangerous(user_rated_id)
            
            if not user_rated_id_:
                return jsonify({
                    "success": False,
                    "msg": "Error occurred while processing the request."
                })
            
            try:
                
                ratings = await sess.scalar(
                    select(RatingsTable)
                    .where(
                        RatingsTable.user_rated_id == int(user_rated_id_)
                    )
                )

                if ratings:
                    rating = ratings.rating
                else:
                    rating = 0

                return jsonify({
                    "success" : True,
                    "ratings" : rating
                })
                
            except Exception as e:
                
                print(f"Exception = {e}")
                
                return jsonify({
                    "success" : False,
                    "msg" : "Ensure you have a rating"
                })
        
    else:
        
        return jsonify({
            "success" : False,
            "redirect" : url_for("login_logout_bp.handle_logout")
        })