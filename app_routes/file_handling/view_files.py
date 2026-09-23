

from app_db_models.file_model import FileTable

from quart import (
    Blueprint, jsonify
)

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import login_required

from sqlalchemy import select


import os
from dotenv import load_dotenv
load_dotenv(override=True)

filebase_cdn_base_url = os.getenv("FILEBASE_CDN_BASE_URL", "").strip()



view_file_bp = Blueprint("view_file_bp", __name__)


@view_file_bp.get("/view/file/<file_id>")
@login_required
async def view_file(file_id):

    async with make_session() as sess:

        file_ = await sess.scalar(
            select(FileTable)
            .where(
                FileTable.id == int(file_id)
            )
        )

        if file_:
            
            file_access_link = f"{filebase_cdn_base_url}/{file_.file_name}"

            print(f"file_access_link = {file_access_link}")
            
            return jsonify({
                "success" : True,
                "file_access_link" : file_access_link
            })
        else:
            return jsonify({
                "success" : False,
                "msg" : "File not found"
            })