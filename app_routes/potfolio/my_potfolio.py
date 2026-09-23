

from quart import (
    Blueprint, render_template, jsonify,
    url_for
)

from quart_auth import current_user

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    login_required, technician_required
)
from helper_tools.web_security import (
    decode_with_itsdangerous
)

from app_db_models.file_model import FileTable

from app_routes.file_handling.s3_upload_helper.delete_files_from_s3 import delete_obj_from_s3


from sqlalchemy import select

import os

from dotenv import load_dotenv
load_dotenv(override=True)


my_potfolio_bp = Blueprint('my_potfolio_bp', __name__)


ENDPOINT=f'{os.getenv("FILEBASE_CDN_BASE_URL", "").strip()}/'


@my_potfolio_bp.route('/my_potfolio', methods=['GET'])
@technician_required
async def my_potfolio_page():

    return await render_template(
        'my_potfolio_page.html',
        ENDPOINT=ENDPOINT
    )



@my_potfolio_bp.post('/my_potfolio/files')
@technician_required
async def potfolio_files():
    
    async with make_session() as sess:

        if await current_user.is_authenticated and current_user.auth_id is not None:
            
            try:
                files_ = await sess.execute(
                    select(
                        FileTable.file_name,
                        FileTable.id
                    )
                    .where(
                        FileTable.user_id == int(current_user.auth_id),
                        FileTable.is_profile.is_(False)
                    )
                )

                file_names = [
                    {
                        "file_id" : file.id,
                        "file_name" : file.file_name
                    }
                    for file in files_.all()
                ]

                if file_names:
                    return jsonify({
                        "success" : True,
                        "files" : file_names
                    })
                else:
                    return jsonify({
                        "success" : False,
                        "file" : []
                    })
                
            except Exception as e:

                print(f"Error = {e}")

                return jsonify({
                    "success" : False,
                    "message" : "Something went wrong loading files"
                })
            
        else:

            return jsonify({
                "success" : False,
                "redirect" : url_for('login_logout_bp.handle_logout')
            })
        


@my_potfolio_bp.post('/my_potfolio/files/delete/<file_id>')
@technician_required
async def delete_file(file_id):
    
    async with make_session() as sess:
        
        if await current_user.is_authenticated and current_user.auth_id is not None:
            
            try:
                file_record = await sess.scalar(
                    select(FileTable)
                    .where(
                        FileTable.id == int(file_id)
                    )
                )

                if file_record:

                    await delete_obj_from_s3(file_record.file_name)

                    await sess.delete(file_record)
                    await sess.commit()

                    return jsonify({
                        "success" : True
                    })
                else:
                    return jsonify({
                        "success" : False,
                        "message" : "File not found"
                    })
            
            except Exception as e:

                print(f"Error = {e}")
                return jsonify({
                    "success" : False,
                    "message" : "Something went wrong deleting file"
                })
            
        else:

            return jsonify({
                "success" : False,
                "redirect" : url_for('login_logout_bp.handle_logout')
            })
        

@my_potfolio_bp.get("/client-potfolio/files/<client_id_>")
@login_required
async def get_files(client_id_):
    
    async with make_session() as sess:

        if await current_user.is_authenticated and current_user.auth_id is not None:
            
            try:

                client_id = decode_with_itsdangerous(client_id_)

                if not client_id:
                    return jsonify({
                        "success": False,
                        "msg": "Client not Found."
                    })

                files_ = await sess.execute(
                    select(
                        FileTable.file_name,
                        FileTable.id
                    )
                    .where(
                        FileTable.user_id == int(client_id),
                        FileTable.is_profile.is_(False)
                    )
                )

                client_files = [
                    {
                        "file_name" : file.file_name,
                        "file_id" : file.id
                    }
                    for file in files_.all()
                ]

                if client_files:
                    return jsonify({
                        "success" : True,
                        "files" : client_files
                    })
                else:
                    return jsonify({
                        "success" : False,
                        "file" : []
                    })
                
            except Exception as e:

                print(f"Error = {e}")

                return jsonify({
                    "success" : False,
                    "message" : "Something went wrong loading files"
                })
            
        else:

            return jsonify({
                "success" : False,
                "redirect" : url_for('login_logout_bp.handle_logout')
            })