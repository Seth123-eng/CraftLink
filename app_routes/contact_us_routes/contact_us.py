

from quart import (
     request, render_template, Blueprint, jsonify
)

from quart_auth import current_user


from app_db_models.contact_us_model import ContactUsTable

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time
from helper_tools.authenticated_clients_manager import (
    login_required, admin_required
)
from helper_tools.web_security import (
    encode_with_itsdangerous, decode_with_itsdangerous
)

from sqlalchemy import select, func


contact_us_bp = Blueprint("contact_us_bp", __name__)


@contact_us_bp.get("/contact_us_page")
@admin_required
async def contact_us_page():

    return await render_template("admin/contact_us.html")


@contact_us_bp.post("/add_to_contact_us")
@login_required
async def add_to_contact_us():

    async with make_session() as sess:

        form = await request.form

        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "User not authenticated"
            })
        
        else:

            form = await request.form

            try:
                sess.add(
                    ContactUsTable(
                        message=form.get("message", ""),
                        user_id=int(current_user.auth_id),
                        date_time= await get_current_time()
                    )
                )

                await sess.commit()

                return jsonify({
                    "success" : True,
                    "msg" : "Message added successfully"
                })
            except Exception as e:
                
                print(f"Exception = {e}")

                await sess.rollback()
                
                return jsonify({
                    "success" : False,
                    "msg" : "Ensure you have a message"
                })
            


@contact_us_bp.get("/get/contact_us")
@admin_required
async def get_contact_us():
    
    async with make_session() as sess:

        contact_us_ = await sess.execute(
            select(ContactUsTable)
            .order_by(ContactUsTable.date_time.desc())
        )
        
        #displayed in a receipt style on the frontend
        try:
            contact_us = [
                {
                    "id": encode_with_itsdangerous(contact_us.id),
                    "message": contact_us.message,
                    "date_time": contact_us.date_time.isoformat() if contact_us.date_time else None,
                    "is_read": contact_us.is_read
                }
                for contact_us in contact_us_.scalars().all()
            ]
        except Exception as e:
            print(f"Exception = {e}")
            contact_us=[]

        if contact_us:

            return jsonify({
                "success": True,
                "contact_us": contact_us
            })
        else:
            return jsonify({
                "success": False,
                "contact_us": []
            })
        


@contact_us_bp.post("/delete/contact_us/<contact_us_id_>")
@admin_required
async def delete_contact_us(contact_us_id_):
    
    async with make_session() as sess:

        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "User not authenticated"
            })
        
        else:

            try:

                contact_us_id = decode_with_itsdangerous(contact_us_id_)

                contact_us = await sess.scalar(
                    select(ContactUsTable)
                    .where(
                        ContactUsTable.id == contact_us_id
                    )
                )

                await sess.delete(contact_us)

                await sess.commit()

                return jsonify({
                    "success": True,
                    "msg": "Contact us deleted successfully"
                })
            
            except Exception as e:
                
                print(f"Exception = {e}")
                
                await sess.rollback()
                
                return jsonify({
                    "success": False,
                    "msg": "Contact us not deleted"
                })
            

@contact_us_bp.post("/mark/contact_us/read/<contact_us_id_>")
@admin_required
async def mark_contact_us_read(contact_us_id_):
    
    async with make_session() as sess:

        if current_user.auth_id is None:
            return jsonify({
                "success": False,
                "message": "User not authenticated"
            })
        
        else:

            try:

                contact_us_id = decode_with_itsdangerous(contact_us_id_)

                contact_us = await sess.scalar(
                    select(ContactUsTable)
                    .where(
                        ContactUsTable.id == contact_us_id
                    )
                )
                
                if contact_us:
                    contact_us.is_read = True
    
                    await sess.commit()

                    return jsonify({
                        "success": True,
                        "msg": "Contact us marked as read successfully"
                    })
                else:
                    return jsonify({
                        "success": False,
                        "msg": "Contact us not found"
                    })
            
            except Exception as e:
                
                print(f"Exception = {e}")
                
                await sess.rollback()
                
                return jsonify({
                    "success": False,
                    "msg": "Contact us not marked as read"
                })
            



@contact_us_bp.get("/get/contact_us/unread/count")
@admin_required
async def get_contact_us_unread_count():
    """
    Get the count of unread contact messages for the admin.
    """
    async with make_session() as sess:
        try:
            # Count unread messages
            unread_count = await sess.scalar(
                select(func.count(ContactUsTable.id))
                .where(ContactUsTable.is_read == False)
            )

            if unread_count is None:
                return jsonify({
                    "success": False,
                    "message": "Error counting unread messages"
                })

            return jsonify({
                "success": True,
                "unread_count": unread_count
            })

        except Exception as e:
            print(f"Exception in get_contact_us_unread_count: {e}")
            return jsonify({
                "success": False,
                "message": "An error occurred"
            })