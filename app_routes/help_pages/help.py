

from quart import (
    Blueprint, render_template
)

from quart_auth import login_required


help_bp = Blueprint("help_bp", __name__)



@help_bp.get("/help")
@login_required
async def help_page():
    
    return await render_template("help_page.html")