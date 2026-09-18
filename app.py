import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sankhei_village_secret_key_2026_secure'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///village.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Database and Login Manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False) # Hashed password

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False) 

class PortalCategory(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)

class PortalEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.String(50), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

class SiteContent(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)

class MapLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    icon_type = db.Column(db.String(50), default='default')

class VisitorCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

class MandiPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(50), default="Quintal")
    market = db.Column(db.String(100), default="Nayagarh Mandi")
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class VillageSuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default="General")
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Received")
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from flask import session

@app.before_request
def track_visitor():
    if request.path.startswith('/static') or request.endpoint == 'static':
        return
    if 'has_visited' not in session:
        session['has_visited'] = True
        counter = VisitorCount.query.first()
        if counter:
            counter.count += 1
            db.session.commit()
        else:
            counter = VisitorCount(id=1, count=100)
            db.session.add(counter)
            db.session.commit()

@app.context_processor
def inject_global_data():
    counter = VisitorCount.query.first()
    total_count = counter.count if counter else 100
    mandi_prices = MandiPrice.query.order_by(MandiPrice.last_updated.desc()).all()
    suggestions = VillageSuggestion.query.order_by(VillageSuggestion.date_submitted.desc()).all()
    return dict(visitor_count=total_count, mandi_prices=mandi_prices, suggestions=suggestions)

# --- Routes ---

@app.route('/')
def index():
    events = Event.query.all()
    slideshow_images = Image.query.filter_by(category='slideshow').all()
    site_content_list = SiteContent.query.all()
    # Convert list to dict for easy access in template
    site_content = {sc.id: sc for sc in site_content_list}
    return render_template('index.html', events=events, slideshow_images=slideshow_images, site_content=site_content)

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/map')
def map_page():
    locations = MapLocation.query.all()
    return render_template('map.html', locations=locations)

@app.route('/announcements')
def announcements():
    announcements = Announcement.query.order_by(Announcement.date_posted.desc()).all()
    return render_template('announcements.html', announcements=announcements)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message_text = request.form.get('message')
        
        if name and email and message_text:
            new_msg = Message(name=name, email=email, message=message_text)
            db.session.add(new_msg)
            db.session.commit()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact'))
        else:
            flash('Please fill in all fields.', 'error')
            
    return render_template('contact.html')

@app.route('/portal')
def portal():
    # Fetch all categories and images
    categories = PortalCategory.query.all()
    images = Image.query.all()
    events = Event.query.all()
    portal_events = PortalEvent.query.all()
    messages = Message.query.order_by(Message.date_sent.desc()).all()
    all_announcements = Announcement.query.order_by(Announcement.date_posted.desc()).all()
    site_content_list = SiteContent.query.all()
    site_content = {sc.id: sc for sc in site_content_list}
    map_locations = MapLocation.query.all()
    
    # Pre-calculate counts for each category
    category_data = []
    category_icons = {
        'school': '🏫',
        'medical': '🏥',
        'sarapanch': '🏛️',
        'president': '👑',
        'culture': '🎭',
        'temples': '🛕',
        'agriculture': '🌾'
    }
    for cat in categories:
        img_count = Image.query.filter_by(category=cat.id).count()
        event_count = PortalEvent.query.filter_by(category_id=cat.id).count()
        icon = category_icons.get(cat.id, '📌')
        category_data.append({
            'cat': cat,
            'img_count': img_count,
            'event_count': event_count,
            'icon': icon
        })
        
    return render_template('portal.html', categories=categories, category_data=category_data, images=images, events=events, portal_events=portal_events, messages=messages, announcements=all_announcements, site_content=site_content, map_locations=map_locations)

@app.route('/portal/<category_id>')
def portal_category_detail(category_id):
    category = PortalCategory.query.get_or_404(category_id)
    all_categories = PortalCategory.query.all()
    category_images = Image.query.filter_by(category=category_id).all()
    category_events = PortalEvent.query.filter_by(category_id=category_id).all()
    
    category_icons = {
        'school': '🏫',
        'medical': '🏥',
        'sarapanch': '🏛️',
        'president': '👑',
        'culture': '🎭',
        'temples': '🛕',
        'agriculture': '🌾'
    }
    category_icon = category_icons.get(category_id, '📌')
    
    return render_template(
        'category_detail.html',
        category=category,
        all_categories=all_categories,
        images=category_images,
        events=category_events,
        category_icon=category_icon
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('portal'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not check_password_hash(current_user.password, current_password):
            flash('Incorrect current password.', 'error')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'error')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
        else:
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('portal'))
            
    return render_template('change_password.html')

@app.route('/edit_category/<category_id>', methods=['POST'])
@login_required
def edit_category(category_id):
    category = PortalCategory.query.get_or_404(category_id)
    new_description = request.form.get('description')
    profile_image = request.files.get('profile_image')
    
    if new_description:
        category.description = new_description
        
        # Handle profile image upload
        if profile_image and profile_image.filename != '' and allowed_file(profile_image.filename):
            filename = secure_filename(f"{category_id}_profile_{uuid.uuid4().hex}_{profile_image.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_image.save(filepath)
            category.profile_image = filename
            
        db.session.commit()
        flash(f'Section {category.title} updated successfully.', 'success')
    else:
        flash('Description cannot be empty.', 'error')
        
    return redirect(url_for('portal') + f'#{category_id}')

@app.route('/add_event', methods=['POST'])
@login_required
def add_event():
    tag = request.form.get('tag')
    description = request.form.get('description')
    
    if tag and description:
        new_event = Event(tag=tag.strip(), description=description.strip())
        db.session.add(new_event)
        db.session.commit()
        flash('Event added successfully.', 'success')
    else:
        flash('Event tag and description cannot be empty.', 'error')
        
    return redirect(url_for('portal') + '#homepage_content')

@app.route('/edit_event/<int:event_id>', methods=['POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    tag = request.form.get('tag')
    description = request.form.get('description')
    
    if tag and description:
        event.tag = tag.strip()
        event.description = description.strip()
        db.session.commit()
        flash('Event updated successfully.', 'success')
    else:
        flash('Event tag and description cannot be empty.', 'error')
        
    return redirect(url_for('portal') + '#homepage_content')

@app.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully.', 'success')
    return redirect(url_for('portal') + '#homepage_content')

@app.route('/edit_portal_event/<int:event_id>', methods=['POST'])
@login_required
def edit_portal_event(event_id):
    event = PortalEvent.query.get_or_404(event_id)
    category_id = event.category_id
    tag = request.form.get('tag')
    description = request.form.get('description')
    
    if tag and description:
        event.tag = tag.strip()
        event.description = description.strip()
        db.session.commit()
        flash(f'Event in {category_id} updated successfully.', 'success')
    else:
        flash('Event details cannot be empty.', 'error')
        
    return redirect(url_for('portal') + f'#{category_id}')

@app.route('/add_portal_event', methods=['POST'])
@login_required
def add_portal_event():
    category_id = request.form.get('category_id')
    tag = request.form.get('tag')
    description = request.form.get('description')
    
    if category_id and tag and description:
        new_event = PortalEvent(category_id=category_id, tag=tag, description=description)
        db.session.add(new_event)
        db.session.commit()
        flash(f'Event added to {category_id} successfully.', 'success')
    else:
        flash('Event details cannot be empty.', 'error')
        
    return redirect(url_for('portal') + f'#{category_id}')

@app.route('/delete_portal_event/<int:event_id>', methods=['POST'])
@login_required
def delete_portal_event(event_id):
    event = PortalEvent.query.get_or_404(event_id)
    category_id = event.category_id
    db.session.delete(event)
    db.session.commit()
    flash('Category event deleted successfully.', 'success')
    return redirect(url_for('portal') + f'#{category_id}')

@app.route('/add_announcement', methods=['POST'])
@login_required
def add_announcement():
    title = request.form.get('title')
    content = request.form.get('content')
    
    if title and content:
        new_ann = Announcement(title=title, content=content)
        db.session.add(new_ann)
        db.session.commit()
        flash('Announcement posted successfully.', 'success')
    else:
        flash('Title and content cannot be empty.', 'error')
        
    return redirect(url_for('portal') + '#announcements_content')

@app.route('/delete_announcement/<int:ann_id>', methods=['POST'])
@login_required
def delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted successfully.', 'success')
    return redirect(url_for('portal') + '#announcements_content')

@app.route('/delete_message/<int:msg_id>', methods=['POST'])
@login_required
def delete_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'success')
    return redirect(url_for('portal') + '#messages_content')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/upload', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('portal'))
    
    file = request.files['image']
    category = request.form.get('category')
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('portal'))
        
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        
        new_image = Image(filename=unique_filename, category=category)
        db.session.add(new_image)
        db.session.commit()
        
        flash('Image uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Only images allowed.', 'error')
        
    return redirect(url_for('portal') + f'#{category}')

@app.route('/delete_image/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully.', 'success')
    return redirect(url_for('portal') + f'#{image.category}')

@app.route('/edit_site_content/<content_id>', methods=['POST'])
@login_required
def edit_site_content(content_id):
    content = SiteContent.query.get_or_404(content_id)
    new_title = request.form.get('title')
    new_content = request.form.get('content')
    image_file = request.files.get('image')

    if new_title:
        content.title = new_title.replace('<br>', ' ').replace('&lt;br&gt;', ' ').replace('<br/>', ' ').strip()
    if new_content:
        content.content = new_content
        
    if image_file and image_file.filename != '' and allowed_file(image_file.filename):
        filename = secure_filename(f"{content_id}_{uuid.uuid4().hex}_{image_file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        content.image_filename = filename

    db.session.commit()
    flash(f'Content {content_id} updated successfully.', 'success')
    return redirect(url_for('portal') + '#homepage_static_content')

@app.route('/add_map_location', methods=['POST'])
@login_required
def add_map_location():
    name = request.form.get('name')
    description = request.form.get('description')
    latitude = request.form.get('latitude', type=float)
    longitude = request.form.get('longitude', type=float)
    icon_type = request.form.get('icon_type', 'default')

    if name and latitude and longitude:
        new_loc = MapLocation(name=name, description=description, latitude=latitude, longitude=longitude, icon_type=icon_type)
        db.session.add(new_loc)
        db.session.commit()
        flash('Map location added successfully.', 'success')
    else:
        flash('Name, Latitude, and Longitude are required.', 'error')
        
    return redirect(url_for('portal') + '#map_content')

@app.route('/edit_map_location/<int:loc_id>', methods=['POST'])
@login_required
def edit_map_location(loc_id):
    loc = MapLocation.query.get_or_404(loc_id)
    loc.name = request.form.get('name', loc.name)
    loc.description = request.form.get('description', loc.description)
    
    lat = request.form.get('latitude', type=float)
    if lat is not None: loc.latitude = lat
        
    lng = request.form.get('longitude', type=float)
    if lng is not None: loc.longitude = lng
        
    loc.icon_type = request.form.get('icon_type', loc.icon_type)
    
    db.session.commit()
    flash(f'Map location "{loc.name}" updated successfully.', 'success')
    return redirect(url_for('portal') + '#map_content')

@app.route('/delete_map_location/<int:loc_id>', methods=['POST'])
@login_required
def delete_map_location(loc_id):
    loc = MapLocation.query.get_or_404(loc_id)
    db.session.delete(loc)
    db.session.commit()
    flash('Map location deleted successfully.', 'success')
    return redirect(url_for('portal') + '#map_content')

# --- Additional Routes for Mandi Prices & Village Suggestions ---

@app.route('/submit_suggestion', methods=['POST'])
def submit_suggestion():
    title = request.form.get('title')
    name = request.form.get('name')
    category = request.form.get('category', 'General')
    description = request.form.get('description')
    
    if title and name and description:
        new_sug = VillageSuggestion(title=title, name=name, category=category, description=description)
        db.session.add(new_sug)
        db.session.commit()
        flash('Your suggestion/issue has been submitted to the Sarapanch Office!', 'success')
    else:
        flash('Please fill in all required fields.', 'error')
        
    return redirect(url_for('contact') + '#suggestions')

@app.route('/update_suggestion_status/<int:sug_id>', methods=['POST'])
@login_required
def update_suggestion_status(sug_id):
    sug = VillageSuggestion.query.get_or_404(sug_id)
    new_status = request.form.get('status')
    if new_status:
        sug.status = new_status
        db.session.commit()
        flash(f'Status for "{sug.title}" updated to {new_status}.', 'success')
    return redirect(request.referrer or url_for('portal'))

@app.route('/add_mandi_price', methods=['POST'])
@login_required
def add_mandi_price():
    crop_name = request.form.get('crop_name')
    price = request.form.get('price')
    market = request.form.get('market', 'Nayagarh Mandi')
    
    if crop_name and price:
        new_item = MandiPrice(crop_name=crop_name, price=price, market=market)
        db.session.add(new_item)
        db.session.commit()
        flash(f'Mandi price for {crop_name} added successfully.', 'success')
    else:
        flash('Crop name and price are required.', 'error')
        
    return redirect(url_for('portal_category_detail', category_id='agriculture'))

@app.route('/delete_mandi_price/<int:price_id>', methods=['POST'])
@login_required
def delete_mandi_price(price_id):
    item = MandiPrice.query.get_or_404(price_id)
    db.session.delete(item)
    db.session.commit()
    flash('Mandi price entry deleted.', 'success')
    return redirect(url_for('portal_category_detail', category_id='agriculture'))

# --- DB Initialization ---
def init_db():
    with app.app_context():
        db.create_all()
        # Create default admin user if none exists
        if not User.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('password123')
            admin = User(username='admin', password=hashed_pw)
            db.session.add(admin)
        
        # Populate default categories if empty
        if not PortalCategory.query.first():
            default_categories = [
                ('school', 'School', 'Educational facilities from 1st to 10th standard.'),
                ('medical', 'Medical', 'Primary hospital and healthcare.'),
                ('sarapanch', 'Sarapanch', 'Office of the Sarapanch.'),
                ('president', 'President', 'Office of the Village President.'),
                ('culture', 'Culture', 'Vibrant traditions, Danda Yatra, and other Odia festivals.'),
                ('temples', 'Temples', 'Baba Kapileswar Shiv, Maa Ramchandi, and other revered shrines.'),
                ('agriculture', 'Agriculture', 'Fertile lands, paddy fields, and our farming heritage.')
            ]
            for c_id, c_title, c_desc in default_categories:
                db.session.add(PortalCategory(id=c_id, title=c_title, description=c_desc))
                
        # Initialize Visitor Counter if empty
        if not VisitorCount.query.first():
            db.session.add(VisitorCount(id=1, count=100))

        # Seed default Mandi prices if empty
        if not MandiPrice.query.first():
            default_prices = [
                ('Paddy (Dhan)', '₹2,183 / Qtl', 'Quintal', 'Nayagarh Mandi'),
                ('Moong Dal', '₹8,500 / Qtl', 'Quintal', 'Nayagarh Mandi'),
                ('Black Gram (Biri)', '₹7,400 / Qtl', 'Quintal', 'Nayagarh Mandi'),
                ('Groundnut', '₹6,375 / Qtl', 'Quintal', 'Nayagarh Mandi'),
                ('Fresh Vegetables', 'Market Rate', 'Kg', 'Sankhei Local Market')
            ]
            for c_name, p_val, u_val, m_val in default_prices:
                db.session.add(MandiPrice(crop_name=c_name, price=p_val, unit=u_val, market=m_val))

        # Seed sample suggestion if empty
        if not VillageSuggestion.query.first():
            db.session.add(VillageSuggestion(
                title='Solar Street Lights in Main Canal Road',
                name='Ramesh Sahoo',
                category='Infrastructure',
                description='Request to install solar street lights along the canal road for night safety.',
                status='Under Review'
            ))

        # Seed default Homepage Ticker events if empty
        if not Event.query.first():
            default_events = [
                ('Festival', 'Grand Danda Yatra celebrations approaching in April 2027'),
                ('Notice', 'Gram Sabha meeting organized at Panchayat Office to discuss village development'),
                ('Development', 'Revenue Inspector (RI) office setup is currently in progress near the village entrance')
            ]
            for tag_val, desc_val in default_events:
                db.session.add(Event(tag=tag_val, description=desc_val))

        # Clean up any lingering <br> or &lt;br&gt; tags in SiteContent
        about_item = SiteContent.query.get('home_about')
        if about_item and ('<br>' in about_item.title or '&lt;br&gt;' in about_item.title or '<br/>' in about_item.title):
            about_item.title = about_item.title.replace('<br>', ' ').replace('&lt;br&gt;', ' ').replace('<br/>', ' ').strip()

        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)

