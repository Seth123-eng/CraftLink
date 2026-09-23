
from quart import (
     request, render_template, url_for, Blueprint, jsonify, session
)



timezone_bp = Blueprint("timezone_bp", __name__)


@timezone_bp.route('/')
async def welcome_page():
    
    return await render_template('auth_pages/welcome_page.html')
    

@timezone_bp.route('/get/user/timezone', methods=['POST'])
async def get_user_timezone():
    
    data = await request.get_json()
     
    zone_name =data.get("timezone")
    
    if zone_name:
        session['zone_name'] = zone_name
    
    return jsonify({
        'redirect': url_for('timezone_bp.sign_up_page')
    })


@timezone_bp.route('/signup/page')
async def sign_up_page():
        return await render_template('auth_pages/sign_up_login_page.html',
                                     msg="Access your dashboard"
                                     )