

from quart import (
    Blueprint, render_template, url_for, session,
    redirect
)

from helper_tools.db_helper import make_session
from helper_tools.web_security import (
    decode_with_itsdangerous_timed, encode_with_itsdangerous_timed,
    encode_with_itsdangerous, decode_with_itsdangerous
)
from helper_tools.date_helper import get_current_time
from helper_tools.email_handling.email_sending import send_email_link

from app_db_models.user_model import UserTable
from app_db_models.connects_model import ConnectsTable

import asyncio


async def get_activation_link() -> str | None:

    user_email = session.get("email", "")
    user_id = session.get("user_id", "")

    if user_email and user_id:
        activation_link= url_for(
            "activate_account_bp.send_activation_email",
            user_id_=encode_with_itsdangerous(user_id),
        )
    else:
        activation_link=None

    return activation_link


activate_account_bp = Blueprint("activate_account_bp", __name__)


@activate_account_bp.get("/activate_account/page")
async def activate_account_page():

    activation_link = await get_activation_link()
    user_email = session.get("email", "")

    return await render_template(
        "activate_account/activate_account_page.html",
        activation_link=activation_link,
        info=user_email
    )


@activate_account_bp.get("/awarded_connects_page")
async def awarded_connects_page():
        
    return await render_template(
        "activate_account/awarded_connects_page.html"
    )



@activate_account_bp.get("/send_activation_email/<user_id_>")
async def send_activation_email(user_id_):

    try:
        int_user_id = int(user_id_)
        user_id = encode_with_itsdangerous_timed(int_user_id)
    except Exception as e:
        decoded_user_id=decode_with_itsdangerous(user_id_)
        user_id = encode_with_itsdangerous_timed(decoded_user_id)

    try:

        asyncio.create_task(
            send_email_link(
                email=session.get("email", ""),
                reason="activate_account",
                link=url_for(
                    "activate_account_bp.activate_account",
                    user_id_=user_id,
                    _external=True
                )
            )
        )

    
        return await render_template(
            "activate_account/activate_account_page.html",
            activation_link=None,
            info="Email with the activation link sent successfully, expires in 5mins"
        )
    
    except Exception as e:
        print(f"Error = {e}")

        return await render_template(
            "activate_account/activate_account_page.html",
            activation_link=None,
            info="An error occurred while sending the email"
        )


@activate_account_bp.get("/activate_account/<user_id_>") #type:ignore
async def activate_account(user_id_):

    try:

        user_id = decode_with_itsdangerous_timed(user_id_)

        activation_link = await get_activation_link()

        if not user_id:
            return await render_template(
                "activate_account/activate_account_page.html",
                activation_link=activation_link,
                info="Activation Link Expired or Invalid!"
            )

        async with make_session() as sess:

            user = await sess.get(UserTable, user_id)
        
            new_connects = ConnectsTable(
                user_id=int(user_id),
                date_time=await get_current_time(),
                available_connects=10
            )


            if user:
                try:
                    user.account_status = "active"

                    sess.add(new_connects)
                    await sess.commit()

                    return redirect(url_for("activate_account_bp.awarded_connects_page"))
                
                except Exception as e:
                    print(f"Error = {e}")
                    await sess.rollback()
                    
                    return await render_template(
                        "activate_account/activate_account_page.html",
                        activation_link=activation_link,
                        info="Looks like you've already activated your account. Please login to continue."
                    )
            else:        
                return await render_template(
                    "activate_account/activate_account_page.html",
                    activation_link=None,
                    info="Invalid user."
                )
            
        return redirect(url_for("timezone_bp.sign_up_page"))
    
    except Exception as ex:

        print(f"Error = {ex}")

        activation_link = await get_activation_link()

        return await render_template(
            "activate_account/activate_account_page.html",
            activation_link=activation_link,
            info=f"Activation link expired or invalid. Please try again."
        )