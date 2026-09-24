

from quart import (
    Blueprint, render_template, jsonify,
    request
)

from quart_auth import current_user

from helper_tools.db_helper import make_session
from helper_tools.authenticated_clients_manager import (
    login_required, get_current_user, client_required
)
from helper_tools.date_helper import get_current_time
from helper_tools.web_security import (
    encode_with_itsdangerous, decode_with_itsdangerous
)

from app_db_models.job_postings_models import JobPostingsTable
from app_db_models.user_model import UserTable

from sqlalchemy import select

jobs_bp = Blueprint("jobs_bp", __name__)



@jobs_bp.get("/job-postings/page")
@login_required
async def job_postings_page():

    async with make_session() as sess:

        if current_user.auth_id:
            current_user_ = await sess.get(UserTable, int(current_user.auth_id))

            if not current_user_:
                current_user_id=None
                account_type=None
            else:
                current_user_id = current_user_.id
                account_type = current_user_.account_type


    return await render_template(
        "jobs_folder/job_postings_page.html",
        current_user_=current_user_,
        current_user_id=current_user_id,
        account_type=account_type,
        encode_with_itsdangerous=encode_with_itsdangerous
    )


@jobs_bp.get("/get-job-postings")
@login_required
async def get_job_postings():
    
    async with make_session() as sess:

        user = await get_current_user()

        if not user:
            return jsonify({
                "success" :False,
                "message" : "You must be logged in to view job postings"
            })

        if user.account_type == "client":

            job_postings_ = await sess.execute(
                select(
                    JobPostingsTable, UserTable
                )
                .join(UserTable, JobPostingsTable.user_id == UserTable.id)
                .where(
                    JobPostingsTable.user_id == int(user.id)
                )
            )
        else:

            job_postings_ = await sess.execute(
                select(
                    JobPostingsTable, UserTable
                )
                .join(UserTable, JobPostingsTable.user_id == UserTable.id)
            )


        jobs = []

        for job, user in job_postings_.all():
            
            if current_user.auth_id is None:

                return jsonify({
                    "success" : False,
                    "msg" : "You must be logged in to view your job postings"
                })

            jobs.append(
                {
                    "job_description" : job.job_description,
                    "user_id" : encode_with_itsdangerous(job.user_id),
                    "id" : encode_with_itsdangerous(job.id),
                    "user_name" : user.user_name,
                    "avatar_url" : "",
                    "status" : job.status,
                    "job_category" : job.job_category,
                    "phone _number" : "",
                    "email" : "",
                    "location" : ""
                })      



        if jobs:

            print(f"jobs: {jobs}")

            return jsonify({
                "success" : True,
                "jobs" : jobs
            })
        else:
            return jsonify({
                "success" : False,
                "jobs" : []
            })
        


@jobs_bp.route('/remove-job/<job_id>')
@client_required
async def remove_job(job_id):
    
    async with make_session() as sess:

        job_id_ = decode_with_itsdangerous(job_id)

        if not job_id_:
            return jsonify({
                "success": False,
                "msg": "Job Not found."
            })
        
        try:
            
            if current_user.auth_id is None:
                return jsonify({
                    "success": False,
                    "message": "User not authenticated"
                })
            else:
                job = await sess.scalar(
                    select(JobPostingsTable)
                    .where(JobPostingsTable.id == int(job_id_))
                )
                if job:
                    if current_user.auth_id == job.user_id:
                        await sess.delete(job)
                        await sess.commit()

                        return jsonify({
                            "success": True,
                            "msg": "Job removed successfully"
                        })
                    else:
                        return jsonify({
                            "success": False,
                            "msg": "You are not the owner of this job"
                        })
                else:
                    return jsonify({
                        "success": False,
                        "msg": "Job not found"
                    })
                
        except Exception as e:

            await sess.rollback()
            
            print(f"Exception = {e}")
            
            return jsonify({
                "success" : False,
                "msg" : "Ensure you have a job"
            })
        


@jobs_bp.route("/post/job", methods=["POST"])
@client_required
async def post_job():
    
    async with make_session() as sess:
        
        form = await request.form
        
        try:
            new_job = JobPostingsTable(
                job_description=form.get("job_description"),
                job_category=form.get("job_category"),
                user_id=int(current_user.auth_id) if current_user.auth_id is not None else None,
                date_time=await get_current_time()
            )

            sess.add(new_job)

            await sess.commit()

            return jsonify({
                "success" : True,
                "msg" : "Job added successfully"
            })
        
        except Exception as e:

            print(f"Exception = {e}")

            await sess.rollback()

            return jsonify({
                "success" : False,
                "msg" : "Ensure you have a job description and title"
            })



@jobs_bp.route('/decode-id', methods=['POST'])
@login_required
async def decode_id():
    data = await request.get_json()
    encoded_id = data.get('encoded_id')
    
    if not encoded_id:
        return jsonify({"success": False, "msg": "No encoded ID provided"})
    
    try:
        decoded_id = decode_with_itsdangerous(encoded_id)
        return jsonify({"success": True, "decoded_id": decoded_id})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})