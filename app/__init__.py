from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from app.models import (
    db,
    Department,
    Category,
    User,
    IssueGroup,
    Complaint,
    SimilarityRecord,
    ComplaintHistory
)

login_manager = LoginManager()


def create_app(config_class=None):
    """
    Flask Application Factory.
    Initializes extensions, registers blueprints, and sets up authentication.
    """
    if config_class is None:
        config_class = Config

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Validate priority weights on application startup
    config_class.validate_weights()

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Landing Page Route
    @app.route('/')
    def index():
        return render_template('index.html')

    return app


def seed_initial_data():
    """
    Seeds default institutional departments and categories if they do not exist.
    Called inside app context on initial database creation.
    """
    if Department.query.first():
        return  # Data already seeded

    default_data = [
        {
            'dept': 'Hostel Administration',
            'desc': 'Hostel rooms, amenities, and residential maintenance',
            'categories': [
                ('Hostel Maintenance', 'Room repairs, plumbing, furniture, and residential issues')
            ]
        },
        {
            'dept': 'IT Support Services',
            'desc': 'Campus network, Wi-Fi, lab equipment, and software',
            'categories': [
                ('Network & Wi-Fi', 'Campus Wi-Fi connectivity, DNS, and network speed issues'),
                ('Computer Lab Infrastructure', 'Lab computers, projectors, and operating systems')
            ]
        },
        {
            'dept': 'Estate & Sanitation Office',
            'desc': 'Campus cleanliness, waste management, and washrooms',
            'categories': [
                ('Campus Sanitation', 'Restrooms, water coolers, and campus hygiene')
            ]
        },
        {
            'dept': 'Electrical Maintenance Department',
            'desc': 'Power supply, lighting, switchboards, and ventilation',
            'categories': [
                ('Electrical & Lighting', 'Classroom lights, ceiling fans, power sockets, and outages')
            ]
        },
        {
            'dept': 'Academic Facilities Management',
            'desc': 'Classrooms, lecture halls, benches, and podiums',
            'categories': [
                ('Classroom Infrastructure', 'Desks, blackboards, podiums, and classroom audio')
            ]
        }
    ]

    for item in default_data:
        dept = Department(department_name=item['dept'], description=item['desc'])
        db.session.add(dept)
        db.session.flush()  # Populates dept.department_id

        for cat_name, cat_desc in item['categories']:
            cat = Category(
                department_id=dept.department_id,
                category_name=cat_name,
                description=cat_desc
            )
            db.session.add(cat)

    db.session.commit()
