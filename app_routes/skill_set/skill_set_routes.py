

from quart import (
    Blueprint, request, url_for,
    jsonify, render_template
)

from quart_auth import current_user

from app_db_models.skill_set_model import SkillSetTable

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    technician_required
)
from helper_tools.date_helper import get_current_time

from sqlalchemy import select

skill_set_bp = Blueprint("skill_set_bp", __name__)


@skill_set_bp.get("/skills/page")
@technician_required
async def skill_set_page():

    return await render_template("skill_set_page.html")


@skill_set_bp.get("/my_skill_set")
@technician_required
async def my_skill_set():
    
    data = request.args.get("data")
    
    async with make_session() as sess:

        try:
            if current_user.auth_id is not None:
            
                skill_set_ = await sess.scalars(
                    select(SkillSetTable)
                    .where(
                        SkillSetTable.user_id == int(current_user.auth_id)
                    )
                )

                skills = [
                    {
                        "skill_set" : skill.skill_set,
                        "id" : skill.id
                    }
                    for skill in skill_set_.all()
                ]

                print(f"skills = {skills}")

                return jsonify({
                    "success" : True,
                    "msg" : "Skill set loaded successfully",
                    "skill_set" : skills
                })
            
            else:
                return jsonify({
                    "redirect" : url_for("login_logout_bp.handle_logout")
                })
            
        except Exception as e:
            
            print(f"Exception = {e}")

            skill_set_ = []
            
            return jsonify({
                "success" : False,
                "msg" : "Ensure you have a skill set"
            })



@skill_set_bp.post("/delete_skillset/<skill_set_id>")
@technician_required
async def delete_skillset(skill_set_id):
    
    
    async with make_session() as sess:
        
        try:

            if current_user.auth_id is not None:
            
                skill_set_ = await sess.scalar(
                    select(SkillSetTable)
                    .where(
                        SkillSetTable.user_id == int(current_user.auth_id),
                        SkillSetTable.id == int(skill_set_id)
                    )
                )
            else:

                return jsonify({
                    "success" : False,
                    "redirect" : url_for("login_logout_bp.handle_logout")
                })
            
            if skill_set_:
                
                await sess.delete(skill_set_)
                
                await sess.commit()
                
                return jsonify({
                    "success" : True,
                    "msg" : "Skill set deleted successfully"
                })
                
            else:
                
                return jsonify({
                    "success" : False,
                    "msg" : "Skill set not found"
                })
            
        except Exception as e:
            
            print(f"Exception = {e}")
            
            return jsonify({
                "success" : False,
                "msg" : "Ensure you have a skill set"
            })
        

@skill_set_bp.post("/add/skill_set")
@technician_required
async def add_skill_set():
    
    data = request.args.get("data")

    print(f"data = {data}")
    
    async with make_session() as sess:
        
        try:

            if current_user.auth_id is not None:
            
                skill_set_ = await sess.scalar(
                    select(SkillSetTable)
                    .where(
                        SkillSetTable.user_id == int(current_user.auth_id),
                        SkillSetTable.skill_set == data
                    )
                )
            else:
                return jsonify({
                    "success" : False,
                    "redirect" : url_for("login_logout_bp.handle_logout")
                })
            
            if not skill_set_:

                if current_user.auth_id is not None:

                    try:

                        if data:
                
                            sess.add(SkillSetTable(
                                skill_set=data.capitalize(),
                                user_id=int(current_user.auth_id),
                                date_time=await get_current_time()
                            ))
                            
                            await sess.commit()

                            return jsonify({
                                "success" : True,
                                "msg" : "Skill set added successfully"
                            })
                        else:
                            return jsonify({
                                "success" : False,
                                "msg" : "Provide a skill a skill set"
                            })
                    
                    except Exception as e:
                        
                        await sess.rollback()
                        
                        print(f"Exception = {e}")
                        
                        return jsonify({
                            "success" : False,
                            "msg" : "Ensure you have a skill set"
                        })
                
                else:
                    
                    return jsonify({
                        "success" : False,
                        "redirect" : url_for("login_logout_bp.handle_logout")
                    })
                
            else:
                
                return jsonify({
                    "success" : False,
                    "msg" : "Skill set found in your records, pick another skill set!!"
                })
            
        except Exception as e:
            
            print(f"Exception = {e}")
            
            return jsonify({
                "success" : False,
                "msg" : "Ensure you have a skill set"
            })