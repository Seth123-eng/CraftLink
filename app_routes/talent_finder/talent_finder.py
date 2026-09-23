

from quart import (
    Blueprint, render_template, jsonify,
    url_for
)

from quart_auth import current_user

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    client_required
)
from helper_tools.web_security import (
    encode_with_itsdangerous
)

from app_db_models.skill_set_model import SkillSetTable
from app_db_models.user_model import UserTable

from sqlalchemy import select

import os

from dotenv import load_dotenv
load_dotenv(override=True)


ENDPOINT=f'{os.getenv("FILEBASE_CDN_BASE_URL", "").strip()}/'


talent_finder_bp = Blueprint('talent_finder_bp', __name__)


@talent_finder_bp.route('/find-talent', methods=['GET'])
@client_required
async def find_talent_page():
    return await render_template('find_talent_page.html',
                                 ENDPOINT=ENDPOINT)



@talent_finder_bp.get('/get_technicians/with_their_skills')
@client_required
async def get_technicians_with_their_skills():
    
    if await current_user.is_authenticated and current_user.auth_id is not None:
        
        async with make_session() as sess:
            
            try:
                
                technicians_skill_set_ = await sess.execute(
                    select( UserTable, SkillSetTable)
                    .join(SkillSetTable, UserTable.id == SkillSetTable.user_id)
                    .where(
                        UserTable.account_type == "technician"
                    )
                )

                technicians_dict = {}
                
                for user, skill in technicians_skill_set_.all():
                    user_id = encode_with_itsdangerous(user.id)
                    
                    if user_id not in technicians_dict:
                        technicians_dict[user_id] = {
                            "user_id": user_id,
                            "user_name": user.user_name,
                            "avatar_url": "",  # will be provided later
                            "phone_number": "",  # will be provided later
                            "email": "",  # will be provided later
                            "skill_set": []
                        }
                    
                    # Add skill to the technician's skill list
                    technicians_dict[user_id]["skill_set"].append(skill.skill_set)

                # Convert dict to list
                technicians_skill_set = list(technicians_dict.values())

                print(f"technicians_skill_set = {technicians_skill_set}")

                if technicians_skill_set:

                    return jsonify({
                        "success" : True,
                        "technicians_skill_set" : technicians_skill_set
                    })
                else:

                    return jsonify({
                        "success" : False,
                        "technicians_skill_set" : []
                    })
                
            except Exception as e:
                print(f"Exception = {e}")
                return jsonify({
                    "success" : False,
                    "message" : "Failed to get technicians with their skills"
                })
            
    else:
        return jsonify({
            "success" : False,
            "redirect" : url_for("login_logout_bp.handle_logout")
        })