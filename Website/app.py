from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
import os


from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.security import (generate_password_hash,check_password_hash)

load_dotenv()


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


app = Flask(
    __name__,
    template_folder=os.path.join(
        BASE_DIR,
        "HTML"
    ),
    static_folder=BASE_DIR,
    static_url_path="/static"
)

CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5500"]
)

app.secret_key = os.getenv("FLASK_SECRET_KEY")


# -------------------------
# DATABASE
# -------------------------

def connect_db():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "astrobase_web")
    )


# -------------------------
# HOME
# -------------------------

@app.route("/")
def home():

    # User is not logged in
    if "user_id" not in session:
        return render_template(
            "index.html",
            user=None
        )

    # Get logged-in user's information
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            user_id,
            name,
            username,
            email,
            role,
            grade,
            country,
            interests,
            career_goals,
            bio
        FROM users
        WHERE user_id = %s
    """

    cursor.execute(
        query,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    db.close()

    # Account no longer exists
    if not user:
        session.clear()
        return redirect("/login")

    return render_template(
        "index.html",
        user=user
    )


# -------------------------
# LOGIN
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    # Open login page
    if request.method == "GET":
        return render_template("login.html")

    # Get login information
    email_or_username = request.form["email"].strip()
    password = request.form["password"]

    # Connect to database
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # Find account using email OR username
    query = """
        SELECT
            user_id,
            username,
            password_hash,
            role,
            organisation_id
        FROM users
        WHERE email = %s OR username = %s
    """

    cursor.execute(
        query,
        (
            email_or_username,
            email_or_username
        )
    )

    user = cursor.fetchone()

    cursor.close()
    db.close()

    # Verify account and password
    if (
        user
        and check_password_hash(
            user["password_hash"],
            password
        )
    ):

        session["user_id"] = user["user_id"]

        session["username"] = user["username"]

        session["role"] = user["role"]

        session["organisation_id"] = user["organisation_id"]


        # Return to Flask homepage

        return redirect("/")

    # Login failed

    return render_template("login.html", error="Incorrect email/username or password.")


# -------------------------
# EDIT PROFILE
# -------------------------

@app.route("/myastrobase/profile/edit", methods=["GET", "POST"])
def edit_profile():

    # User must be logged in
    if "user_id" not in session:
        return redirect("/login")

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # -------------------------
    # OPEN EDIT PROFILE
    # -------------------------

    if request.method == "GET":

        query = """
            SELECT
                user_id,
                name,
                username,
                email,
                role,
                grade,
                country,
                interests,
                career_goals,
                bio
            FROM users
            WHERE user_id = %s
        """

        cursor.execute(
            query,
            (session["user_id"],)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if not user:
            session.clear()
            return redirect("/login")

        return render_template(
            "edit_profile.html",
            user=user
        )


    # -------------------------
    # SAVE PROFILE
    # -------------------------

    name = request.form["name"].strip()
    username = request.form["username"].strip()
    email = request.form["email"].strip()
    grade = request.form["grade"].strip()
    country = request.form["country"].strip()
    interests = request.form["interests"].strip()
    career_goals = request.form["career_goals"].strip()
    bio = request.form["bio"].strip()


    # Check whether another account
    # already uses this username/email

    query = """
        SELECT user_id
        FROM users
        WHERE (email = %s OR username = %s)
        AND user_id != %s
    """

    cursor.execute(
        query,
        (
            email,
            username,
            session["user_id"]
        )
    )

    existing_user = cursor.fetchone()

    if existing_user:

        cursor.close()
        db.close()

        return "Email or username already exists", 400


    # Update profile

    query = """
        UPDATE users
        SET
            name = %s,
            username = %s,
            email = %s,
            grade = %s,
            country = %s,
            interests = %s,
            career_goals = %s,
            bio = %s
        WHERE user_id = %s
    """

    cursor.execute(
        query,
        (
            name,
            username,
            email,
            grade,
            country,
            interests,
            career_goals,
            bio,
            session["user_id"]
        )
    )

    db.commit()

    # Keep the session username
    # synchronized with the database

    session["username"] = username

    cursor.close()
    db.close()

    return redirect("/myastrobase/profile")


# -------------------------
# DELETE ACCOUNT
# -------------------------

@app.route("/myastrobase/profile/delete", methods=["GET", "POST"])
def delete_profile():

    # User must be logged in
    if "user_id" not in session:
        return redirect("/login")


    # Show confirmation page
    if request.method == "GET":
        return render_template("delete_profile.html")


    # Delete the logged-in user's account
    db = connect_db()
    cursor = db.cursor()

    query = """
        DELETE FROM users
        WHERE user_id = %s
    """

    cursor.execute(
        query,
        (session["user_id"],)
    )

    db.commit()

    cursor.close()
    db.close()


    # Destroy login session
    session.clear()


    # Return to public Astrobase
    return redirect("/")


# -------------------------
# REGISTER
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    # Open registration page
    if request.method == "GET":
        return render_template("register.html")

    # Get registration information
    name = request.form["name"].strip()
    username = request.form["username"].strip()
    email = request.form["email"].strip()
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    grade = request.form["grade"].strip()
    country = request.form["country"].strip()
    interests = request.form["interests"].strip()
    career_goals = request.form["career_goals"].strip()
    bio = request.form["bio"].strip()

    # Check passwords
    if password != confirm_password:

        return render_template(
            "register.html",
            error="Passwords do not match."
        )

    # Hash password securely
    password_hash = generate_password_hash(
        password
    )

    # Connect to database
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # Check whether email or username already exists
    query = """
        SELECT user_id
        FROM users
        WHERE email = %s OR username = %s
    """

    cursor.execute(
        query,
        (email, username)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        db.close()

        return "Email or username already exists", 400

    # Create student account
    query = """
        INSERT INTO users (
            name,
            username,
            email,
            password_hash,
            role,
            grade,
            country,
            interests,
            career_goals,
            bio
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            'Student',
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    cursor.execute(
        query,
        (
            name,
            username,
            email,
            password_hash,
            grade,
            country,
            interests,
            career_goals,
            bio
        )
    )

    db.commit()

    cursor.close()
    db.close()

    # Account created
    return redirect("/login")


# -------------------------
# CURRENT USER API
# -------------------------

@app.route("/api/me")
def current_user():

    if "user_id" not in session:

        return jsonify({
            "logged_in": False
        })


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            u.user_id,
            u.name,
            u.username,
            u.role,
            u.grade,
            u.country,
            u.interests,
            u.career_goals,
            u.bio,
            u.organisation_id,
            o.organisation_name,
            o.organisation_type,
            o.status AS organisation_status
        FROM users u
        LEFT JOIN organisations o
            ON u.organisation_id = o.organisation_id
        WHERE u.user_id = %s
    """


    cursor.execute(
        query,
        (session["user_id"],)
    )


    user = cursor.fetchone()


    cursor.close()

    db.close()


    if not user:

        session.clear()

        return jsonify({
            "logged_in": False
        })


    return jsonify({

        "logged_in": True,

        "user": user

    })

# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():

    # Remove all session information
    session.clear()

    # Return to login
    return redirect("/login")


# -------------------------
# USER PROFILE
# -------------------------

@app.route("/myastrobase/profile")
def profile():


    # User must be logged in
    if "user_id" not in session:
        return redirect("/login")
    
    if session.get("role") == "Organisation":

        return redirect("/organisation/profile")

    # Connect to database
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # Get current user's profile
    query = """
        SELECT
            user_id,
            name,
            username,
            email,
            role,
            grade,
            country,
            interests,
            career_goals,
            bio
        FROM users
        WHERE user_id = %s
    """

    cursor.execute(
        query,
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    db.close()

    # Account no longer exists
    if not user:
        session.clear()
        return redirect("/login")

    return render_template(
        "profile.html",
        user=user
    )


@app.route("/organisation/apply", methods=["GET", "POST"])
def organisation_apply():

    if request.method == "GET":

        return render_template("organisation_apply.html")


    organisation_name = request.form.get("organisation_name", "").strip()

    organisation_type = request.form.get("organisation_type", "").strip()

    website = request.form.get("website", "").strip()

    contact_email = request.form.get("contact_email", "").strip()

    description = request.form.get("description", "").strip()

    application_reason = request.form.get("application_reason", "").strip()

    requested_areas = request.form.getlist("requested_areas")


    if not organisation_name or not contact_email or not description or not application_reason:

        return "Please complete all required fields.", 400


    requested_areas_text = ", ".join(requested_areas)


    db = connect_db()

    cursor = db.cursor()


    cursor.execute(
        """
        INSERT INTO organisations
        (
            organisation_name,
            description,
            website,
            contact_email,
            organisation_type
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            organisation_name,
            description,
            website,
            contact_email,
            organisation_type
        )
    )


    organisation_id = cursor.lastrowid


    cursor.execute(
        """
        INSERT INTO organisation_applications
        (
            organisation_id,
            application_reason,
            requested_areas
        )
        VALUES (%s, %s, %s)
        """,
        (
            organisation_id,
            application_reason,
            requested_areas_text
        )
    )


    db.commit()

    cursor.close()

    db.close()


    return render_template("organisation_submitted.html", organisation_id=organisation_id)


# -------------------------
# EDIT ORGANISATION APPLICATION
# -------------------------

@app.route("/organisation/application/<int:organisation_id>/edit", methods=["GET", "POST"])
def edit_organisation_application(organisation_id):

    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # Get organisation and its application

    query = """
        SELECT
            o.organisation_id,
            o.organisation_name,
            o.description,
            o.website,
            o.contact_email,
            o.organisation_type,
            o.status,
            oa.application_id,
            oa.application_reason,
            oa.requested_areas,
            oa.status AS application_status
        FROM organisations o
        JOIN organisation_applications oa
            ON o.organisation_id = oa.organisation_id
        WHERE o.organisation_id = %s
    """

    cursor.execute(
        query,
        (organisation_id,)
    )

    organisation = cursor.fetchone()


    if not organisation:

        cursor.close()

        db.close()

        return "Organisation application not found", 404


    # Only pending applications can be edited

    if organisation["status"] != "Pending":

        cursor.close()

        db.close()

        return "This organisation application can no longer be edited.", 403


    # Open edit page

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "organisation_edit.html",
            organisation=organisation
        )


    # Get updated information

    organisation_name = request.form.get(
        "organisation_name",
        ""
    ).strip()

    organisation_type = request.form.get(
        "organisation_type",
        ""
    ).strip()

    website = request.form.get(
        "website",
        ""
    ).strip()

    contact_email = request.form.get(
        "contact_email",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    application_reason = request.form.get(
        "application_reason",
        ""
    ).strip()

    requested_areas = request.form.getlist(
        "requested_areas"
    )


    if (
        not organisation_name
        or not contact_email
        or not description
        or not application_reason
    ):

        cursor.close()

        db.close()

        return "Please complete all required fields.", 400


    requested_areas_text = ", ".join(
        requested_areas
    )


    # Update organisation

    query = """
        UPDATE organisations
        SET
            organisation_name = %s,
            description = %s,
            website = %s,
            contact_email = %s,
            organisation_type = %s
        WHERE organisation_id = %s
    """

    cursor.execute(
        query,
        (
            organisation_name,
            description,
            website,
            contact_email,
            organisation_type,
            organisation_id
        )
    )


    # Update application

    query = """
        UPDATE organisation_applications
        SET
            application_reason = %s,
            requested_areas = %s,
            status = 'Pending',
            reviewed_at = NULL,
            reviewed_by = NULL,
            review_reason = NULL
        WHERE organisation_id = %s
    """

    cursor.execute(
        query,
        (
            application_reason,
            requested_areas_text,
            organisation_id
        )
    )


    db.commit()

    cursor.close()

    db.close()


    return redirect(
        f"/organisation/application/{organisation_id}"
    )


# -------------------------
# ORGANISATION CHECK-IN
# -------------------------

@app.route(
    "/organisation/check-in",
    methods=["GET", "POST"]
)
def organisation_check_in():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()


        if not email:

            return render_template(
                "organisation_check_in.html",
                error="Please enter your application email."
            )


        db = connect_db()

        cursor = db.cursor(dictionary=True)


        query = """
            SELECT
                o.organisation_id,
                o.organisation_name,
                o.contact_email,
                oa.application_id,
                oa.status AS application_status,
                oa.submitted_at
            FROM organisations o
            JOIN organisation_applications oa
                ON o.organisation_id = oa.organisation_id
            WHERE o.contact_email = %s
            ORDER BY oa.submitted_at DESC
            LIMIT 1
        """


        cursor.execute(
            query,
            (email,)
        )


        application = cursor.fetchone()


        cursor.close()

        db.close()


        if not application:

            return render_template(
                "organisation_check_in.html",
                error="No organisation application was found for this email address."
            )


        return render_template(
            "organisation_check_in.html",
            application=application
        )


    return render_template(
        "organisation_check_in.html"
    )


# -------------------------
# VIEW ORGANISATION APPLICATION
# -------------------------

@app.route("/organisation/application/<int:organisation_id>")
def organisation_application_view(organisation_id):

    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            o.organisation_id,
            o.organisation_name,
            o.description,
            o.website,
            o.contact_email,
            o.organisation_type,
            o.status,
            oa.application_id,
            oa.application_reason,
            oa.requested_areas,
            oa.status AS application_status,
            oa.submitted_at
        FROM organisations o
        JOIN organisation_applications oa
            ON o.organisation_id = oa.organisation_id
        WHERE o.organisation_id = %s
    """


    cursor.execute(
        query,
        (organisation_id,)
    )


    organisation = cursor.fetchone()


    cursor.close()

    db.close()


    if not organisation:

        return "Organisation application not found", 404


    return render_template(
        "organisation_application_view.html",
        organisation=organisation
    )


# -------------------------
# REVIEW ORGANISATION APPLICATION
# -------------------------

@app.route("/admin/organisations/<int:application_id>")
def admin_organisation_review(application_id):

    if "user_id" not in session or session.get("role") != "Admin":

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            oa.application_id,
            oa.organisation_id,
            oa.application_reason,
            oa.requested_areas,
            oa.submitted_at,
            oa.reviewed_at,
            oa.reviewed_by,
            oa.review_reason,
            oa.status,
            o.organisation_name,
            o.description,
            o.website,
            o.contact_email,
            o.organisation_type
        FROM organisation_applications oa
        JOIN organisations o
            ON oa.organisation_id = o.organisation_id
        WHERE oa.application_id = %s
    """


    cursor.execute(
        query,
        (application_id,)
    )


    application = cursor.fetchone()


    cursor.close()

    db.close()


    if not application:

        return "Organisation application not found", 404


    return render_template(
        "admin_organisation_review.html",
        application=application
    )


# -------------------------
# APPROVE ORGANISATION
# -------------------------

@app.route(
    "/admin/organisations/<int:application_id>/approve",
    methods=["POST"]
)
def approve_organisation(application_id):

    if "user_id" not in session or session.get("role") != "Admin":

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # Find the application

    query = """
        SELECT
            organisation_id,
            status
        FROM organisation_applications
        WHERE application_id = %s
    """


    cursor.execute(
        query,
        (application_id,)
    )


    application = cursor.fetchone()


    if not application:

        cursor.close()

        db.close()

        return "Organisation application not found", 404


    # Only pending applications can be approved

    if application["status"] != "Pending":

        cursor.close()

        db.close()

        return "This application has already been reviewed.", 400


    organisation_id = application["organisation_id"]


    # Update application

    query = """
        UPDATE organisation_applications
        SET
            status = 'Approved',
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = %s,
            review_reason = %s
        WHERE application_id = %s
    """


    cursor.execute(
        query,
        (
            session["user_id"],
            "Application approved.",
            application_id
        )
    )


    # Activate organisation

    query = """
        UPDATE organisations
        SET status = 'Verified'
        WHERE organisation_id = %s
    """


    cursor.execute(
        query,
        (organisation_id,)
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect(
        f"/admin/organisations/{application_id}"
    )


# -------------------------
# REJECT ORGANISATION
# -------------------------

@app.route(
    "/admin/organisations/<int:application_id>/reject",
    methods=["POST"]
)
def reject_organisation(application_id):

    if "user_id" not in session or session.get("role") != "Admin":

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # Find the application

    query = """
        SELECT
            organisation_id,
            status
        FROM organisation_applications
        WHERE application_id = %s
    """


    cursor.execute(
        query,
        (application_id,)
    )


    application = cursor.fetchone()


    if not application:

        cursor.close()

        db.close()

        return "Organisation application not found", 404


    # Only pending applications can be rejected

    if application["status"] != "Pending":

        cursor.close()

        db.close()

        return "This application has already been reviewed.", 400


    organisation_id = application["organisation_id"]


    # Update application

    query = """
        UPDATE organisation_applications
        SET
            status = 'Rejected',
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = %s,
            review_reason = %s
        WHERE application_id = %s
    """


    cursor.execute(
        query,
        (
            session["user_id"],
            "Application rejected.",
            application_id
        )
    )


    # Update organisation

    query = """
        UPDATE organisations
        SET status = 'Rejected'
        WHERE organisation_id = %s
    """


    cursor.execute(
        query,
        (organisation_id,)
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect(
        f"/admin/organisations/{application_id}"
    )


# -------------------------
# WITHDRAW ORGANISATION APPLICATION
# -------------------------

@app.route("/organisation/application/<int:organisation_id>/withdraw", methods=["POST"])
def withdraw_organisation_application(organisation_id):

    db = connect_db()

    cursor = db.cursor()


    query = """
        UPDATE organisations
        SET status = 'Withdrawn'
        WHERE organisation_id = %s
        AND status = 'Pending'
    """


    cursor.execute(
        query,
        (organisation_id,)
    )


    query = """
        UPDATE organisation_applications
        SET status = 'Withdrawn'
        WHERE organisation_id = %s
        AND status = 'Pending'
    """


    cursor.execute(
        query,
        (organisation_id,)
    )


    db.commit()

    cursor.close()

    db.close()


    return redirect("/")

# -------------------------
# ORGANISATION ACCOUNT
# -------------------------

@app.route("/organisation/register", methods=["GET", "POST"])
def organisation_register():

    if request.method == "GET":

        return render_template(
            "organisation_register.html"
        )


    organisation_name = request.form.get(
        "organisation_name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )


    if password != confirm_password:

        return "Passwords do not match.", 400


    db = connect_db()

    cursor = db.cursor(dictionary=True, buffered=True)


    # Find the verified organisation

    query = """
        SELECT
            organisation_id,
            organisation_name,
            contact_email,
            status
        FROM organisations
        WHERE organisation_name = %s
        AND contact_email = %s
        AND status = 'Verified'
    """


    cursor.execute(
        query,
        (
            organisation_name,
            email
        )
    )


    organisation = cursor.fetchone()


    if not organisation:

        cursor.close()

        db.close()

        return "Verified organisation not found. Please make sure the organisation name and email match the approved application.", 404


    organisation_id = organisation["organisation_id"]


    # Check whether an account already exists for this organisation

    query = """
        SELECT user_id
        FROM users
        WHERE organisation_id = %s
    """


    cursor.execute(
        query,
        (organisation_id,)
    )


    existing_account = cursor.fetchone()


    if existing_account:

        cursor.close()

        db.close()

        return "An organisation account already exists.", 400


    # Check whether email is already used

    query = """
        SELECT user_id
        FROM users
        WHERE email = %s
    """


    cursor.execute(
        query,
        (email,)
    )


    existing_email = cursor.fetchone()


    if existing_email:

        cursor.close()

        db.close()

        return "This email is already associated with an account.", 400


    password_hash = generate_password_hash(
        password
    )


    # Create Organisation account

    query = """
        INSERT INTO users
        (
            name,
            email,
            password_hash,
            role,
            organisation_id
        )
        VALUES
        (
            %s,
            %s,
            %s,
            'Organisation',
            %s
        )
    """


    cursor.execute(
        query,
        (
            organisation_name,
            email,
            password_hash,
            organisation_id
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect("/login")


# -------------------------
# ORGANISATION DASHBOARD
# -------------------------

@app.route("/organisation/dashboard")
def organisation_dashboard():

    if (
        "user_id" not in session
        or session.get("role") != "Organisation"
    ):

        return redirect("/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            organisation_id,
            organisation_name,
            description,
            website,
            contact_email,
            organisation_type,
            status
        FROM organisations
        WHERE organisation_id = %s
    """


    cursor.execute(
        query,
        (session["organisation_id"],)
    )


    organisation = cursor.fetchone()


    cursor.close()

    db.close()


    if not organisation:

        session.clear()

        return redirect("/login")


    if organisation["status"] != "Verified":

        session.clear()

        return redirect("/login")


    return render_template(
        "organisation_dashboard.html",
        organisation=organisation
    )


# -------------------------
# ORGANISATION OPPORTUNITIES
# -------------------------

@app.route("/organisation/opportunities")
def organisation_opportunities():

    if (
        "user_id" not in session
        or session.get("role") != "Organisation"
    ):

        return redirect("/login")


    organisation_id = session.get(
        "organisation_id"
    )


    if not organisation_id:

        return redirect("/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            o.opportunity_id,
            o.opportunity_name,
            o.category,
            o.description,
            o.eligibility,
            o.deadline,
            o.official_website,
            o.status,
            o.created_at,
            o.updated_at
        FROM opportunities o
        WHERE
            o.organisation_id = %s
        ORDER BY o.created_at DESC
    """


    cursor.execute(
        query,
        (organisation_id,)
    )


    opportunities = cursor.fetchall()


    cursor.close()

    db.close()


    return render_template(
        "organisation_opportunities.html",
        opportunities=opportunities
    )

# -------------------------
# ORGANISATION RESOURCES
# -------------------------

@app.route("/organisation/resources")
def organisation_resources():

    if (
        "user_id" not in session
        or session.get("role") != "Organisation"
    ):

        return redirect("/login")


    organisation_id = session.get(
        "organisation_id"
    )


    if not organisation_id:

        return redirect("/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            r.resource_id,
            r.resource_name,
            r.resource_type,
            r.description,
            r.recommended_for,
            r.official_website,
            r.status,
            r.is_featured,
            r.created_at,
            r.updated_at
        FROM resources r
        WHERE
            r.organisation_id = %s
        ORDER BY r.created_at DESC
    """


    cursor.execute(
        query,
        (organisation_id,)
    )


    resources = cursor.fetchall()


    cursor.close()

    db.close()


    return render_template(
        "organisation_resources.html",
        resources=resources
    )


# -------------------------
# ORGANISATION UNIVERSITIES
# -------------------------

@app.route("/organisation/universities")
def organisation_universities():

    if (
        "user_id" not in session
        or session.get("role") != "Organisation"
    ):

        return redirect("/login")


    organisation_id = session.get(
        "organisation_id"
    )


    if not organisation_id:

        return redirect("/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            u.university_id,
            u.university_name,
            u.country,
            u.city,
            u.university_type,
            u.description,
            u.official_website,
            u.admissions_website,
            u.international_students_info,
            u.additional_notes,
            u.status,
            u.created_at,
            u.updated_at,

            COUNT(
                CASE
                    WHEN p.status != 'Archived'
                    THEN p.programme_id
                END
            ) AS programme_count

        FROM universities u

        LEFT JOIN programmes p
            ON u.university_id = p.university_id

        WHERE
            u.organisation_id = %s

        GROUP BY
            u.university_id,
            u.university_name,
            u.country,
            u.city,
            u.university_type,
            u.description,
            u.official_website,
            u.admissions_website,
            u.international_students_info,
            u.additional_notes,
            u.status,
            u.created_at,
            u.updated_at

        ORDER BY
            u.created_at DESC
    """


    cursor.execute(
        query,
        (
            organisation_id,
        )
    )


    universities = cursor.fetchall()


    cursor.close()

    db.close()


    return render_template(
        "organisation_universities.html",
        universities=universities
    )


# -------------------------
# ORGANISATION ADD UNIVERSITY
# -------------------------

@app.route(
    "/organisation/universities/add",
    methods=["GET", "POST"]
)
def organisation_add_university():

    if (
        "user_id" not in session
        or session.get("role") != "Organisation"
    ):

        return redirect("/login")


    organisation_id = session.get(
        "organisation_id"
    )


    if not organisation_id:

        return redirect("/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Verify Organisation
    # -------------------------

    cursor.execute(
        """
        SELECT
            organisation_id,
            organisation_name,
            status
        FROM organisations
        WHERE organisation_id = %s
        """,
        (
            organisation_id,
        )
    )


    organisation = cursor.fetchone()


    if not organisation:

        cursor.close()

        db.close()

        return "Organisation not found.", 404


    if organisation["status"] != "Verified":

        cursor.close()

        db.close()

        return "Your organisation must be verified before adding universities.", 403


    # -------------------------
    # GET
    # -------------------------

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "organisation_university_add.html",
            organisation=organisation
        )


    # -------------------------
    # POST
    # -------------------------

    university_name = request.form.get(
        "university_name",
        ""
    ).strip()


    country = request.form.get(
        "country",
        ""
    ).strip()


    city = request.form.get(
        "city",
        ""
    ).strip()


    university_type = request.form.get(
        "university_type",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    admissions_website = request.form.get(
        "admissions_website",
        ""
    ).strip()


    international_students_info = request.form.get(
        "international_students_info",
        ""
    ).strip()


    additional_notes = request.form.get(
        "additional_notes",
        ""
    ).strip()


    action = request.form.get(
        "action",
        "draft"
    )


    # -------------------------
    # Validation
    # -------------------------

    if (
        not university_name
        or not country
        or not city
        or not university_type
        or not description
    ):

        cursor.close()

        db.close()

        return render_template(
            "organisation_university_add.html",
            organisation=organisation,
            error="University name, country, city, university type and description are required.",
            form_data=request.form
        )


    # -------------------------
    # Determine Status
    # -------------------------

    if action == "submit":

        status = "Pending"

    else:

        status = "Draft"


    # -------------------------
    # Insert University
    # -------------------------

    query = """
        INSERT INTO universities
        (
            university_name,
            country,
            city,
            university_type,
            description,
            official_website,
            admissions_website,
            international_students_info,
            additional_notes,
            organisation_id,
            status,
            submitted_at
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            NULLIF(%s, ''),
            NULLIF(%s, ''),
            NULLIF(%s, ''),
            NULLIF(%s, ''),
            %s,
            %s,
            CASE
                WHEN %s = 'Pending'
                THEN CURRENT_TIMESTAMP
                ELSE NULL
            END
        )
    """


    cursor.execute(
        query,
        (
            university_name,
            country,
            city,
            university_type,
            description,
            official_website,
            admissions_website,
            international_students_info,
            additional_notes,
            organisation_id,
            status,
            status
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect(
        "/organisation/universities"
    )


# -------------------------
# ORGANISATION EDIT UNIVERSITY
# -------------------------

@app.route(
    "/organisation/universities/<int:university_id>/edit",
    methods=["GET", "POST"]
)
def organisation_edit_university(university_id):

    if (
        "user_id" not in session
        or session.get("role") != "Organisation"
    ):

        return redirect("/login")


    organisation_id = session.get(
        "organisation_id"
    )


    if not organisation_id:

        return redirect("/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Get University
    # -------------------------

    cursor.execute(
        """
        SELECT
            university_id,
            university_name,
            country,
            city,
            university_type,
            description,
            official_website,
            admissions_website,
            international_students_info,
            additional_notes,
            organisation_id,
            status
        FROM universities
        WHERE university_id = %s
        """,
        (
            university_id,
        )
    )


    university = cursor.fetchone()


    if not university:

        cursor.close()

        db.close()

        return "University not found.", 404


    # -------------------------
    # Ownership Check
    # -------------------------

    if university["organisation_id"] != organisation_id:

        cursor.close()

        db.close()

        return "Access denied.", 403


    # -------------------------
    # Archived Check
    # -------------------------

    if university["status"] == "Archived":

        cursor.close()

        db.close()

        return "Archived universities cannot be edited.", 400


    # -------------------------
    # GET
    # -------------------------

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "organisation_university_edit.html",
            university=university
        )


    # -------------------------
    # POST
    # -------------------------

    university_name = request.form.get(
        "university_name",
        ""
    ).strip()


    country = request.form.get(
        "country",
        ""
    ).strip()


    city = request.form.get(
        "city",
        ""
    ).strip()


    university_type = request.form.get(
        "university_type",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    admissions_website = request.form.get(
        "admissions_website",
        ""
    ).strip()


    international_students_info = request.form.get(
        "international_students_info",
        ""
    ).strip()


    additional_notes = request.form.get(
        "additional_notes",
        ""
    ).strip()


    action = request.form.get(
        "action",
        "save"
    )


    # -------------------------
    # Validation
    # -------------------------

    if (
        not university_name
        or not country
        or not city
        or not university_type
        or not description
    ):

        cursor.close()

        db.close()

        return render_template(
            "organisation_university_edit.html",
            university=university,
            error="University name, country, city, university type and description are required.",
            form_data=request.form
        )


    # -------------------------
    # Determine Status
    # -------------------------

    if university["status"] == "Draft":

        if action == "submit":

            status = "Pending"

        else:

            status = "Draft"


    elif university["status"] == "Pending":

        status = "Pending"


    elif university["status"] == "Rejected":

        if action == "submit":

            status = "Pending"

        else:

            status = "Rejected"


    else:

        # Published university edited by Organisation
        # must return to Admin review.

        status = "Pending"


    # -------------------------
    # Update University
    # -------------------------

    query = """
        UPDATE universities

        SET
            university_name = %s,
            country = %s,
            city = %s,
            university_type = %s,
            description = %s,
            official_website = NULLIF(%s, ''),
            admissions_website = NULLIF(%s, ''),
            international_students_info = NULLIF(%s, ''),
            additional_notes = NULLIF(%s, ''),
            status = %s,

            submitted_at =
                CASE
                    WHEN %s = 'Pending'
                    THEN CURRENT_TIMESTAMP
                    ELSE submitted_at
                END,

            reviewed_at = NULL,
            reviewed_by = NULL,
            review_reason = NULL

        WHERE
            university_id = %s
            AND organisation_id = %s
    """


    cursor.execute(
        query,
        (
            university_name,
            country,
            city,
            university_type,
            description,
            official_website,
            admissions_website,
            international_students_info,
            additional_notes,
            status,
            status,
            university_id,
            organisation_id
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect(
        "/organisation/universities"
    )


# -------------------------
# ADMIN LOGIN
# -------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "GET":

        return render_template("admin_login.html")


    email_or_username = request.form["email"].strip()

    password = request.form["password"]


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            user_id,
            username,
            password_hash,
            role
        FROM users
        WHERE (email = %s OR username = %s)
        AND role = 'Admin'
    """


    cursor.execute(
        query,
        (
            email_or_username,
            email_or_username
        )
    )


    admin = cursor.fetchone()


    cursor.close()

    db.close()


    if (admin and check_password_hash(admin["password_hash"], password)):

        session["user_id"] = admin["user_id"]

        session["username"] = admin["username"]

        session["role"] = admin["role"]

        return redirect("/admin/dashboard")


    return render_template(
    "admin_login.html",
    error="Incorrect email/username or password."
)



# -------------------------
# ORGANISATION PROFILE
# -------------------------

@app.route("/organisation/profile")
def organisation_profile():

    if "user_id" not in session:

        return redirect("/login")


    if session.get("role") != "Organisation":

        return "Access denied.", 403


    organisation_id = session.get(
        "organisation_id"
    )


    if not organisation_id:

        return "Organisation account is not linked to an organisation.", 400


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            organisation_id,
            organisation_name,
            description,
            website,
            contact_email,
            organisation_type,
            status
        FROM organisations
        WHERE organisation_id = %s
    """


    cursor.execute(
        query,
        (organisation_id,)
    )


    organisation = cursor.fetchone()


    cursor.close()

    db.close()


    if not organisation:

        return "Organisation not found.", 404


    return render_template(
        "organisation_profile.html",
        organisation=organisation
    )


# -------------------------
# ADMIN DASHBOARD
# -------------------------

@app.route("/admin/dashboard")
def admin_dashboard():

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):
        return redirect("/admin/login")

    db = connect_db()
    cursor = db.cursor(dictionary=True)


    query = """
        SELECT COUNT(*) AS count
        FROM organisations
        WHERE status = 'Pending'
    """

    cursor.execute(query)

    pending_organisations = cursor.fetchone()["count"]


    query = """
        SELECT COUNT(*) AS count
        FROM opportunities
        WHERE status = 'Pending'
    """

    cursor.execute(query)

    pending_opportunities = cursor.fetchone()["count"]


    query = """
        SELECT COUNT(*) AS count
        FROM resources
        WHERE status = 'Pending'
    """

    cursor.execute(query)

    pending_resources = cursor.fetchone()["count"]


    query = """
        SELECT COUNT(*) AS count
        FROM universities
        WHERE status = 'Pending'
    """

    cursor.execute(query)

    pending_universities = cursor.fetchone()["count"]


    query = """
        SELECT COUNT(*) AS count
        FROM reports
        WHERE status = 'Pending'
    """

    cursor.execute(query)

    pending_reports = cursor.fetchone()["count"]


    cursor.close()
    db.close()


    return render_template(
        "admin_dashboard.html",
        pending_organisations=pending_organisations,
        pending_opportunities=pending_opportunities,
        pending_resources=pending_resources,
        pending_universities=pending_universities,
        pending_reports=pending_reports
    )

# -------------------------
# ADMIN ORGANISATION APPLICATIONS
# -------------------------

@app.route("/admin/organisations")
def admin_organisations():

    if "user_id" not in session or session.get("role") != "Admin":

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            oa.application_id,
            oa.organisation_id,
            oa.status,
            oa.submitted_at,
            o.organisation_name,
            o.organisation_type,
            o.contact_email
        FROM organisation_applications oa
        JOIN organisations o
            ON oa.organisation_id = o.organisation_id
        WHERE oa.status = 'Pending'
        ORDER BY oa.submitted_at ASC
    """


    cursor.execute(query)


    applications = cursor.fetchall()


    cursor.close()

    db.close()


    return render_template(
        "admin_organisations.html",
        applications=applications
    )


# -------------------------
# ADMIN VERIFIED ORGANISATIONS
# -------------------------

@app.route("/admin/organisations/verified")
def admin_verified_organisations():

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            organisation_id,
            organisation_name,
            organisation_type,
            description,
            website,
            contact_email,
            status
        FROM organisations
        WHERE status = 'Verified'
        ORDER BY organisation_name ASC
    """


    cursor.execute(query)


    organisations = cursor.fetchall()


    cursor.close()

    db.close()


    return render_template(
        "admin_organisations_verified.html",
        organisations=organisations
    )

# -------------------------
# OPPORTUNITIES
# -------------------------

@app.route("/opportunities")
def opportunities():

    # -------------------------
    # ADMIN
    # -------------------------

    if session.get("role") == "Admin":

        return redirect(
            "/admin/opportunities"
        )


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    role = session.get("role")

    organisation_id = session.get(
        "organisation_id"
    )


    # -------------------------
    # PUBLIC / STUDENT
    # -------------------------

    if role != "Organisation":

        query = """
            SELECT
                o.opportunity_id,
                o.opportunity_name,
                o.category,
                o.description,
                o.eligibility,
                o.deadline,
                o.official_website,
                o.status,
                o.organisation_id,
                org.organisation_name
            FROM opportunities o
            LEFT JOIN organisations org
                ON o.organisation_id = org.organisation_id
            WHERE o.status = 'Published'
            ORDER BY o.created_at DESC
        """

        cursor.execute(query)


    # -------------------------
    # ORGANISATION
    # -------------------------

    else:

        query = """
            SELECT
                o.opportunity_id,
                o.opportunity_name,
                o.category,
                o.description,
                o.eligibility,
                o.deadline,
                o.official_website,
                o.status,
                o.organisation_id,
                org.organisation_name
            FROM opportunities o
            LEFT JOIN organisations org
                ON o.organisation_id = org.organisation_id
            WHERE
                o.status = 'Published'
                OR (
                    o.organisation_id = %s
                    AND o.status != 'Archived'
                )
            ORDER BY o.created_at DESC
        """

        cursor.execute(
            query,
            (
                organisation_id,
            )
        )


    opportunities = cursor.fetchall()


    # ---------------------------------------------------------
    # CHECK SAVED OPPORTUNITIES
    # ---------------------------------------------------------

    if role == "Student":

        for opportunity in opportunities:

            cursor.execute(
                """
                SELECT
                    user_id
                FROM saved_opportunities
                WHERE
                    user_id = %s
                    AND opportunity_id = %s
                LIMIT 1
                """,
                (
                    session["user_id"],
                    opportunity["opportunity_id"]
                )
            )

            opportunity["is_saved"] = (
                cursor.fetchone() is not None
            )

    else:

        for opportunity in opportunities:

            opportunity["is_saved"] = False


    cursor.close()

    db.close()


    return render_template(
        "opportunities.html",
        opportunities=opportunities,
        role=role,
        organisation_id=organisation_id
    )


# -------------------------
# ADD OPPORTUNITY
# -------------------------

@app.route("/organisation/opportunities/add", methods=["GET", "POST"])
def add_opportunity():

    # Must be logged in

    if "user_id" not in session:

        return redirect("/login")


    # Only Organisations can add opportunities

    if session.get("role") != "Organisation":

        return redirect("/opportunities")


    organisation_id = session.get("organisation_id")


    # Organisation ID must exist

    if not organisation_id:

        return redirect("/opportunities")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # Check that the organisation is verified

    cursor.execute(
        """
        SELECT
            organisation_id,
            organisation_name,
            status
        FROM organisations
        WHERE organisation_id = %s
        """,
        (organisation_id,)
    )


    organisation = cursor.fetchone()


    if not organisation or organisation["status"] != "Verified":

        cursor.close()

        db.close()

        return redirect("/opportunities")


    # -------------------------
    # GET
    # -------------------------

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "organisation_opportunity_add.html",
            organisation=organisation
        )


    # -------------------------
    # POST
    # -------------------------

    opportunity_name = request.form.get(
        "opportunity_name",
        ""
    ).strip()


    category = request.form.get(
        "category",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    eligibility = request.form.get(
        "eligibility",
        ""
    ).strip()


    deadline = request.form.get(
        "deadline",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    action = request.form.get(
        "action"
    )


    # Basic validation

    if not opportunity_name or not category or not description:

        cursor.close()

        db.close()

        return render_template(
            "organisation_opportunity_add.html",
            organisation=organisation,
            error="Opportunity name, category and description are required.",
            form_data=request.form
        )


    # Determine status

    if action == "submit":

        status = "Pending"

    else:

        status = "Draft"


    # Submitted timestamp only when sent for review

    submitted_at = None

    if status == "Pending":

        submitted_at = True


    # Insert opportunity

    query = """
        INSERT INTO opportunities
        (
            organisation_id,
            opportunity_name,
            category,
            description,
            eligibility,
            deadline,
            official_website,
            status,
            submitted_at
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            NULLIF(%s, ''),
            NULLIF(%s, ''),
            %s,
            CASE
                WHEN %s = 'Pending'
                THEN CURRENT_TIMESTAMP
                ELSE NULL
            END
        )
    """


    cursor.execute(
        query,
        (
            organisation_id,
            opportunity_name,
            category,
            description,
            eligibility,
            deadline,
            official_website,
            status,
            status
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect("/opportunities")

# -------------------------
# EDIT OPPORTUNITY
# -------------------------

@app.route(
    "/organisation/opportunities/<int:opportunity_id>/edit",
    methods=["GET", "POST"]
)
def edit_opportunity(opportunity_id):

    # Must be logged in

    if "user_id" not in session:

        return redirect("/login")


    # Only Organisations can edit here

    if session.get("role") != "Organisation":

        return redirect("/opportunities")


    organisation_id = session.get("organisation_id")


    if not organisation_id:

        return redirect("/opportunities")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Get Opportunity
    # -------------------------

    cursor.execute(
        """
        SELECT
            opportunity_id,
            organisation_id,
            opportunity_name,
            category,
            description,
            eligibility,
            deadline,
            official_website,
            status
        FROM opportunities
        WHERE opportunity_id = %s
        """,
        (opportunity_id,)
    )


    opportunity = cursor.fetchone()


    # Opportunity doesn't exist

    if not opportunity:

        cursor.close()

        db.close()

        return redirect("/opportunities")


    # -------------------------
    # Ownership Check
    # -------------------------

    if opportunity["organisation_id"] != organisation_id:

        cursor.close()

        db.close()

        return redirect("/opportunities")


    # Archived opportunities cannot be edited

    if opportunity["status"] == "Archived":

        cursor.close()

        db.close()

        return redirect("/opportunities")


    # -------------------------
    # GET
    # -------------------------

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "organisation_opportunity_edit.html",
            opportunity=opportunity
        )


    # -------------------------
    # POST
    # -------------------------

    opportunity_name = request.form.get(
        "opportunity_name",
        ""
    ).strip()


    category = request.form.get(
        "category",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    eligibility = request.form.get(
        "eligibility",
        ""
    ).strip()


    deadline = request.form.get(
        "deadline",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    action = request.form.get("action")


    # -------------------------
    # Validation
    # -------------------------

    if not opportunity_name or not category or not description:

        cursor.close()

        db.close()

        return render_template(
            "organisation_opportunity_edit.html",
            opportunity=opportunity,
            error="Opportunity name, category and description are required.",
            form_data=request.form
        )


    # -------------------------
    # Determine Status
    # -------------------------

    current_status = opportunity["status"]


    if current_status == "Draft":

        if action == "submit":

            status = "Pending"

        else:

            status = "Draft"


    elif current_status == "Pending":

        # It is already awaiting review

        status = "Pending"


    else:

        # Published content has been changed.
        # It must return to Admin review.

        status = "Pending"


    # -------------------------
    # Update Opportunity
    # -------------------------

    query = """
        UPDATE opportunities

        SET
            opportunity_name = %s,
            category = %s,
            description = %s,
            eligibility = %s,
            deadline = NULLIF(%s, ''),
            official_website = NULLIF(%s, ''),
            status = %s,

            submitted_at =
                CASE
                    WHEN %s = 'Pending'
                    THEN CURRENT_TIMESTAMP
                    ELSE submitted_at
                END,

            reviewed_at = NULL,
            reviewed_by = NULL,
            review_reason = NULL

        WHERE
            opportunity_id = %s
            AND organisation_id = %s
    """


    cursor.execute(
        query,
        (
            opportunity_name,
            category,
            description,
            eligibility,
            deadline,
            official_website,
            status,
            status,
            opportunity_id,
            organisation_id
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect("/opportunities")


# -------------------------
# EDIT ORGANISATION PROFILE
# -------------------------

@app.route("/organisation/profile/edit", methods=["GET", "POST"])
def edit_organisation_profile():

    # Must be logged in

    if "user_id" not in session:

        return redirect("/login")


    # Only Organisations can edit their profile

    if session.get("role") != "Organisation":

        return redirect("/opportunities")


    organisation_id = session.get("organisation_id")


    if not organisation_id:

        return redirect("/opportunities")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # Get Organisation

    cursor.execute(
        """
        SELECT
            organisation_id,
            organisation_name,
            description,
            website,
            contact_email,
            organisation_type,
            status
        FROM organisations
        WHERE organisation_id = %s
        """,
        (organisation_id,)
    )


    organisation = cursor.fetchone()


    if not organisation:

        cursor.close()

        db.close()

        return redirect("/opportunities")


    # Only verified organisations can edit their profile

    if organisation["status"] != "Verified":

        cursor.close()

        db.close()

        return redirect("/organisation/profile")


    # -------------------------
    # GET
    # -------------------------

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "organisation_edit.html",
            organisation=organisation
        )


    # -------------------------
    # POST
    # -------------------------

    organisation_name = request.form.get(
        "organisation_name",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    website = request.form.get(
        "website",
        ""
    ).strip()


    contact_email = request.form.get(
        "contact_email",
        ""
    ).strip()


    organisation_type = request.form.get(
        "organisation_type",
        ""
    ).strip()


    # Basic validation

    if not organisation_name or not contact_email:

        cursor.close()

        db.close()

        return render_template(
            "organisation_edit.html",
            organisation=organisation,
            error="Organisation name and contact email are required.",
            form_data=request.form
        )


    # Update Organisation

    cursor.execute(
        """
        UPDATE organisations

        SET
            organisation_name = %s,
            description = %s,
            website = NULLIF(%s, ''),
            contact_email = %s,
            organisation_type = NULLIF(%s, '')

        WHERE organisation_id = %s
        """,
        (
            organisation_name,
            description,
            website,
            contact_email,
            organisation_type,
            organisation_id
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect("/organisation/profile")


# =========================
# DELETE ORGANISATION
# =========================

@app.route("/organisation/profile/delete", methods=["GET", "POST"])
def organisation_delete():

    if "user_id" not in session:
        return redirect("/login")


    if session.get("role") != "Organisation":
        return redirect("/")


    organisation_id = session.get("organisation_id")


    if not organisation_id:
        return redirect("/")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # =========================
    # GET ORGANISATION
    # =========================

    cursor.execute(
        """
        SELECT
            organisation_id,
            organisation_name,
            status
        FROM organisations
        WHERE organisation_id = %s
        """,
        (organisation_id,)
    )


    organisation = cursor.fetchone()


    if not organisation:

        cursor.close()

        db.close()

        return redirect("/")


    # =========================
    # SHOW DELETE PAGE
    # =========================

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "delete_profile.html",
            organisation=organisation
        )


    # =========================
    # CLOSE ORGANISATION
    # =========================

    try:

        # Archive organisation opportunities

        cursor.execute(
            """
            UPDATE opportunities
            SET status = 'Archived'
            WHERE organisation_id = %s
            """,
            (organisation_id,)
        )


        # Scrub organisation information

        cursor.execute(
            """
            UPDATE organisations
            SET
                organisation_name = %s,
                description = NULL,
                website = NULL,
                contact_email = NULL,
                organisation_type = NULL,
                status = 'Deleted'
            WHERE organisation_id = %s
            """,
            (
                "Deleted Organisation",
                organisation_id
            )
        )


        db.commit()


        # End organisation session

        session.clear()


        cursor.close()

        db.close()


        return redirect("/")


    except Exception as error:

        db.rollback()

        cursor.close()

        db.close()


        return render_template(
            "delete_profile.html",
            organisation=organisation,
            error="Could not close the organisation. Please try again."
        )


# -------------------------
# ADMIN OPPORTUNITY REVIEW
# -------------------------

@app.route(
    "/admin/opportunities/<int:opportunity_id>"
)
def admin_opportunity_view(opportunity_id):

    # Only Admins can review opportunities

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Get Opportunity
    # -------------------------

    query = """
        SELECT
            o.opportunity_id,
            o.opportunity_name,
            o.category,
            o.description,
            o.eligibility,
            o.deadline,
            o.official_website,
            o.status,
            o.organisation_id,
            o.review_reason,
            org.organisation_name
        FROM opportunities o
        LEFT JOIN organisations org
            ON o.organisation_id = org.organisation_id
        WHERE o.opportunity_id = %s
    """


    cursor.execute(
        query,
        (opportunity_id,)
    )


    opportunity = cursor.fetchone()


    cursor.close()

    db.close()


    # Opportunity doesn't exist

    if not opportunity:

        return "Opportunity not found.", 404


    return render_template(
        "admin_opportunity_view.html",
        opportunity=opportunity
    )

# -------------------------
# ADMIN OPPORTUNITY MANAGEMENT
# -------------------------

@app.route("/admin/opportunities")
def admin_opportunities():

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    # Get requested status filter

    status = request.args.get(
        "status"
    )


    # Archived has its own page

    if status == "Archived":

        return redirect(
            "/admin/opportunities/archived"
        )


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Base Query
    # -------------------------

    query = """
        SELECT
            o.opportunity_id,
            o.opportunity_name,
            o.category,
            o.description,
            o.eligibility,
            o.deadline,
            o.official_website,
            o.status,
            o.organisation_id,
            org.organisation_name
        FROM opportunities o
        LEFT JOIN organisations org
            ON o.organisation_id = org.organisation_id
    """


    # -------------------------
    # Status Filter
    # -------------------------

    if status in [
        "Pending",
        "Published",
        "Rejected"
    ]:

        query += """
            WHERE o.status = %s
        """

        query += """
            ORDER BY o.created_at DESC
        """

        cursor.execute(
            query,
            (status,)
        )


    else:

        query += """
            ORDER BY o.created_at DESC
        """

        cursor.execute(
            query
        )


    opportunities = cursor.fetchall()


    cursor.close()

    db.close()


    return render_template(
        "admin_opportunities.html",
        opportunities=opportunities,
        current_status=status
    )


# -------------------------
# ADMIN ADD OPPORTUNITY
# -------------------------

@app.route(
    "/admin/opportunities/add",
    methods=["GET", "POST"]
)
def admin_add_opportunity():

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Get Organisations
    # -------------------------

    query = """
        SELECT
            organisation_id,
            organisation_name,
            organisation_type,
            status
        FROM organisations
        WHERE status = 'Verified'
        ORDER BY organisation_name ASC
    """


    cursor.execute(query)


    organisations = cursor.fetchall()


    # -------------------------
    # GET
    # -------------------------

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "admin_opportunity_add.html",
            organisations=organisations
        )


    # -------------------------
    # POST
    # -------------------------

    organisation_id = request.form.get(
        "organisation_id"
    )


    opportunity_name = request.form.get(
        "opportunity_name",
        ""
    ).strip()


    category = request.form.get(
        "category",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    eligibility = request.form.get(
        "eligibility",
        ""
    ).strip()


    deadline = request.form.get(
        "deadline",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    status = request.form.get(
        "status",
        "Draft"
    ).strip()


    # -------------------------
    # Validation
    # -------------------------

    if (
        not organisation_id
        or not opportunity_name
        or not category
        or not description
    ):

        cursor.close()

        db.close()

        return render_template(
            "admin_opportunity_add.html",
            organisations=organisations,
            error="Organisation, opportunity name, category and description are required.",
            form_data=request.form
        )


    # -------------------------
    # Validate Organisation
    # -------------------------

    cursor.execute(
        """
        SELECT
            organisation_id
        FROM organisations
        WHERE
            organisation_id = %s
            AND status = 'Verified'
        """,
        (
            organisation_id,
        )
    )


    organisation = cursor.fetchone()


    if not organisation:

        cursor.close()

        db.close()

        return render_template(
            "admin_opportunity_add.html",
            organisations=organisations,
            error="Please select a valid verified organisation.",
            form_data=request.form
        )


    # -------------------------
    # Validate Status
    # -------------------------

    if status not in [
        "Draft",
        "Pending",
        "Published"
    ]:

        status = "Draft"


    # -------------------------
    # Insert Opportunity
    # -------------------------

    query = """
        INSERT INTO opportunities
        (
            organisation_id,
            opportunity_name,
            category,
            description,
            eligibility,
            deadline,
            official_website,
            status,
            submitted_at,
            reviewed_at,
            reviewed_by,
            review_reason
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            NULLIF(%s, ''),
            NULLIF(%s, ''),
            %s,
            CASE
                WHEN %s = 'Pending'
                THEN CURRENT_TIMESTAMP
                ELSE NULL
            END,
            CASE
                WHEN %s = 'Published'
                THEN CURRENT_TIMESTAMP
                ELSE NULL
            END,
            CASE
                WHEN %s = 'Published'
                THEN %s
                ELSE NULL
            END,
            CASE
                WHEN %s = 'Published'
                THEN 'Created by Admin.'
                ELSE NULL
            END
        )
    """


    cursor.execute(
        query,
        (
            organisation_id,
            opportunity_name,
            category,
            description,
            eligibility,
            deadline,
            official_website,
            status,
            status,
            status,
            status,
            session["user_id"],
            status
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect(
        "/admin/opportunities"
    )


# -------------------------
# EDIT OPPORTUNITY AS ADMIN
# -------------------------

@app.route(
    "/admin/opportunities/<int:opportunity_id>/edit",
    methods=["GET", "POST"]
)
def admin_edit_opportunity(opportunity_id):

    # Only Admins can edit opportunities here

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Get Opportunity
    # -------------------------

    query = """
        SELECT
            opportunity_id,
            opportunity_name,
            category,
            description,
            eligibility,
            deadline,
            official_website,
            status,
            organisation_id
        FROM opportunities
        WHERE opportunity_id = %s
    """


    cursor.execute(
        query,
        (opportunity_id,)
    )


    opportunity = cursor.fetchone()


    if not opportunity:

        cursor.close()

        db.close()

        return "Opportunity not found.", 404


    # -------------------------
    # OPEN EDIT PAGE
    # -------------------------

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "admin_opportunity_edit.html",
            opportunity=opportunity
        )


    # -------------------------
    # GET UPDATED INFORMATION
    # -------------------------

    opportunity_name = request.form.get(
        "opportunity_name",
        ""
    ).strip()


    category = request.form.get(
        "category",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    eligibility = request.form.get(
        "eligibility",
        ""
    ).strip()


    deadline = request.form.get(
        "deadline",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    # -------------------------
    # VALIDATION
    # -------------------------

    if (
        not opportunity_name
        or not category
        or not description
    ):

        cursor.close()

        db.close()

        return render_template(
            "admin_opportunity_edit.html",
            opportunity=opportunity,
            error="Opportunity name, category and description are required.",
            form_data=request.form
        )


    # -------------------------
    # UPDATE OPPORTUNITY
    # -------------------------

    query = """
        UPDATE opportunities

        SET
            opportunity_name = %s,
            category = %s,
            description = %s,
            eligibility = %s,
            deadline = NULLIF(%s, ''),
            official_website = NULLIF(%s, '')

        WHERE opportunity_id = %s
    """


    cursor.execute(
        query,
        (
            opportunity_name,
            category,
            description,
            eligibility,
            deadline,
            official_website,
            opportunity_id
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect(
        "/admin/opportunities"
    )


# -------------------------
# APPROVE OPPORTUNITY
# -------------------------

@app.route(
    "/admin/opportunities/<int:opportunity_id>/approve",
    methods=["POST"]
)
def approve_opportunity(opportunity_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            opportunity_id,
            status
        FROM opportunities
        WHERE opportunity_id = %s
    """


    cursor.execute(
        query,
        (opportunity_id,)
    )


    opportunity = cursor.fetchone()


    if not opportunity:

        cursor.close()

        db.close()

        return "Opportunity not found.", 404


    if opportunity["status"] != "Pending":

        cursor.close()

        db.close()

        return "This opportunity has already been reviewed.", 400


    query = """
        UPDATE opportunities
        SET
            status = 'Published',
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = %s,
            review_reason = %s
        WHERE opportunity_id = %s
    """


    cursor.execute(
        query,
        (
            session["user_id"],
            "Opportunity approved.",
            opportunity_id
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect("/admin/opportunities")


# -------------------------
# REJECT OPPORTUNITY
# -------------------------

@app.route(
    "/admin/opportunities/<int:opportunity_id>/reject",
    methods=["POST"]
)
def reject_opportunity(opportunity_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            opportunity_id,
            status
        FROM opportunities
        WHERE opportunity_id = %s
    """


    cursor.execute(
        query,
        (opportunity_id,)
    )


    opportunity = cursor.fetchone()


    if not opportunity:

        cursor.close()

        db.close()

        return "Opportunity not found.", 404


    if opportunity["status"] != "Pending":

        cursor.close()

        db.close()

        return "This opportunity has already been reviewed.", 400


    query = """
        UPDATE opportunities
        SET
            status = 'Rejected',
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = %s,
            review_reason = %s
        WHERE opportunity_id = %s
    """


    cursor.execute(
        query,
        (
            session["user_id"],
            "Opportunity rejected.",
            opportunity_id
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect("/admin/opportunities")


# -------------------------
# ARCHIVE OPPORTUNITY
# -------------------------

@app.route(
    "/admin/opportunities/<int:opportunity_id>/archive",
    methods=["POST"]
)
def archive_opportunity(opportunity_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            opportunity_id,
            status
        FROM opportunities
        WHERE opportunity_id = %s
    """


    cursor.execute(
        query,
        (opportunity_id,)
    )


    opportunity = cursor.fetchone()


    if not opportunity:

        cursor.close()

        db.close()

        return "Opportunity not found.", 404


    query = """
        UPDATE opportunities
        SET
            status = 'Archived',
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = %s,
            review_reason = %s
        WHERE opportunity_id = %s
    """


    cursor.execute(
        query,
        (
            session["user_id"],
            "Opportunity archived.",
            opportunity_id
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect("/admin/opportunities")


@app.route("/admin/opportunities/archived")
def admin_archived_opportunities():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "Admin":
        return redirect("/")

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            o.*,
            org.organisation_name
        FROM opportunities o
        LEFT JOIN organisations org
            ON o.organisation_id = org.organisation_id
        WHERE o.status = 'Archived'
        ORDER BY o.updated_at DESC
    """

    cursor.execute(query)

    opportunities = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admin_opportunities_archived.html",
        opportunities=opportunities
    )


# -------------------------
# UNARCHIVE OPPORTUNITY
# -------------------------

@app.route(
    "/admin/opportunities/<int:opportunity_id>/unarchive",
    methods=["POST"]
)
def unarchive_opportunity(opportunity_id):

    # Only Admins can unarchive opportunities

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Find Opportunity
    # -------------------------

    query = """
        SELECT
            opportunity_id,
            status
        FROM opportunities
        WHERE opportunity_id = %s
    """


    cursor.execute(
        query,
        (opportunity_id,)
    )


    opportunity = cursor.fetchone()


    if not opportunity:

        cursor.close()

        db.close()

        return "Opportunity not found.", 404


    # -------------------------
    # Only Archived Opportunities
    # can be unarchived
    # -------------------------

    if opportunity["status"] != "Archived":

        cursor.close()

        db.close()

        return "This opportunity is not archived.", 400


    # -------------------------
    # Return to Pending
    # -------------------------

    query = """
        UPDATE opportunities
        SET
            status = 'Pending',
            submitted_at = CURRENT_TIMESTAMP,
            reviewed_at = NULL,
            reviewed_by = NULL,
            review_reason = NULL
        WHERE opportunity_id = %s
        AND status = 'Archived'
    """


    cursor.execute(
        query,
        (opportunity_id,)
    )


    db.commit()


    cursor.close()

    db.close()


    # Return to Admin Opportunity Management

    return redirect(
        "/admin/opportunities"
    )


# -------------------------
# ADMIN ADD RESOURCE
# -------------------------

@app.route(
    "/admin/resources/add",
    methods=["GET", "POST"]
)
def admin_add_resource():

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Get Organisations
    # -------------------------

    cursor.execute(
        """
        SELECT
            organisation_id,
            organisation_name,
            organisation_type,
            status
        FROM organisations
        WHERE status = 'Verified'
        ORDER BY organisation_name ASC
        """
    )


    organisations = cursor.fetchall()


    # -------------------------
    # GET
    # -------------------------

    if request.method == "GET":

        cursor.close()

        db.close()

        return render_template(
            "admin_resource_add.html",
            organisations=organisations
        )


    # -------------------------
    # POST
    # -------------------------

    organisation_id = request.form.get(
        "organisation_id"
    )


    resource_name = request.form.get(
        "resource_name",
        ""
    ).strip()


    resource_type = request.form.get(
        "resource_type",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    recommended_for = request.form.get(
        "recommended_for",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    status = request.form.get(
        "status",
        "Draft"
    ).strip()


    is_featured = request.form.get(
        "is_featured"
    ) == "1"


    # -------------------------
    # Validation
    # -------------------------

    if (
        not organisation_id
        or not resource_name
        or not resource_type
        or not description
    ):

        cursor.close()

        db.close()

        return render_template(
            "admin_resource_add.html",
            organisations=organisations,
            error="Organisation, resource name, resource type and description are required.",
            form_data=request.form
        )


    # -------------------------
    # Validate Organisation
    # -------------------------

    cursor.execute(
        """
        SELECT
            organisation_id
        FROM organisations
        WHERE
            organisation_id = %s
            AND status = 'Verified'
        """,
        (
            organisation_id,
        )
    )


    organisation = cursor.fetchone()


    if not organisation:

        cursor.close()

        db.close()

        return render_template(
            "admin_resource_add.html",
            organisations=organisations,
            error="Please select a valid verified organisation.",
            form_data=request.form
        )


    # -------------------------
    # Validate Status
    # -------------------------

    if status not in [
        "Draft",
        "Pending",
        "Published",
        "Rejected"
    ]:

        status = "Draft"


    # -------------------------
    # Featured Validation
    # -------------------------

    if status != "Published":

        is_featured = False


    # -------------------------
    # Insert Resource
    # -------------------------

    query = """
        INSERT INTO resources
        (
            organisation_id,
            resource_name,
            resource_type,
            description,
            recommended_for,
            official_website,
            status,
            is_featured
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            NULLIF(%s, ''),
            NULLIF(%s, ''),
            %s,
            %s
        )
    """


    cursor.execute(
        query,
        (
            organisation_id,
            resource_name,
            resource_type,
            description,
            recommended_for,
            official_website,
            status,
            is_featured
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect(
        "/admin/resources"
    )


# -------------------------
# ADMIN RESOURCE MANAGEMENT
# -------------------------

@app.route("/admin/resources")
def admin_resources():

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    status = request.args.get(
        "status"
    )


    # Archived resources have their own page

    if status == "Archived":

        return redirect(
            "/admin/resources/archived"
        )


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Base Query
    # -------------------------

    query = """
        SELECT
            r.resource_id,
            r.resource_name,
            r.resource_type,
            r.description,
            r.recommended_for,
            r.official_website,
            r.status,
            r.organisation_id,
            r.is_featured,
            r.submitted_at,
            r.reviewed_at,
            r.reviewed_by,
            r.review_reason,
            r.created_at,
            r.updated_at,
            org.organisation_name
        FROM resources r
        LEFT JOIN organisations org
            ON r.organisation_id = org.organisation_id
    """


    # -------------------------
    # Status Filter
    # -------------------------

    if status in [
        "Pending",
        "Published",
        "Rejected",
        "Draft"
    ]:

        query += """
            WHERE r.status = %s
        """

        query += """
            ORDER BY r.created_at DESC
        """

        cursor.execute(
            query,
            (
                status,
            )
        )


    else:

        query += """
            WHERE r.status != 'Archived'
            ORDER BY r.created_at DESC
        """

        cursor.execute(query)


    resources = cursor.fetchall()


    cursor.close()

    db.close()


    return render_template(
        "admin_resources.html",
        resources=resources,
        current_status=status
    )


# -------------------------
# ADMIN RESOURCE REVIEW
# -------------------------

@app.route(
    "/admin/resources/<int:resource_id>"
)
def admin_resource_view(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            r.resource_id,
            r.resource_name,
            r.resource_type,
            r.description,
            r.recommended_for,
            r.official_website,
            r.status,
            r.organisation_id,
            r.is_featured,
            r.submitted_at,
            r.reviewed_at,
            r.reviewed_by,
            r.review_reason,
            r.created_at,
            r.updated_at,
            org.organisation_name
        FROM resources r
        LEFT JOIN organisations org
            ON r.organisation_id = org.organisation_id
        WHERE r.resource_id = %s
    """


    cursor.execute(
        query,
        (resource_id,)
    )


    resource = cursor.fetchone()


    cursor.close()

    db.close()


    if not resource:

        return "Resource not found.", 404


    return render_template(
        "admin_resource_view.html",
        resource=resource
    )


@app.route("/resources")
def resources():

    if session.get("role") == "Admin":

        return redirect(
            "/admin/resources"
        )


    db = connect_db()
    cursor = db.cursor(dictionary=True)


    role = session.get("role")

    organisation_id = session.get(
        "organisation_id"
    )


    resource_type = request.args.get(
        "type"
    )


    # =========================
    # PUBLIC RESOURCE QUERY
    # =========================

    if resource_type:

        query = """
            SELECT
                r.resource_id,
                r.resource_name,
                r.resource_type,
                r.description,
                r.recommended_for,
                r.official_website,
                r.status,
                r.organisation_id,
                r.is_featured,
                org.organisation_name
            FROM resources r
            LEFT JOIN organisations org
                ON r.organisation_id = org.organisation_id
            WHERE
                r.status = 'Published'
                AND r.resource_type = %s
            ORDER BY r.created_at DESC
        """

        cursor.execute(
            query,
            (
                resource_type,
            )
        )

        featured_resources = cursor.fetchall()


    else:

        query = """
            SELECT
                r.resource_id,
                r.resource_name,
                r.resource_type,
                r.description,
                r.recommended_for,
                r.official_website,
                r.status,
                r.organisation_id,
                r.is_featured,
                org.organisation_name
            FROM resources r
            LEFT JOIN organisations org
                ON r.organisation_id = org.organisation_id
            WHERE
                r.status = 'Published'
                AND r.is_featured = TRUE
            ORDER BY r.created_at DESC
        """

        cursor.execute(query)

        featured_resources = cursor.fetchall()


    # =========================
    # ORGANISATION RESOURCES
    # =========================

    organisation_resources = []


    if role == "Organisation":

        query = """
            SELECT
                r.resource_id,
                r.resource_name,
                r.resource_type,
                r.description,
                r.recommended_for,
                r.official_website,
                r.status,
                r.organisation_id,
                r.is_featured,
                org.organisation_name
            FROM resources r
            LEFT JOIN organisations org
                ON r.organisation_id = org.organisation_id
            WHERE
                r.organisation_id = %s
                AND r.status != 'Archived'
        """

        parameters = [
            organisation_id
        ]


        if resource_type:

            query += """
                AND r.resource_type = %s
            """

            parameters.append(
                resource_type
            )


        query += """
            ORDER BY r.created_at DESC
        """


        cursor.execute(
            query,
            parameters
        )


        organisation_resources = cursor.fetchall()


    # ---------------------------------------------------------
    # CHECK SAVED RESOURCES
    # ---------------------------------------------------------

    if role == "Student":

        for resource in featured_resources:

            cursor.execute(
                """
                SELECT
                    user_id
                FROM saved_resources
                WHERE
                    user_id = %s
                    AND resource_id = %s
                """,
                (
                    session["user_id"],
                    resource["resource_id"]
                )
            )

            resource["is_saved"] = (
                cursor.fetchone() is not None
            )

    else:

        for resource in featured_resources:

            resource["is_saved"] = False

    cursor.close()
    db.close()


    return render_template(
        "resources.html",
        featured_resources=featured_resources,
        organisation_resources=organisation_resources,
        role=role,
        organisation_id=organisation_id,
        resource_type=resource_type
    )

@app.route(
    "/resources/<int:resource_id>/unsave",
    methods=["POST"]
)
def unsave_resource(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Student"
    ):
        return redirect("/login")

    user_id = session["user_id"]

    db = connect_db()
    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM saved_resources
        WHERE
            user_id = %s
            AND resource_id = %s
        """,
        (
            user_id,
            resource_id
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect("/resources")


@app.route(
    "/organisation/resources/add",
    methods=["GET", "POST"]
)
def organisation_add_resource():

    if (
        "user_id" not in session
        or session.get("role") != "Organisation"
    ):
        return redirect("/login")


    organisation_id = session.get(
        "organisation_id"
    )


    if not organisation_id:
        return redirect("/")


    db = connect_db()
    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            organisation_id,
            organisation_name,
            status
        FROM organisations
        WHERE organisation_id = %s
    """

    cursor.execute(
        query,
        (organisation_id,)
    )

    organisation = cursor.fetchone()


    if not organisation:

        cursor.close()
        db.close()

        return "Organisation not found.", 404


    if organisation["status"] != "Verified":

        cursor.close()
        db.close()

        return "Your organisation must be verified before adding resources.", 403


    if request.method == "GET":

        cursor.close()
        db.close()

        return render_template(
            "organisation_resource_add.html"
        )


    resource_name = request.form.get(
        "resource_name",
        ""
    ).strip()


    resource_type = request.form.get(
        "resource_type",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    recommended_for = request.form.get(
        "recommended_for",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    action = request.form.get(
        "action",
        "draft"
    )


    if (
        not resource_name
        or not resource_type
        or not description
    ):

        cursor.close()
        db.close()

        return render_template(
            "organisation_resource_add.html",
            error="Resource name, resource type and description are required.",
            form_data=request.form
        )


    if action == "submit":

        status = "Pending"

    else:

        status = "Draft"


    query = """
        INSERT INTO resources (
            organisation_id,
            resource_name,
            resource_type,
            description,
            recommended_for,
            official_website,
            status,
            submitted_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            NULLIF(%s, ''),
            %s,
            %s
        )
    """


    submitted_at = (
        "CURRENT_TIMESTAMP"
        if status == "Pending"
        else None
    )


    if status == "Pending":

        query = """
            INSERT INTO resources (
                organisation_id,
                resource_name,
                resource_type,
                description,
                recommended_for,
                official_website,
                status,
                submitted_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                NULLIF(%s, ''),
                'Pending',
                CURRENT_TIMESTAMP
            )
        """

        cursor.execute(
            query,
            (
                organisation_id,
                resource_name,
                resource_type,
                description,
                recommended_for,
                official_website
            )
        )

    else:

        query = """
            INSERT INTO resources (
                organisation_id,
                resource_name,
                resource_type,
                description,
                recommended_for,
                official_website,
                status
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                NULLIF(%s, ''),
                'Draft'
            )
        """

        cursor.execute(
            query,
            (
                organisation_id,
                resource_name,
                resource_type,
                description,
                recommended_for,
                official_website
            )
        )


    db.commit()


    cursor.close()
    db.close()


    return redirect(
        "/organisation/dashboard"
    )


# -------------------------
# SUBMIT RESOURCE FOR REVIEW
# -------------------------

@app.route(
    "/organisation/resources/<int:resource_id>/submit",
    methods=["POST"]
)
def submit_resource(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Organisation"
    ):

        return redirect("/login")


    organisation_id = session.get(
        "organisation_id"
    )


    if not organisation_id:

        return redirect("/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Get Resource
    # -------------------------

    query = """
        SELECT
            resource_id,
            organisation_id,
            status
        FROM resources
        WHERE resource_id = %s
    """

    cursor.execute(
        query,
        (resource_id,)
    )


    resource = cursor.fetchone()


    if not resource:

        cursor.close()
        db.close()

        return "Resource not found.", 404


    # -------------------------
    # Ownership Check
    # -------------------------

    if resource["organisation_id"] != organisation_id:

        cursor.close()
        db.close()

        return "Access denied.", 403


    # -------------------------
    # Only Draft Resources
    # can be submitted
    # -------------------------

    if resource["status"] != "Draft":

        cursor.close()
        db.close()

        return "Only draft resources can be submitted for review.", 400


    # -------------------------
    # Submit Resource
    # -------------------------

    query = """
        UPDATE resources

        SET
            status = 'Pending',
            submitted_at = CURRENT_TIMESTAMP,
            reviewed_at = NULL,
            reviewed_by = NULL,
            review_reason = NULL

        WHERE
            resource_id = %s
            AND organisation_id = %s
            AND status = 'Draft'
    """


    cursor.execute(
        query,
        (
            resource_id,
            organisation_id
        )
    )


    db.commit()


    cursor.close()
    db.close()


    return redirect(
        "/resources"
    )


# -------------------------
# APPROVE RESOURCE
# -------------------------

@app.route(
    "/admin/resources/<int:resource_id>/approve",
    methods=["POST"]
)
def approve_resource(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            resource_id,
            status
        FROM resources
        WHERE resource_id = %s
    """

    cursor.execute(
        query,
        (resource_id,)
    )


    resource = cursor.fetchone()


    if not resource:

        cursor.close()
        db.close()

        return "Resource not found.", 404


    if resource["status"] != "Pending":

        cursor.close()
        db.close()

        return "Only pending resources can be approved.", 400


    query = """
        UPDATE resources

        SET
            status = 'Published',
            is_featured = FALSE,
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = %s,
            review_reason = %s

        WHERE
            resource_id = %s
            AND status = 'Pending'
    """

    cursor.execute(
        query,
        (
            session["user_id"],
            "Resource approved.",
            resource_id
        )
    )


    db.commit()


    cursor.close()
    db.close()


    return redirect(
        f"/admin/resources/{resource_id}"
    )


# -------------------------
# REJECT RESOURCE
# -------------------------

@app.route(
    "/admin/resources/<int:resource_id>/reject",
    methods=["POST"]
)
def reject_resource(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            resource_id,
            status
        FROM resources
        WHERE resource_id = %s
    """

    cursor.execute(
        query,
        (resource_id,)
    )


    resource = cursor.fetchone()


    if not resource:

        cursor.close()
        db.close()

        return "Resource not found.", 404


    if resource["status"] != "Pending":

        cursor.close()
        db.close()

        return "Only pending resources can be rejected.", 400


    query = """
        UPDATE resources

        SET
            status = 'Rejected',
            is_featured = FALSE,
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = %s,
            review_reason = %s

        WHERE
            resource_id = %s
            AND status = 'Pending'
    """

    cursor.execute(
        query,
        (
            session["user_id"],
            "Resource rejected.",
            resource_id
        )
    )


    db.commit()


    cursor.close()
    db.close()


    return redirect(
        f"/admin/resources/{resource_id}"
    )


# -------------------------
# ARCHIVE RESOURCE
# -------------------------

@app.route(
    "/admin/resources/<int:resource_id>/archive",
    methods=["POST"]
)
def archive_resource(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            resource_id,
            status
        FROM resources
        WHERE resource_id = %s
    """

    cursor.execute(
        query,
        (resource_id,)
    )


    resource = cursor.fetchone()


    if not resource:

        cursor.close()
        db.close()

        return "Resource not found.", 404


    if resource["status"] == "Archived":

        cursor.close()
        db.close()

        return "Resource is already archived.", 400


    query = """
        UPDATE resources

        SET
            status = 'Archived',
            is_featured = FALSE

        WHERE
            resource_id = %s
    """

    cursor.execute(
        query,
        (resource_id,)
    )


    db.commit()


    cursor.close()
    db.close()


    return redirect(
        "/admin/resources"
    )


# -------------------------
# FEATURE / UNFEATURE RESOURCE
# -------------------------

@app.route(
    "/admin/resources/<int:resource_id>/feature",
    methods=["POST"]
)
def toggle_resource_feature(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            resource_id,
            status,
            is_featured
        FROM resources
        WHERE resource_id = %s
    """

    cursor.execute(
        query,
        (resource_id,)
    )


    resource = cursor.fetchone()


    if not resource:

        cursor.close()
        db.close()

        return "Resource not found.", 404


    if resource["status"] != "Published":

        cursor.close()
        db.close()

        return "Only published resources can be featured.", 400


    new_featured_status = not resource["is_featured"]


    query = """
        UPDATE resources

        SET
            is_featured = %s

        WHERE
            resource_id = %s
            AND status = 'Published'
    """

    cursor.execute(
        query,
        (
            new_featured_status,
            resource_id
        )
    )


    db.commit()


    cursor.close()
    db.close()


    return redirect(
        f"/admin/resources/{resource_id}"
    )


# -------------------------
# EDIT RESOURCE AS ADMIN
# -------------------------

@app.route(
    "/admin/resources/<int:resource_id>/edit",
    methods=["GET", "POST"]
)
def admin_edit_resource(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            resource_id,
            resource_name,
            resource_type,
            description,
            recommended_for,
            official_website,
            status,
            organisation_id
        FROM resources
        WHERE resource_id = %s
    """

    cursor.execute(
        query,
        (resource_id,)
    )


    resource = cursor.fetchone()


    if not resource:

        cursor.close()
        db.close()

        return "Resource not found.", 404


    if resource["status"] == "Archived":

        cursor.close()
        db.close()

        return "Archived resources cannot be edited.", 400


    # -------------------------
    # OPEN EDIT PAGE
    # -------------------------

    if request.method == "GET":

        cursor.close()
        db.close()

        return render_template(
            "admin_resource_edit.html",
            resource=resource
        )


    # -------------------------
    # GET UPDATED INFORMATION
    # -------------------------

    resource_name = request.form.get(
        "resource_name",
        ""
    ).strip()


    resource_type = request.form.get(
        "resource_type",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    recommended_for = request.form.get(
        "recommended_for",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    if (
        not resource_name
        or not resource_type
        or not description
    ):

        cursor.close()
        db.close()

        return render_template(
            "admin_resource_edit.html",
            resource=resource,
            error="Resource name, resource type and description are required."
        )


    query = """
        UPDATE resources

        SET
            resource_name = %s,
            resource_type = %s,
            description = %s,
            recommended_for = %s,
            official_website = NULLIF(%s, '')

        WHERE
            resource_id = %s
    """

    cursor.execute(
        query,
        (
            resource_name,
            resource_type,
            description,
            recommended_for,
            official_website,
            resource_id
        )
    )


    db.commit()


    cursor.close()
    db.close()


    return redirect(
        f"/admin/resources/{resource_id}"
    )


# -------------------------
# ARCHIVED RESOURCES
# -------------------------

@app.route("/admin/resources/archived")
def admin_archived_resources():

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            r.resource_id,
            r.resource_name,
            r.resource_type,
            r.description,
            r.recommended_for,
            r.official_website,
            r.status,
            r.organisation_id,
            r.is_featured,
            r.submitted_at,
            r.reviewed_at,
            r.reviewed_by,
            r.review_reason,
            r.created_at,
            r.updated_at,
            org.organisation_name
        FROM resources r
        LEFT JOIN organisations org
            ON r.organisation_id = org.organisation_id
        WHERE r.status = 'Archived'
        ORDER BY r.updated_at DESC
    """


    cursor.execute(query)


    resources = cursor.fetchall()


    cursor.close()

    db.close()


    return render_template(
        "admin_resources_archived.html",
        resources=resources
    )


# -------------------------
# RESTORE RESOURCE
# -------------------------

@app.route(
    "/admin/resources/<int:resource_id>/unarchive",
    methods=["POST"]
)
def unarchive_resource(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    query = """
        SELECT
            resource_id,
            status
        FROM resources
        WHERE resource_id = %s
    """


    cursor.execute(
        query,
        (resource_id,)
    )


    resource = cursor.fetchone()


    if not resource:

        cursor.close()
        db.close()

        return "Resource not found.", 404


    if resource["status"] != "Archived":

        cursor.close()
        db.close()

        return "Only archived resources can be restored.", 400


    query = """
        UPDATE resources

        SET
            status = 'Draft',
            is_featured = FALSE,
            review_reason = NULL

        WHERE
            resource_id = %s
            AND status = 'Archived'
    """


    cursor.execute(
        query,
        (resource_id,)
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect(
        "/admin/resources/archived"
    )


# -------------------------
# EDIT RESOURCE
# -------------------------

@app.route(
    "/organisation/resources/<int:resource_id>/edit",
    methods=["GET", "POST"]
)
def edit_resource(resource_id):

    # Must be logged in

    if "user_id" not in session:

        return redirect("/login")


    # Only Organisations can edit resources here

    if session.get("role") != "Organisation":

        return redirect("/resources")


    organisation_id = session.get(
        "organisation_id"
    )


    if not organisation_id:

        return redirect("/resources")


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Get Resource
    # -------------------------

    query = """
        SELECT
            resource_id,
            organisation_id,
            resource_name,
            resource_type,
            description,
            recommended_for,
            official_website,
            status,
            is_featured
        FROM resources
        WHERE resource_id = %s
    """

    cursor.execute(
        query,
        (resource_id,)
    )


    resource = cursor.fetchone()


    if not resource:

        cursor.close()
        db.close()

        return "Resource not found.", 404


    # -------------------------
    # Ownership Check
    # -------------------------

    if resource["organisation_id"] != organisation_id:

        cursor.close()
        db.close()

        return "Access denied.", 403


    # -------------------------
    # Archived Resources
    # cannot be edited
    # -------------------------

    if resource["status"] == "Archived":

        cursor.close()
        db.close()

        return "Archived resources cannot be edited.", 400


    # -------------------------
    # GET
    # -------------------------

    if request.method == "GET":

        cursor.close()
        db.close()

        return render_template(
            "organisation_resource_edit.html",
            resource=resource
        )


    # -------------------------
    # POST
    # -------------------------

    resource_name = request.form.get(
        "resource_name",
        ""
    ).strip()


    resource_type = request.form.get(
        "resource_type",
        ""
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    recommended_for = request.form.get(
        "recommended_for",
        ""
    ).strip()


    official_website = request.form.get(
        "official_website",
        ""
    ).strip()


    action = request.form.get(
        "action",
        "save"
    )


    # -------------------------
    # Validation
    # -------------------------

    if (
        not resource_name
        or not resource_type
        or not description
    ):

        cursor.close()
        db.close()

        return render_template(
            "organisation_resource_edit.html",
            resource=resource,
            error="Resource name, resource type and description are required."
        )


    current_status = resource["status"]


    # -------------------------
    # Determine Status
    # -------------------------

    if current_status == "Draft":

        if action == "submit":

            status = "Pending"

        else:

            status = "Draft"


    elif current_status == "Pending":

        status = "Pending"


    elif current_status == "Rejected":

        if action == "submit":

            status = "Pending"

        else:

            status = "Rejected"


    else:

        # Published resource has been changed.
        # Changes require Admin review.

        status = "Pending"


    # -------------------------
    # Update Resource
    # -------------------------

    query = """
        UPDATE resources

        SET
            resource_name = %s,
            resource_type = %s,
            description = %s,
            recommended_for = %s,
            official_website = NULLIF(%s, ''),
            status = %s,

            is_featured =
                CASE
                    WHEN %s = 'Pending'
                    THEN FALSE
                    ELSE is_featured
                END,

            submitted_at =
                CASE
                    WHEN %s = 'Pending'
                    THEN CURRENT_TIMESTAMP
                    ELSE submitted_at
                END,

            reviewed_at = NULL,
            reviewed_by = NULL,
            review_reason = NULL

        WHERE
            resource_id = %s
            AND organisation_id = %s
    """


    cursor.execute(
        query,
        (
            resource_name,
            resource_type,
            description,
            recommended_for,
            official_website,
            status,
            status,
            status,
            resource_id,
            organisation_id
        )
    )


    db.commit()


    cursor.close()
    db.close()


    return redirect(
        "/resources"
    )


@app.route(
    "/organisation/resources/<int:resource_id>/delete",
    methods=["POST"]
)
def delete_resource(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Organisation"
    ):
        return redirect("/login")

    organisation_id = session.get("organisation_id")

    if not organisation_id:
        return redirect("/login")

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            resource_id,
            organisation_id,
            status
        FROM resources
        WHERE resource_id = %s
    """

    cursor.execute(query, (resource_id,))
    resource = cursor.fetchone()

    if not resource:
        cursor.close()
        db.close()
        return "Resource not found.", 404

    if resource["organisation_id"] != organisation_id:
        cursor.close()
        db.close()
        return "You do not have permission to delete this resource.", 403

    if resource["status"] not in ["Draft", "Rejected"]:
        cursor.close()
        db.close()
        return "Only Draft or Rejected resources can be deleted.", 400

    query = """
        DELETE FROM resources
        WHERE
            resource_id = %s
            AND organisation_id = %s
            AND status IN ('Draft', 'Rejected')
    """

    cursor.execute(
        query,
        (
            resource_id,
            organisation_id
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect("/resources")


# -------------------------
# UNIVERSITIES
# -------------------------

@app.route("/universities")
def universities():

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    search = request.args.get("search", "").strip()
    selected_country = request.args.get("country", "").strip()
    selected_type = request.args.get("type", "").strip()
    selected_programme = request.args.get("programme", "").strip()


    # ---------------------------------------------------------
    # UNIVERSITY SEARCH
    # ---------------------------------------------------------

    query = """
        SELECT
            u.university_id,
            u.university_name,
            u.country,
            u.city,
            u.university_type,
            u.description,
            u.official_website,
            u.admissions_website,
            COUNT(
                CASE
                    WHEN p.status = 'Published'
                    THEN p.programme_id
                END
            ) AS programme_count

        FROM universities u

        LEFT JOIN programmes p
            ON u.university_id = p.university_id

        WHERE
            u.status = 'Published'
    """

    parameters = []


    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    if search:

        query += """
            AND (
                u.university_name LIKE %s
                OR u.country LIKE %s
                OR u.city LIKE %s

                OR EXISTS (
                    SELECT 1
                    FROM programmes ps
                    WHERE
                        ps.university_id = u.university_id
                        AND ps.status = 'Published'
                        AND (
                            ps.programme_name LIKE %s
                            OR ps.field LIKE %s
                        )
                )
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])


    # ---------------------------------------------------------
    # COUNTRY FILTER
    # ---------------------------------------------------------

    if selected_country:

        query += """
            AND u.country = %s
        """

        parameters.append(selected_country)


    # ---------------------------------------------------------
    # UNIVERSITY TYPE FILTER
    # ---------------------------------------------------------

    if selected_type:

        query += """
            AND u.university_type = %s
        """

        parameters.append(selected_type)


    # ---------------------------------------------------------
    # PROGRAMME FILTER
    # ---------------------------------------------------------

    if selected_programme:

        query += """
            AND EXISTS (
                SELECT 1
                FROM programmes pf
                WHERE
                    pf.university_id = u.university_id
                    AND pf.status = 'Published'
                    AND pf.programme_name = %s
            )
        """

        parameters.append(selected_programme)


    # ---------------------------------------------------------
    # GROUPING
    # ---------------------------------------------------------

    query += """
        GROUP BY
            u.university_id,
            u.university_name,
            u.country,
            u.city,
            u.university_type,
            u.description,
            u.official_website,
            u.admissions_website

        ORDER BY
            u.university_name ASC
    """


    cursor.execute(
        query,
        parameters
    )

    universities = cursor.fetchall()


    # ---------------------------------------------------------
    # COUNTRIES
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT DISTINCT country
        FROM universities
        WHERE status = 'Published'
        ORDER BY country ASC
        """
    )

    countries = cursor.fetchall()


    # ---------------------------------------------------------
    # UNIVERSITY TYPES
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT DISTINCT university_type
        FROM universities
        WHERE status = 'Published'
        ORDER BY university_type ASC
        """
    )

    university_types = cursor.fetchall()


    # ---------------------------------------------------------
    # PROGRAMMES
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT DISTINCT programme_name
        FROM programmes
        WHERE status = 'Published'
        ORDER BY programme_name ASC
        """
    )

    programmes = cursor.fetchall()


    cursor.close()
    db.close()


    return render_template(
        "universities.html",

        universities=universities,

        countries=countries,

        university_types=university_types,

        programmes=programmes,

        search=search,

        selected_country=selected_country,

        selected_type=selected_type,

        selected_programme=selected_programme,

        role=session.get("role")
    )


@app.route("/universities/<int:university_id>")
def university_profile(university_id):

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            university_id,
            university_name,
            country,
            city,
            university_type,
            description,
            official_website,
            admissions_website,
            international_students_info,
            additional_notes,
            organisation_id,
            status
        FROM universities
        WHERE
            university_id = %s
            AND status = 'Published'
    """

    cursor.execute(query, (university_id,))

    university = cursor.fetchone()

    if not university:

        cursor.close()
        db.close()

        return "University not found", 404


    query = """
        SELECT
            programme_id,
            programme_name,
            degree_level,
            field,
            description,
            duration,
            eligibility,
            official_website,
            admissions_website
        FROM programmes
        WHERE
            university_id = %s
            AND status = 'Published'
        ORDER BY programme_name ASC
    """

    cursor.execute(query, (university_id,))

    programmes = cursor.fetchall()


    saved_university = False

    if (
        "user_id" in session
        and session.get("role") == "Student"
    ):

        cursor.execute(
            """
            SELECT user_id
            FROM saved_universities
            WHERE
                user_id = %s
                AND university_id = %s
            """,
            (
                session["user_id"],
                university_id
            )
        )

        saved_university = cursor.fetchone() is not None


    cursor.close()
    db.close()

    return render_template(
        "university_profile.html",
        university=university,
        programmes=programmes,
        saved_university=saved_university
    )


@app.route(
    "/universities/<int:university_id>/programmes/<int:programme_id>"
)
def programme_profile(university_id, programme_id):

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            p.programme_id,
            p.university_id,
            p.programme_name,
            p.degree_level,
            p.field,
            p.description,
            p.duration,
            p.eligibility,
            p.official_website,
            p.admissions_website,
            u.university_name,
            u.city,
            u.country
        FROM programmes p
        INNER JOIN universities u
            ON p.university_id = u.university_id
        WHERE
            p.programme_id = %s
            AND p.university_id = %s
            AND p.status = 'Published'
            AND u.status = 'Published'
    """

    cursor.execute(
        query,
        (programme_id, university_id)
    )

    programme = cursor.fetchone()

    if not programme:

        cursor.close()
        db.close()

        return "Programme not found", 404


    saved_programme = False

    if (
        "user_id" in session
        and session.get("role") == "Student"
    ):

        cursor.execute(
            """
            SELECT user_id
            FROM saved_programmes
            WHERE
                user_id = %s
                AND programme_id = %s
            """,
            (
                session["user_id"],
                programme_id
            )
        )

        saved_programme = cursor.fetchone() is not None


    cursor.close()
    db.close()

    return render_template(
        "programme_profile.html",
        programme=programme,
        saved_programme=saved_programme
    )


@app.route(
    "/universities/<int:university_id>/save",
    methods=["POST"]
)
def save_university(university_id):

    if (
        "user_id" not in session
        or session.get("role") != "Student"
    ):
        return redirect("/login")

    user_id = session["user_id"]

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT university_id
        FROM universities
        WHERE
            university_id = %s
            AND status = 'Published'
        """,
        (university_id,)
    )

    university = cursor.fetchone()

    if not university:

        cursor.close()
        db.close()

        return "University not found", 404

    cursor.execute(
        """
        SELECT user_id
        FROM saved_universities
        WHERE
            user_id = %s
            AND university_id = %s
        """,
        (user_id, university_id)
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            DELETE FROM saved_universities
            WHERE
                user_id = %s
                AND university_id = %s
            """,
            (user_id, university_id)
        )

    else:

        cursor.execute(
            """
            INSERT INTO saved_universities (
                user_id,
                university_id
            )
            VALUES (%s, %s)
            """,
            (user_id, university_id)
        )

    db.commit()

    cursor.close()
    db.close()

    return redirect(
        f"/universities/{university_id}"
    )


@app.route(
    "/universities/<int:university_id>/programmes/<int:programme_id>/save",
    methods=["POST"]
)
def save_programme(university_id, programme_id):

    if (
        "user_id" not in session
        or session.get("role") != "Student"
    ):
        return redirect("/login")

    user_id = session["user_id"]

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            programme_id
        FROM programmes
        WHERE
            programme_id = %s
            AND university_id = %s
            AND status = 'Published'
        """,
        (programme_id, university_id)
    )

    programme = cursor.fetchone()

    if not programme:

        cursor.close()
        db.close()

        return "Programme not found", 404

    cursor.execute(
        """
        SELECT user_id
        FROM saved_programmes
        WHERE
            user_id = %s
            AND programme_id = %s
        """,
        (user_id, programme_id)
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            DELETE FROM saved_programmes
            WHERE
                user_id = %s
                AND programme_id = %s
            """,
            (user_id, programme_id)
        )

    else:

        cursor.execute(
            """
            INSERT INTO saved_programmes (
                user_id,
                programme_id
            )
            VALUES (%s, %s)
            """,
            (user_id, programme_id)
        )

    db.commit()

    cursor.close()
    db.close()

    return redirect(
        f"/universities/{university_id}/programmes/{programme_id}"
    )


# -------------------------
# SAVE / UNSAVE RESOURCE
# -------------------------

@app.route(
    "/resources/<int:resource_id>/save",
    methods=["POST"]
)
def save_resource(resource_id):

    if (
        "user_id" not in session
        or session.get("role") != "Student"
    ):

        return redirect("/login")


    user_id = session["user_id"]

    db = connect_db()
    cursor = db.cursor(dictionary=True)


    # Check that the resource exists and is published

    cursor.execute(
        """
        SELECT
            resource_id
        FROM resources
        WHERE
            resource_id = %s
            AND status = 'Published'
        """,
        (resource_id,)
    )

    resource = cursor.fetchone()


    if not resource:

        cursor.close()
        db.close()

        return "Resource not found", 404


    # Check whether already saved

    cursor.execute(
        """
        SELECT
            user_id
        FROM saved_resources
        WHERE
            user_id = %s
            AND resource_id = %s
        """,
        (
            user_id,
            resource_id
        )
    )

    existing = cursor.fetchone()


    if existing:

        # Unsave

        cursor.execute(
            """
            DELETE FROM saved_resources
            WHERE
                user_id = %s
                AND resource_id = %s
            """,
            (
                user_id,
                resource_id
            )
        )

    else:

        # Save

        cursor.execute(
            """
            INSERT INTO saved_resources (
                user_id,
                resource_id
            )
            VALUES (
                %s,
                %s
            )
            """,
            (
                user_id,
                resource_id
            )
        )


    db.commit()

    cursor.close()
    db.close()


    return redirect("/resources")


# -------------------------
# SAVE / UNSAVE OPPORTUNITY
# -------------------------

@app.route(
    "/opportunities/<int:opportunity_id>/save",
    methods=["POST"]
)
def save_opportunity(opportunity_id):

    if (
        "user_id" not in session
        or session.get("role") != "Student"
    ):

        return redirect("/login")


    user_id = session["user_id"]

    db = connect_db()
    cursor = db.cursor(dictionary=True)


    # Check that the opportunity exists and is published

    cursor.execute(
        """
        SELECT
            opportunity_id
        FROM opportunities
        WHERE
            opportunity_id = %s
            AND status = 'Published'
        """,
        (opportunity_id,)
    )

    opportunity = cursor.fetchone()


    if not opportunity:

        cursor.close()
        db.close()

        return "Opportunity not found", 404


    # Check whether already saved

    cursor.execute(
        """
        SELECT
            user_id
        FROM saved_opportunities
        WHERE
            user_id = %s
            AND opportunity_id = %s
        """,
        (
            user_id,
            opportunity_id
        )
    )

    existing = cursor.fetchone()


    if existing:

        # Unsave

        cursor.execute(
            """
            DELETE FROM saved_opportunities
            WHERE
                user_id = %s
                AND opportunity_id = %s
            """,
            (
                user_id,
                opportunity_id
            )
        )

    else:

        # Save

        cursor.execute(
            """
            INSERT INTO saved_opportunities (
                user_id,
                opportunity_id
            )
            VALUES (
                %s,
                %s
            )
            """,
            (
                user_id,
                opportunity_id
            )
        )


    db.commit()

    cursor.close()
    db.close()


    return redirect("/opportunities")


@app.route("/myastrobase/saved")
def saved_items():

    if (
        "user_id" not in session
        or session.get("role") != "Student"
    ):

        return redirect("/login")


    user_id = session["user_id"]

    db = connect_db()
    cursor = db.cursor(dictionary=True)


    # ---------------------------------------------------------
    # SAVED UNIVERSITIES
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT
            u.university_id,
            u.university_name,
            u.country,
            u.city,
            u.university_type,
            u.description,
            su.saved_at

        FROM saved_universities su

        INNER JOIN universities u
            ON su.university_id = u.university_id

        WHERE
            su.user_id = %s
            AND u.status = 'Published'

        ORDER BY su.saved_at DESC
        """,
        (user_id,)
    )

    saved_universities = cursor.fetchall()


    # ---------------------------------------------------------
    # SAVED PROGRAMMES
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT
            p.programme_id,
            p.programme_name,
            p.degree_level,
            p.field,
            p.description,
            p.duration,
            p.university_id,
            u.university_name,
            u.city,
            u.country,
            sp.saved_at

        FROM saved_programmes sp

        INNER JOIN programmes p
            ON sp.programme_id = p.programme_id

        INNER JOIN universities u
            ON p.university_id = u.university_id

        WHERE
            sp.user_id = %s
            AND p.status = 'Published'
            AND u.status = 'Published'

        ORDER BY sp.saved_at DESC
        """,
        (user_id,)
    )

    saved_programmes = cursor.fetchall()


    # ---------------------------------------------------------
    # SAVED RESOURCES
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT
            r.resource_id,
            r.resource_name,
            r.resource_type,
            r.description,
            r.recommended_for,
            r.official_website,
            r.organisation_id,
            org.organisation_name,
            sr.saved_at

        FROM saved_resources sr

        INNER JOIN resources r
            ON sr.resource_id = r.resource_id

        LEFT JOIN organisations org
            ON r.organisation_id = org.organisation_id

        WHERE
            sr.user_id = %s
            AND r.status = 'Published'

        ORDER BY sr.saved_at DESC
        """,
        (user_id,)
    )

    saved_resources = cursor.fetchall()


    # ---------------------------------------------------------
    # SAVED OPPORTUNITIES
    # ---------------------------------------------------------

    cursor.execute(
        """
        SELECT
            o.opportunity_id,
            o.opportunity_name,
            o.category,
            o.description,
            o.eligibility,
            o.deadline,
            o.official_website,
            o.organisation_id,
            org.organisation_name,
            so.saved_at

        FROM saved_opportunities so

        INNER JOIN opportunities o
            ON so.opportunity_id = o.opportunity_id

        LEFT JOIN organisations org
            ON o.organisation_id = org.organisation_id

        WHERE
            so.user_id = %s
            AND o.status = 'Published'

        ORDER BY so.saved_at DESC
        """,
        (user_id,)
    )

    saved_opportunities = cursor.fetchall()


    cursor.close()
    db.close()


    return render_template(
        "saved.html",

        saved_universities=saved_universities,

        saved_programmes=saved_programmes,

        saved_resources=saved_resources,

        saved_opportunities=saved_opportunities
    )


# -------------------------
# ADMIN UNIVERSITY MANAGEMENT
# -------------------------

@app.route("/admin/universities")
def admin_universities():

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    status = request.args.get(
        "status"
    )


    # Archived universities have their own page

    if status == "Archived":

        return redirect(
            "/admin/universities/archived"
        )


    db = connect_db()

    cursor = db.cursor(dictionary=True)


    # -------------------------
    # Base Query
    # -------------------------

    query = """
        SELECT
            u.university_id,
            u.university_name,
            u.country,
            u.city,
            u.university_type,
            u.description,
            u.official_website,
            u.admissions_website,
            u.international_students_info,
            u.additional_notes,
            u.organisation_id,
            u.status,
            u.submitted_at,
            u.reviewed_at,
            u.reviewed_by,
            u.review_reason,
            u.created_at,
            u.updated_at,

            org.organisation_name,

            COUNT(
                CASE
                    WHEN p.status != 'Archived'
                    THEN p.programme_id
                END
            ) AS programme_count

        FROM universities u

        LEFT JOIN organisations org
            ON u.organisation_id = org.organisation_id

        LEFT JOIN programmes p
            ON u.university_id = p.university_id
    """


    # -------------------------
    # Status Filter
    # -------------------------

    if status in [
        "Pending",
        "Published",
        "Rejected",
        "Draft"
    ]:

        query += """
            WHERE u.status = %s
        """

        query += """
            GROUP BY
                u.university_id,
                u.university_name,
                u.country,
                u.city,
                u.university_type,
                u.description,
                u.official_website,
                u.admissions_website,
                u.international_students_info,
                u.additional_notes,
                u.organisation_id,
                u.status,
                u.submitted_at,
                u.reviewed_at,
                u.reviewed_by,
                u.review_reason,
                u.created_at,
                u.updated_at,
                org.organisation_name

            ORDER BY
                u.created_at DESC
        """


        cursor.execute(
            query,
            (
                status,
            )
        )


    else:

        query += """
            WHERE u.status != 'Archived'
        """

        query += """
            GROUP BY
                u.university_id,
                u.university_name,
                u.country,
                u.city,
                u.university_type,
                u.description,
                u.official_website,
                u.admissions_website,
                u.international_students_info,
                u.additional_notes,
                u.organisation_id,
                u.status,
                u.submitted_at,
                u.reviewed_at,
                u.reviewed_by,
                u.review_reason,
                u.created_at,
                u.updated_at,
                org.organisation_name

            ORDER BY
                u.created_at DESC
        """


        cursor.execute(
            query
        )


    universities = cursor.fetchall()


    cursor.close()

    db.close()


    return render_template(
        "admin_universities.html",
        universities=universities,
        current_status=status
    )

# -------------------------
# ADMIN ADD UNIVERSITY
# -------------------------

@app.route(
    "/admin/universities/add",
    methods=["GET", "POST"]
)
def admin_add_university():

    if (
        "user_id" not in session
        or session.get("role") != "Admin"
    ):

        return redirect("/admin/login")


    db = connect_db()

    cursor = db.cursor(
        dictionary=True
    )


    # -------------------------
    # GET
    # -------------------------

    if request.method == "GET":

        cursor.execute(
            """
            SELECT
                organisation_id,
                organisation_name
            FROM organisations
            WHERE status = 'Verified'
            ORDER BY organisation_name
            """
        )

        organisations = cursor.fetchall()


        cursor.close()

        db.close()


        return render_template(
            "admin_university_add.html",
            organisations=organisations
        )


    # -------------------------
    # POST
    # -------------------------

    organisation_id = request.form.get(
        "organisation_id"
    )

    university_name = request.form.get(
        "university_name"
    )

    country = request.form.get(
        "country"
    )

    city = request.form.get(
        "city"
    )

    university_type = request.form.get(
        "university_type"
    )

    description = request.form.get(
        "description"
    )

    official_website = request.form.get(
        "official_website"
    )

    admissions_website = request.form.get(
        "admissions_website"
    )

    international_students_info = request.form.get(
        "international_students_info"
    )

    additional_notes = request.form.get(
        "additional_notes"
    )

    status = request.form.get(
        "status"
    )


    # -------------------------
    # Create University
    # -------------------------

    query = """
        INSERT INTO universities (
            university_name,
            country,
            city,
            university_type,
            description,
            official_website,
            admissions_website,
            international_students_info,
            additional_notes,
            organisation_id,
            status
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """


    cursor.execute(
        query,
        (
            university_name,
            country,
            city,
            university_type,
            description,
            official_website or None,
            admissions_website or None,
            international_students_info or None,
            additional_notes or None,
            organisation_id or None,
            status
        )
    )


    db.commit()


    cursor.close()

    db.close()


    return redirect(
        "/admin/universities"
    )


# -------------------------
# STUDENT REPORT
# -------------------------

@app.route("/report", methods=["GET", "POST"])
def report():

    if (
        "user_id" not in session
        or session.get("role") != "Student"
    ):

        return redirect("/login")


    if request.method == "POST":

        report_text = request.form.get(
            "report",
            ""
        ).strip()


        if not report_text:

            return render_template(
                "report.html",
                error="Please enter a report or suggestion."
            )


        db = connect_db()

        cursor = db.cursor()


        query = """
            INSERT INTO reports (
                user_id,
                report_text
            )
            VALUES (
                %s,
                %s
            )
        """


        cursor.execute(
            query,
            (
                session["user_id"],
                report_text
            )
        )


        db.commit()


        cursor.close()

        db.close()


        return render_template(
            "report.html",
            success="Your report has been submitted to Astrobase."
        )


    return render_template(
        "report.html"
    )


# -------------------------
# PUBLIC PAGES
# -------------------------

# -------------------------
# PUBLIC PAGES
# -------------------------

@app.route("/HTML/about.html")
def about():
    return render_template("about.html")


@app.route("/HTML/astrobase_ai.html")
def astrobase_ai():
    return render_template("astrobase_ai.html")


@app.route("/HTML/assessment.html")
def assessment():
    return render_template("assessment.html")


@app.route("/HTML/community.html")
def community():
    return render_template("community.html")


@app.route("/HTML/explore.html")
def explore():
    return render_template("explore.html")


@app.route("/HTML/join.html")
def join():
    return render_template("join.html")


# -------------------------
# START FLASK
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)