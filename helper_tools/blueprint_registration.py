
from app_factory import web_app

from app_routes.auth.grab_timezone import timezone_bp
from app_routes.auth.login_logout_routes import login_logout_bp
from app_routes.auth.register_client import register_client_bp
from app_routes.auth.not_authourized_route import not_authourized_bp
from app_routes.auth.dashboard_routes import dashboard_bp
from app_routes.auth.activate_account import activate_account_bp

from app_routes.file_handling.file_upload import file_upload_bp
from app_routes.file_handling.view_files import view_file_bp

from app_routes.account_management.delete_account import delete_account_bp
from app_routes.account_management.recover_account import recover_account_bp
from app_routes.account_management.update_account_info import update_account_info_bp

from app_routes.skill_set.skill_set_routes import skill_set_bp

from app_routes.potfolio.my_potfolio import my_potfolio_bp

from app_routes.ratings_manager.ratings import ratings_bp

from app_routes.talent_finder.talent_finder import talent_finder_bp

from app_routes.complaints_handler.complaints_reporting import complaints_reporting_bp

from app_routes.chats_manager.messaging_helper.private_chat_client import private_chat_client_bp
from app_routes.chats_manager.private_chats import private_chat_bp

from app_routes.jobs_manager.jobs_routes import jobs_bp

from app_routes.notification.notification_handler import notification_bp

from app_routes.apis.payments_manager.payments import payments_bp
from app_routes.apis.payments_manager.callback_route import callback_bp

from app_routes.admin_routes.admin_dashboard import admin_bp
from app_routes.admin_routes.dashboard_items import dashboard_items_bp
from app_routes.admin_routes.complaints import complaints_bp

from app_routes.help_pages.help import help_bp
from app_routes.contact_us_routes.contact_us import contact_us_bp

from app_routes.password_reset.reset_password import reset_password_bp

from app_routes.refferals_management.refferals import refferals_bp

blueprints=[
    timezone_bp,
    login_logout_bp,
    register_client_bp,
    not_authourized_bp,
    dashboard_bp,
    activate_account_bp,

    file_upload_bp,
    view_file_bp,

    delete_account_bp,
    recover_account_bp,
    update_account_info_bp,

    skill_set_bp,

    my_potfolio_bp,

    ratings_bp,

    talent_finder_bp,

    complaints_reporting_bp,

    private_chat_client_bp,
    private_chat_bp,

    jobs_bp,

    notification_bp,

    payments_bp,
    callback_bp,

    admin_bp,
    dashboard_items_bp,
    complaints_bp,

    help_bp,

    contact_us_bp,

    reset_password_bp,

    refferals_bp
]


blueprints_not_registered=[]
async def register_all_blueprints():
    
    count=0
    
    for blueprint in blueprints:
        
        try:
            web_app.register_blueprint(blueprint)
            print(f"Blueprint {blueprint.__repr__} registered🎉")
            count += 1
        except Exception as e:
            print(f"Failed to register blueprint {blueprint.__repr__}")
            print(f"Exception = {e}")

            blueprints_not_registered.append({
                "blueprint": blueprint,
                "exception": e
            })
            
    print(f"Registered Blueprints == {count} 🎉🎉")

    print(f"blueprints_not_registered = {blueprints_not_registered}")