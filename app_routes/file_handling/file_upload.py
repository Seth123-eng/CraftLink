

from quart import (
     request, render_template, url_for, Blueprint, jsonify
)

from quart_auth import current_user


from app_db_models.file_model import FileTable

from helper_tools.db_helper import make_session
from helper_tools.date_helper import get_current_time
from helper_tools.authenticated_clients_manager import (
    login_required, technician_required
)

from sqlalchemy import select

from .s3_upload_helper.upload_with_a_presigned_url import upload_file_with_a_presigned_url
from .s3_upload_helper.delete_files_from_s3 import delete_obj_from_s3


file_upload_bp = Blueprint("file_upload_bp", __name__)


@file_upload_bp.route("/update/profile/page", methods=["GET", "POST"])
@login_required
async def update_profile_page():

    return await render_template("update_profile.html")


@file_upload_bp.route("/update/profile", methods=["GET", "POST"])
@login_required
async def update_profile():
    
    if request.method == "POST":
        
        files = await request.files
        
        file = files.get("file")

        current_time = await get_current_time()
        
        if file:
            if current_user.auth_id is not None:
                file_name = f"{current_user.auth_id}_{file.filename}"
            
            async with make_session() as sess:
                if await current_user.is_authenticated and current_user.auth_id is not None:

                    file_record = await sess.scalar(
                        select(FileTable)
                        .where(
                            FileTable.is_profile.is_(True),
                            FileTable.user_id == int(current_user.auth_id)
                        )
                    )

                if file_record:
                    
                    #put method replaces the file with the same name
                    #await delete_obj_from_s3(file_record.file_name)

                    file_record.file_name = file_name

                    print(f"client already has a profile,, updating profile")

                    presigned_url = await upload_file_with_a_presigned_url(
                        file_type=file.mimetype,
                        file_name=file_name
                    )

                    await sess.commit()

                    return jsonify({
                        "success":  True,
                        "presigned_url": presigned_url
                    })
                
                else:
                
                    try:

                        if await current_user.is_authenticated and current_user.auth_id is not None:

                            new_file = FileTable(
                                file_name=file_name,
                                file_type=file.mimetype,
                                user_id=int(current_user.auth_id),
                                is_profile=True,
                                date_time=current_time
                            )

                        sess.add(new_file)

                        presigned_url = await upload_file_with_a_presigned_url(
                            file_type=file.mimetype,
                            file_name=file_name
                        )

                        await sess.commit()

                        print(f"File uploaded successfully")

                        return jsonify({
                            "success":  True,
                            "presigned_url": presigned_url
                        })
                    
                    except Exception as e:

                        print(f"Exception = {e}")

                        await sess.rollback()

                        return jsonify({
                            "success":  False,
                            "message": f"Failed to upload file"
                        })
        else:
            
            return jsonify({
                "success":  False,
                "message": f"No file selected upload"
            })
    else:
        
        return jsonify({
            "redirect": url_for("file_upload_bp.update_profile_page")
        })
    


@file_upload_bp.route("/upload/potfolio/files", methods=["GET", "POST"])
@technician_required
async def upload_potfolio_files():
    
    if request.method == "POST":
        
        files = await request.files
        
        file = files.get("file")
        
        if file:

            current_time = await get_current_time()
            
            if current_user.auth_id is not None:
                file_name = f"{current_user.auth_id}_{file.filename}"
            
            async with make_session() as sess:

                if current_user.auth_id is not None:

                    file_record = await sess.scalar(
                        select(FileTable)
                        .where(
                            FileTable.file_name == file_name,
                            FileTable.user_id == int(current_user.auth_id)
                        )
                    )
                #print(f"file_record = {file_record}")

                if file_record:

                    print(f"File being uploaded already exists in the records")

                    return jsonify({
                        "success":  True,
                        "message": f"File being uploaded already exists in the records"
                    })

                try:

                    if current_user.auth_id is not None:

                        new_file = FileTable(
                            file_name=file_name,
                            file_type=file.mimetype,
                            user_id=int(current_user.auth_id),
                            date_time=current_time
                        )

                    sess.add(new_file)

                    presigned_url = await upload_file_with_a_presigned_url(
                        file_type=file.mimetype,
                        file_name=file_name
                    )

                    await sess.commit()

                    print(f"File uploaded successfully")

                    return jsonify({
                        "success":  True,
                        "presigned_url": presigned_url
                    })
                
                except Exception as e:

                    print(f"Exception = {e}")

                    await sess.rollback()

                    return jsonify({
                        "success":  False,
                        "message": f"Failed to upload file"
                    })
            
        else:
            
            return jsonify({
                "success":  False,
                "message": f"No file selected upload"
            })
    else:
        
        return jsonify({
            "redirect": url_for("my_potfolio_bp.my_potfolio_page")
        })