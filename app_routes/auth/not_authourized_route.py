


from quart import render_template, Blueprint


not_authourized_bp = Blueprint("not_authourized_bp", __name__)


@not_authourized_bp.get("/not_authourized/page")
async def not_authourized_page():

    return await render_template("not_authorized.html")