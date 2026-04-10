

# """
# =============================================================
#   Abhyuday Bharat Food Cluster — Backend API
#   File  : backend/app.py
# =============================================================
# """
# import smtplib, os, json, socket
# from datetime import datetime
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from functools import wraps
# import secrets


# # ── APP SETUP ──────────────────────────────────────────
# BASE_DIR     = os.path.abspath(os.path.dirname(__file__))
# FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
# DB_DIR       = os.path.join(BASE_DIR, '..', 'database')
# os.makedirs(DB_DIR, exist_ok=True)

# app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
# CORS(app, resources={r"/api/*": {"origins": "*"}})



# # ── EMAIL CONFIG ────────────────────────────────────────
# EMAIL_SENDER    = "food@abhyuday.in"
# EMAIL_PASSWORD  = "J@#nv!$200"
# EMAIL_RECIPIENT = "food@abhyuday.in"
# SMTP_SERVER     = "smtp.office365.com"
# SMTP_PORT       = 587

# # ── MODELS ─────────────────────────────────────────────

# class AdminUser(db.Model):
#     __tablename__ = 'admin_users'
#     id            = db.Column(db.Integer, primary_key=True)
#     username      = db.Column(db.String(80),  unique=True, nullable=False)
#     password_hash = db.Column(db.String(256), nullable=False)
#     created_at    = db.Column(db.DateTime, default=datetime.utcnow)
#     def set_password(self, pw): self.password_hash = generate_password_hash(pw)
#     def check_password(self, pw): return check_password_hash(self.password_hash, pw)
#     def to_dict(self): return {'id': self.id, 'username': self.username}

# class Category(db.Model):
#     __tablename__ = 'categories'
#     id         = db.Column(db.Integer,  primary_key=True)
#     slug       = db.Column(db.String(80),  unique=True, nullable=False)
#     name       = db.Column(db.String(120), nullable=False)
#     emoji      = db.Column(db.String(10),  default='📦')
#     active     = db.Column(db.Boolean,  default=True)
#     sort_order = db.Column(db.Integer,  default=0)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     products   = db.relationship('Product', backref='category_obj', lazy=True,
#                                   foreign_keys='Product.cat_slug',
#                                   primaryjoin='Category.slug == Product.cat_slug')
#     def to_dict(self):
#         return {'id': self.id,'slug': self.slug,'name': self.name,
#                 'emoji': self.emoji,'active': self.active,'sort_order': self.sort_order}

# class Product(db.Model):
#     __tablename__ = 'products'
#     id         = db.Column(db.Integer,  primary_key=True)
#     cat_slug   = db.Column(db.String(80), db.ForeignKey('categories.slug'), nullable=False)
#     sub        = db.Column(db.String(120), nullable=False)
#     name       = db.Column(db.String(200), nullable=False)
#     qty        = db.Column(db.String(200), nullable=False)
#     img        = db.Column(db.String(300), nullable=False)
#     note       = db.Column(db.Text, default='')
#     tags       = db.Column(db.Text, default='[]')
#     active     = db.Column(db.Boolean, default=True)
#     sort_order = db.Column(db.Integer,  default=0)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     @property
#     def tags_list(self):
#         try: return json.loads(self.tags)
#         except: return []
#     @tags_list.setter
#     def tags_list(self, val): self.tags = json.dumps(val)
#     def to_dict(self):
#         return {'id': self.id,'cat': self.cat_slug,'sub': self.sub,'name': self.name,
#                 'qty': self.qty,'img': self.img,'note': self.note,'tags': self.tags_list,
#                 'active': self.active,'sort_order': self.sort_order}

# class Enquiry(db.Model):
#     __tablename__ = 'enquiries'
#     id            = db.Column(db.Integer, primary_key=True)
#     name          = db.Column(db.String(120), nullable=False)
#     company       = db.Column(db.String(200), nullable=False)
#     phone         = db.Column(db.String(40),  nullable=False)
#     email         = db.Column(db.String(200), default='')
#     business_type = db.Column(db.String(100), default='')
#     message       = db.Column(db.Text, default='')
#     seen          = db.Column(db.Boolean, default=False)
#     created_at    = db.Column(db.DateTime, default=datetime.utcnow)
#     def to_dict(self):
#         return {'id': self.id,'name': self.name,'company': self.company,'phone': self.phone,
#                 'email': self.email,'business_type': self.business_type,'message': self.message,
#                 'seen': self.seen,'date': self.created_at.isoformat() if self.created_at else None}

# class SiteContact(db.Model):
#     __tablename__ = 'site_contact'
#     id      = db.Column(db.Integer, primary_key=True)
#     address = db.Column(db.Text, default='')
#     phone   = db.Column(db.String(40), default='')
#     email   = db.Column(db.String(200), default='')
#     hours   = db.Column(db.String(200), default='')
#     def to_dict(self):
#         return {'address': self.address,'phone': self.phone,'email': self.email,'hours': self.hours}

# class AdminSession(db.Model):
#     __tablename__ = 'admin_sessions'
#     id         = db.Column(db.Integer, primary_key=True)
#     token      = db.Column(db.String(64), unique=True, nullable=False)
#     username   = db.Column(db.String(80), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# # ── EMAIL FUNCTION ──────────────────────────────────────

# def send_enquiry_email(enquiry):
#     """
#     Send enquiry notification to food@abhyuday.in via Office 365 SMTP.
#     Prints detailed errors to console so you know exactly what failed.
#     """
#     now_str = datetime.now().strftime('%d %B %Y  %I:%M %p')

#     # ── Check SMTP AUTH is possible first (port 587 reachable?) ──
#     print(f"\n📧 Sending enquiry email for: {enquiry.name} / {enquiry.company}")
#     try:
#         sock = socket.create_connection((SMTP_SERVER, SMTP_PORT), timeout=10)
#         sock.close()
#         print(f"   ✅ Network: {SMTP_SERVER}:{SMTP_PORT} reachable")
#     except Exception as e:
#         print(f"   ❌ Network: Cannot reach {SMTP_SERVER}:{SMTP_PORT}")
#         print(f"      Error: {e}")
#         print(f"      FIX: Your server is blocking outbound port 587.")
#         print(f"           Ask your hosting provider to open it.")
#         return False

#     # ── Build email ────────────────────────────────────────────
#     subject = f"📩 New Enquiry — {enquiry.name} ({enquiry.company})"

#     html_body = f"""<!DOCTYPE html>
# <html><head><meta charset="UTF-8">
# <style>
# body{{margin:0;padding:0;background:#f0e8d4;font-family:Arial,sans-serif;}}
# .wrap{{max-width:600px;margin:24px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,.12);}}
# .head{{background:#3B2A14;padding:22px 28px;}}
# .head h1{{margin:0;color:#F5C842;font-size:19px;}}
# .head p{{margin:4px 0 0;color:rgba(255,255,255,.6);font-size:12px;}}
# .alert{{background:#C0541A;padding:10px 28px;color:#fff;font-size:12px;font-weight:700;letter-spacing:.5px;}}
# .body{{padding:28px;}}
# table{{width:100%;border-collapse:collapse;}}
# tr:nth-child(even){{background:#faf5ec;}}
# td{{padding:12px 14px;font-size:14px;border-bottom:1px solid #f0e8d4;vertical-align:top;}}
# .lbl{{width:35%;color:#7a6a55;font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap;}}
# .val{{color:#1C1208;}}
# .msg{{background:#faf5ec;border-left:4px solid #C0541A;border-radius:4px;padding:14px 16px;margin-top:20px;font-size:14px;color:#3B2A14;line-height:1.75;white-space:pre-wrap;}}
# .reply{{background:#e8f4fd;border:1px solid #bee3f8;border-radius:6px;padding:12px 16px;margin-top:16px;font-size:13px;color:#2b6cb0;}}
# .foot{{background:#1C1208;padding:14px 28px;text-align:center;font-size:11px;color:rgba(255,255,255,.4);}}
# </style></head><body>
# <div class="wrap">
#   <div class="head">
#     <h1>✨ New B2B Enquiry Received</h1>
#     <p>Abhyuday Bharat Food Cluster — Website Contact Form</p>
#   </div>
#   <div class="alert">🔔 ACTION REQUIRED — Reply to this enquiry</div>
#   <div class="body">
#     <table>
#       <tr><td class="lbl">👤 Name</td><td class="val"><strong>{enquiry.name}</strong></td></tr>
#       <tr><td class="lbl">🏢 Company</td><td class="val">{enquiry.company}</td></tr>
#       <tr><td class="lbl">📞 Phone</td><td class="val"><a href="tel:{enquiry.phone}" style="color:#C0541A;">{enquiry.phone}</a></td></tr>
#       <tr><td class="lbl">📧 Email</td><td class="val">{'<a href="mailto:' + enquiry.email + '" style="color:#C0541A;">' + enquiry.email + '</a>' if enquiry.email else '<span style="color:#aaa">Not provided</span>'}</td></tr>
#       <tr><td class="lbl">💼 Business</td><td class="val">{enquiry.business_type or '<span style="color:#aaa">Not specified</span>'}</td></tr>
#       <tr><td class="lbl">📅 Date</td><td class="val">{now_str}</td></tr>
#     </table>
#     <div class="msg"><strong style="font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:#C0541A;">📝 Message / Requirements</strong>
# {enquiry.message or 'No message provided'}</div>
#     {'<div class="reply">💡 <strong>Quick reply:</strong> Hit <em>Reply</em> on this email to respond directly to <strong>' + enquiry.email + '</strong></div>' if enquiry.email else ''}
#   </div>
#   <div class="foot">Abhyuday Bharat Food Cluster LLP · Thaltej, Ahmedabad · food@abhyuday.in · +91 9904166522</div>
# </div></body></html>"""

#     text_body = f"""NEW B2B ENQUIRY — Abhyuday Foods
# {'='*45}
# Name          : {enquiry.name}
# Company       : {enquiry.company}
# Phone         : {enquiry.phone}
# Email         : {enquiry.email or 'Not provided'}
# Business Type : {enquiry.business_type or 'Not specified'}
# Date          : {now_str}
# {'─'*45}
# Message:
# {enquiry.message or 'No message provided'}
# {'='*45}
# Check admin panel at /admin for full list.
# """

#     msg = MIMEMultipart('alternative')
#     msg['From']    = f"Abhyuday Foods <{EMAIL_SENDER}>"
#     msg['To']      = EMAIL_RECIPIENT
#     msg['Subject'] = subject
#     if enquiry.email:
#         msg['Reply-To'] = enquiry.email
#     msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
#     msg.attach(MIMEText(html_body, 'html',  'utf-8'))

#     # ── Office 365 SMTP with detailed error reporting ──────────
#     server = None
#     try:
#         print(f"   Connecting to {SMTP_SERVER}:{SMTP_PORT} ...")
#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)

#         print("   EHLO ...")
#         server.ehlo("abhyuday.in")

#         print("   Starting TLS ...")
#         server.starttls()
#         server.ehlo("abhyuday.in")

#         print(f"   Logging in as {EMAIL_SENDER} ...")
#         server.login(EMAIL_SENDER, EMAIL_PASSWORD)

#         print(f"   Sending message ...")
#         server.send_message(msg)
#         server.quit()

#         print(f"   ✅ EMAIL SENT to {EMAIL_RECIPIENT}")
#         return True

#     except smtplib.SMTPAuthenticationError as e:
#         print(f"\n   ❌ AUTH FAILED — {e}")
#         print("""
#    ┌─ HOW TO FIX ────────────────────────────────────────┐
#    │                                                      │
#    │  Option A — Enable SMTP AUTH in Microsoft 365:      │
#    │  1. Go to admin.microsoft.com                        │
#    │  2. Users → Active users → food@abhyuday.in          │
#    │  3. Click "Mail" tab                                 │
#    │  4. Under "Email apps", click "Manage email apps"   │
#    │  5. Check "Authenticated SMTP" → Save               │
#    │                                                      │
#    │  Option B — If MFA is enabled on the account:       │
#    │  1. Go to myaccount.microsoft.com                    │
#    │  2. Security info → App passwords → New             │
#    │  3. Copy the generated password                     │
#    │  4. Replace EMAIL_PASSWORD in app.py with it        │
#    │                                                      │
#    └──────────────────────────────────────────────────────┘
#         """)
#         return False

#     except smtplib.SMTPConnectError as e:
#         print(f"   ❌ CONNECT FAILED: {e}")
#         print("      Port 587 is being blocked. Try port 25 or 465.")
#         return False

#     except smtplib.SMTPRecipientsRefused as e:
#         print(f"   ❌ RECIPIENT REFUSED: {e}")
#         return False

#     except smtplib.SMTPException as e:
#         print(f"   ❌ SMTP ERROR: {type(e).__name__}: {e}")
#         return False

#     except Exception as e:
#         print(f"   ❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
#         return False

#     finally:
#         try:
#             if server: server.quit()
#         except: pass

# # ── AUTH DECORATOR ─────────────────────────────────────

# def require_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth_header = request.headers.get('Authorization', '')
#         token = auth_header[7:] if auth_header.startswith('Bearer ') else request.args.get('token')
#         if not token:
#             return jsonify({'error': 'Authentication required'}), 401
#         if not AdminSession.query.filter_by(token=token).first():
#             return jsonify({'error': 'Invalid or expired token'}), 401
#         return f(*args, **kwargs)
#     return decorated

# def ok(data=None, msg='Success', **kwargs):
#     p = {'success': True, 'message': msg}
#     if data is not None: p['data'] = data
#     p.update(kwargs)
#     return jsonify(p)

# def err(msg='Error', code=400):
#     return jsonify({'success': False, 'error': msg}), code

# # ── SERVE FRONTEND ─────────────────────────────────────

# @app.route('/')
# def serve_index(): return send_from_directory(FRONTEND_DIR, 'index.html')

# @app.route('/admin')
# @app.route('/admin.html')
# def serve_admin(): return send_from_directory(FRONTEND_DIR, 'admin.html')

# @app.route('/<path:path>')
# def serve_static(path):
#     full = os.path.join(FRONTEND_DIR, path)
#     return send_from_directory(FRONTEND_DIR, path) if os.path.isfile(full) \
#            else send_from_directory(FRONTEND_DIR, 'index.html')

# # ── AUTH ROUTES ────────────────────────────────────────

# @app.route('/api/auth/login', methods=['POST'])
# def login():
#     data = request.get_json() or {}
#     user = AdminUser.query.filter_by(username=data.get('username','').strip()).first()
#     if not user or not user.check_password(data.get('password','')):
#         return err('Invalid credentials', 401)
#     token = secrets.token_hex(32)
#     db.session.add(AdminSession(token=token, username=user.username))
#     db.session.commit()
#     return ok({'token': token, 'username': user.username}, 'Login successful')

# @app.route('/api/auth/logout', methods=['POST'])
# @require_auth
# def logout():
#     auth_header = request.headers.get('Authorization', '')
#     token = auth_header[7:] if auth_header.startswith('Bearer ') else None
#     if token:
#         AdminSession.query.filter_by(token=token).delete()
#         db.session.commit()
#     return ok(msg='Logged out')

# @app.route('/api/auth/change-password', methods=['POST'])
# @require_auth
# def change_password():
#     data = request.get_json() or {}
#     auth_header = request.headers.get('Authorization', '')
#     token = auth_header[7:] if auth_header.startswith('Bearer ') else None
#     sess = AdminSession.query.filter_by(token=token).first()
#     user = AdminUser.query.filter_by(username=sess.username).first() if sess else None
#     if not user: return err('Not authenticated', 401)
#     if not user.check_password(data.get('current_password','')): return err('Current password incorrect')
#     new_pw = data.get('new_password','')
#     if len(new_pw) < 6: return err('New password must be at least 6 characters')
#     user.set_password(new_pw)
#     db.session.commit()
#     return ok(msg='Password updated')

# # ── PUBLIC ROUTES ──────────────────────────────────────

# @app.route('/api/categories', methods=['GET'])
# def get_categories():
#     return ok([c.to_dict() for c in Category.query.filter_by(active=True).order_by(Category.sort_order).all()])

# @app.route('/api/products', methods=['GET'])
# def get_products():
#     q = Product.query.filter_by(active=True)
#     cat = request.args.get('cat')
#     if cat and cat != 'all': q = q.filter_by(cat_slug=cat)
#     return ok([p.to_dict() for p in q.order_by(Product.sort_order, Product.id).all()])

# @app.route('/api/contact', methods=['GET'])
# def get_contact():
#     c = SiteContact.query.first()
#     return ok(c.to_dict() if c else {})

# # ── ENQUIRY SUBMISSION ─────────────────────────────────

# @app.route('/api/enquiry', methods=['POST'])
# def submit_enquiry():
#     data    = request.get_json() or {}
#     name    = (data.get('name')    or '').strip()
#     company = (data.get('company') or '').strip()
#     phone   = (data.get('phone')   or '').strip()

#     if not name or not company or not phone:
#         return err('Name, company and phone are required')

#     # 1. Save to DB first — always works even if email fails
#     enq = Enquiry(
#         name          = name,
#         company       = company,
#         phone         = phone,
#         email         = (data.get('email')         or '').strip(),
#         business_type = (data.get('business_type') or '').strip(),
#         message       = (data.get('message')       or '').strip(),
#     )
#     db.session.add(enq)
#     db.session.commit()
#     print(f"\n✅ Enquiry #{enq.id} saved to database: {name} / {company}")

#     # 2. Send email notification
#     email_sent = send_enquiry_email(enq)

#     result = enq.to_dict()
#     result['email_sent'] = email_sent
#     msg = 'Enquiry received.'
#     msg += ' Email sent to food@abhyuday.in.' if email_sent else ' (Email notification pending — check server logs.)'
#     return ok(result, msg)

# # ── ADMIN ROUTES ───────────────────────────────────────

# @app.route('/api/admin/categories', methods=['GET'])
# @require_auth
# def admin_get_categories():
#     return ok([c.to_dict() for c in Category.query.order_by(Category.sort_order).all()])

# @app.route('/api/admin/categories', methods=['POST'])
# @require_auth
# def admin_add_category():
#     data  = request.get_json() or {}
#     slug  = (data.get('slug') or data.get('id') or '').strip().lower()
#     name  = (data.get('name') or '').strip()
#     if not slug or not name: return err('slug and name required')
#     if Category.query.filter_by(slug=slug).first(): return err(f'Slug "{slug}" exists')
#     max_o = db.session.query(db.func.max(Category.sort_order)).scalar() or 0
#     cat = Category(slug=slug, name=name, emoji=(data.get('emoji') or '📦').strip(),
#                    active=data.get('active', True), sort_order=max_o + 1)
#     db.session.add(cat); db.session.commit()
#     return ok(cat.to_dict(), 'Category added')

# @app.route('/api/admin/categories/<int:cat_id>', methods=['PUT'])
# @require_auth
# def admin_update_category(cat_id):
#     cat  = Category.query.get_or_404(cat_id)
#     data = request.get_json() or {}
#     if 'name'   in data: cat.name   = data['name'].strip()
#     if 'emoji'  in data: cat.emoji  = data['emoji'].strip()
#     if 'active' in data: cat.active = bool(data['active'])
#     new_slug = (data.get('slug') or '').strip().lower()
#     if new_slug and new_slug != cat.slug:
#         if Category.query.filter_by(slug=new_slug).first(): return err(f'Slug in use')
#         Product.query.filter_by(cat_slug=cat.slug).update({'cat_slug': new_slug})
#         cat.slug = new_slug
#     db.session.commit()
#     return ok(cat.to_dict(), 'Category updated')

# @app.route('/api/admin/categories/<int:cat_id>', methods=['DELETE'])
# @require_auth
# def admin_delete_category(cat_id):
#     cat = Category.query.get_or_404(cat_id); db.session.delete(cat); db.session.commit()
#     return ok(msg='Category deleted')

# @app.route('/api/admin/products', methods=['GET'])
# @require_auth
# def admin_get_products():
#     q = Product.query
#     cat = request.args.get('cat')
#     if cat and cat != 'all': q = q.filter_by(cat_slug=cat)
#     return ok([p.to_dict() for p in q.order_by(Product.cat_slug, Product.sort_order).all()])

# @app.route('/api/admin/products', methods=['POST'])
# @require_auth
# def admin_add_product():
#     data = request.get_json() or {}
#     cat,sub,name,qty,img = (data.get(k,'').strip() for k in ['cat','sub','name','qty','img'])
#     if not all([cat,sub,name,qty,img]): return err('cat, sub, name, qty, img required')
#     if not Category.query.filter_by(slug=cat).first(): return err(f'Category "{cat}" not found')
#     max_o = db.session.query(db.func.max(Product.sort_order)).scalar() or 0
#     p = Product(cat_slug=cat, sub=sub, name=name, qty=qty, img=img,
#                 note=(data.get('note') or '').strip(), active=data.get('active', True),
#                 sort_order=max_o + 1)
#     p.tags_list = data.get('tags', [])
#     db.session.add(p); db.session.commit()
#     return ok(p.to_dict(), 'Product added')

# @app.route('/api/admin/products/<int:prod_id>', methods=['PUT'])
# @require_auth
# def admin_update_product(prod_id):
#     p = Product.query.get_or_404(prod_id); data = request.get_json() or {}
#     for k in ['cat','sub','name','qty','img','note']:
#         if k in data: setattr(p, 'cat_slug' if k == 'cat' else k, data[k].strip())
#     if 'active' in data: p.active = bool(data['active'])
#     if 'tags'   in data: p.tags_list = data['tags']
#     p.updated_at = datetime.utcnow(); db.session.commit()
#     return ok(p.to_dict(), 'Product updated')

# @app.route('/api/admin/products/<int:prod_id>', methods=['DELETE'])
# @require_auth
# def admin_delete_product(prod_id):
#     p = Product.query.get_or_404(prod_id); db.session.delete(p); db.session.commit()
#     return ok(msg='Product deleted')

# @app.route('/api/admin/enquiries', methods=['GET'])
# @require_auth
# def admin_get_enquiries():
#     return ok([e.to_dict() for e in Enquiry.query.order_by(Enquiry.created_at.desc()).all()])

# @app.route('/api/admin/enquiries/<int:enq_id>/seen', methods=['PUT'])
# @require_auth
# def admin_mark_seen(enq_id):
#     e = Enquiry.query.get_or_404(enq_id); e.seen = True; db.session.commit()
#     return ok(msg='Marked as seen')

# @app.route('/api/admin/enquiries/mark-all-seen', methods=['PUT'])
# @require_auth
# def admin_mark_all_seen():
#     Enquiry.query.filter_by(seen=False).update({'seen': True}); db.session.commit()
#     return ok(msg='All marked as seen')

# @app.route('/api/admin/enquiries/<int:enq_id>', methods=['DELETE'])
# @require_auth
# def admin_delete_enquiry(enq_id):
#     e = Enquiry.query.get_or_404(enq_id); db.session.delete(e); db.session.commit()
#     return ok(msg='Enquiry deleted')

# @app.route('/api/admin/enquiries', methods=['DELETE'])
# @require_auth
# def admin_clear_enquiries():
#     Enquiry.query.delete(); db.session.commit()
#     return ok(msg='All enquiries cleared')

# @app.route('/api/admin/contact', methods=['GET'])
# @require_auth
# def admin_get_contact():
#     c = SiteContact.query.first(); return ok(c.to_dict() if c else {})

# @app.route('/api/admin/contact', methods=['PUT'])
# @require_auth
# def admin_update_contact():
#     data = request.get_json() or {}
#     c = SiteContact.query.first()
#     if not c: c = SiteContact(); db.session.add(c)
#     for k in ['address','phone','email','hours']:
#         if k in data: setattr(c, k, data[k].strip())
#     db.session.commit(); return ok(c.to_dict(), 'Contact updated')

# @app.route('/api/admin/stats', methods=['GET'])
# @require_auth
# def admin_stats():
#     return ok({'total_products': Product.query.filter_by(active=True).count(),
#                'total_cats': Category.query.filter_by(active=True).count(),
#                'total_enquiries': Enquiry.query.count(),
#                'new_enquiries': Enquiry.query.filter_by(seen=False).count()})

# # ── TEST EMAIL (admin only) ────────────────────────────

# @app.route('/api/admin/test-email', methods=['POST'])
# @require_auth
# def test_email():
#     """Hit this to test if email works without needing a real enquiry form submission."""
#     class FakeEnquiry:
#         name='Test User'; company='Test Pvt Ltd'; phone='+91 9999999999'
#         email='food@abhyuday.in'; business_type='QSR / Cloud Kitchen'
#         message='This is a test. If you see this email, notifications are working!'
#     sent = send_enquiry_email(FakeEnquiry())
#     return ok(msg='Test email sent! Check food@abhyuday.in inbox.') if sent \
#            else err('Test email FAILED. Check console/logs for the exact error.', 500)

# # ── DATABASE SEED ──────────────────────────────────────

# def seed_database():
#     if not AdminUser.query.first():
#         a = AdminUser(username='admin'); a.set_password('admin123'); db.session.add(a)
#         print('  ✓ Admin: admin / admin123')
#     if not SiteContact.query.first():
#         db.session.add(SiteContact(
#             address='1001 & 1020 Time Square Arcade, Thaltej, Ahmedabad – 380059',
#             phone='+91 9904166522', email='food@abhyuday.in', hours='Mon–Sat 9AM–6PM IST'))
#         print('  ✓ Contact info seeded')
#     if not Category.query.first():
#         for slug,name,emoji,o in [
#             ('vegs','Frozen Vegetables','🥦',1),('fries','Frozen Fries','🍟',2),
#             ('snacks','Frozen Snacks','🥟',3),('breads','Breads & Paratha','🫓',4),
#             ('curries','Curries & Gravy','🍛',5),('combo','Combo Meals','🍱',6),
#             ('millet','Millet Based Premixes','🌾',7),('nonmillet','Non-Millet Premixes','🍚',8)]:
#             db.session.add(Category(slug=slug,name=name,emoji=emoji,active=True,sort_order=o))
#         db.session.flush(); print('  ✓ Categories seeded')
#     if not Product.query.first():
#         products = [
#             ('fries','French Fries','Straight Cut French Fries','400g · 1kg · 2.5kg · 10kg','src/products/Stright Fries.png','Classic straight-cut fries.',['Frozen','RTE'],1),
#             ('fries','French Fries','Crinkle Cut French Fries','400g · 1kg · 2.5kg · 10kg','src/products/Crinkle Fries.png','Crinkle-cut for extra crunch.',['Frozen','RTE'],2),
#             ('fries','French Fries','Curly French Fries','400g · 1kg · 2.5kg · 10kg','src/products/Curly Fries.png','Fun spiral curly fries.',['Frozen','RTE'],3),
#             ('fries','Wedges','Potato Wedges','400g · 1kg · 2.5kg · 10kg','src/products/Coted Fries.png','Thick seasoned potato wedges.',['Frozen','RTE'],4),
#             ('vegs','IQF Vegetables','Green Peas','400g · 1kg · 2.5kg · 10kg','src/products/IQF Green Peas.png','Flash-frozen at peak freshness.',['IQF'],1),
#             ('vegs','IQF Vegetables','Sweet Corn','400g · 1kg · 2.5kg · 10kg','src/products/IQF Sweet Corn.png','Golden sweet corn kernels.',['IQF'],2),
#             ('vegs','IQF Vegetables','Mixed Vegetables','400g · 1kg · 2.5kg · 10kg','src/products/IQF Mix Veg.png','Pre-cut blend of vegetables.',['IQF'],3),
#             ('vegs','IQF Vegetables','Okra','400g · 1kg · 2.5kg · 10kg','src/products/IQF Cut Okra (2).png','Tender okra.',['IQF'],4),
#             ('vegs','IQF Vegetables','Cauliflower','400g · 1kg · 2.5kg · 10kg','src/products/IQF Cualiflower.png','Florets frozen at peak freshness.',['IQF'],5),
#             ('vegs','IQF Vegetables','French Beans','400g · 1kg · 2.5kg · 10kg','src/products/IQF French Beans.png','Tender green beans.',['IQF'],6),
#             ('vegs','IQF Vegetables','Carrot','400g · 1kg · 2.5kg · 10kg','src/products/IQF Carrot.png','Diced carrots flash-frozen.',['IQF'],7),
#             ('vegs','IQF Vegetables','Broccoli','400g · 1kg · 2.5kg · 10kg','src/products/IQF Broccoli.png','Premium broccoli florets.',['IQF'],8),
#             ('vegs','IQF Vegetables','Baby Corn','400g · 1kg · 2.5kg · 10kg','src/products/IQF Baby Corn.png','Tender baby corn.',['IQF'],9),
#             ('vegs','IQF Vegetables','Spinach','400g · 1kg · 2.5kg · 10kg','src/products/IQF Spinach.png','Washed chopped spinach.',['IQF'],10),
#             ('snacks','Snacks','Punjabi Samosa','400g · 1kg · 2.5kg · 10kg','src/products/Punjabi Samosa.jpg','Classic Punjabi samosa.',['Frozen','RTE'],1),
#             ('snacks','Snacks','Aloo Tikki','400g · 1kg · 2.5kg · 10kg','src/products/Aloo Tikki.jpg','Ready-to-fry potato tikkis.',['Frozen','RTE'],2),
#             ('snacks','Snacks','Hara Bhara Kabab','400g · 1kg · 2.5kg · 10kg','src/products/Harabhara Kabab.jpg','Spinach and pea-based kabab.',['Frozen'],3),
#             ('breads','Naan','Plain Naan','320g · 400g · 1kg · 5kg','src/products/Plain Naan.jpg','Soft fluffy naans.',['Frozen'],1),
#             ('breads','Naan','Garlic Butter Naan','400g · 1kg · 5kg','src/products/Garlic Butter Naan.jpg','Pre-loaded with garlic butter.',['Frozen'],2),
#             ('breads','Paratha','Plain Paratha','400g · 1kg · 5kg','src/products/Plain Paratha.jpg','Layered flaky plain paratha.',['Frozen'],3),
#             ('breads','Paratha','Aloo Paratha','400g · 1kg · 5kg','src/products/Aloo Paratha.jpg','Classic spiced potato stuffed paratha.',['Frozen'],4),
#             ('breads','Paratha','Lachha Paratha','400g · 1kg · 5kg','src/products/Laccha Paratha.jpg','Crispy multi-layered lachha paratha.',['Frozen'],5),
#             ('breads','Paratha','Malabar Paratha','400g · 1kg · 5kg','src/products/Malabar paratha.png','Soft Kerala-style paratha.',['Frozen'],6),
#             ('curries','Dal','Dal Makhani','300g · 500g · 1kg','src/products/Dal-Makhani.jpg','Slow-cooked creamy dal makhani.',['Frozen'],1),
#             ('curries','Curry','Chole Chana','300g · 500g · 1kg','src/products/Amritsari-Cholle.jpg','Punjabi-style chole.',['Frozen'],2),
#             ('curries','Curry','Rajma Masala','300g · 500g · 1kg','src/products/Shahi-Rajma.jpg','Rich kidney bean curry.',['Frozen'],3),
#             ('curries','Dal','Dal Tadka','300g · 500g · 1kg','src/products/Dal-Tadka.jpg','Classic tempered dal.',['Frozen'],4),
#             ('curries','Curry','Pav Bhaji','300g · 500g · 1kg','src/products/Pav-Bhaji.jpg','Mumbai-style pav bhaji.',['Frozen','RTE'],5),
#             ('combo','Rice','Jeera Rice','300g · 500g · 1kg','src/products/Plain-Rice.jpg','Cumin-tempered rice.',['Frozen'],1),
#             ('combo','Combo Meal','Rice + Dal Makhani','300g · 500g · 1kg','src/products/Rice-With-Dal-Makhani.jpg','Complete meal combo.',['Frozen'],2),
#             ('combo','Combo Meal','Rice + Chole','300g · 500g · 1kg','src/products/Rice-With-Amritsarichole.jpg','High-protein combo.',['Frozen'],3),
#             ('combo','Combo Meal','Rice + Rajma','300g · 500g · 1kg','src/products/Rice-With-Rajma.jpg','Wholesome comfort meal.',['Frozen'],4),
#             ('millet','Idli','Multi Millet Idli','1 KG','src/products/multi millet idli.jpg','Blend of 5 millets.',['Millet'],1),
#             ('millet','Idli','Jowar & Oats Idli','1 KG','src/products/jowar idli.png','Sustained energy.',['Millet'],2),
#             ('millet','Idli','Ragi & Jowar Idli','1 KG','src/products/ragi-idli.png','Excellent for bone health.',['Millet'],3),
#             ('millet','Idli','Quinoa Idli','1 KG','src/products/quinoa idli.jpg','All 9 essential amino acids.',['Millet'],4),
#             ('millet','Dosa','Multi Millet Dosa','1 KG','src/products/multi millet dosa.png','Crispy dosa.',['Millet'],5),
#             ('millet','Dosa','Jowar Dosa','1 KG','src/products/jowar dosa.png','Antioxidant-rich.',['Millet'],6),
#             ('millet','Dosa','Ragi Dosa','1 KG','src/products/Ragi Dosa.png','Finger millet dosa.',['Millet'],7),
#             ('millet','Dosa','Oats Dosa','1 KG','src/products/oats dosa.png','Beta-glucan rich.',['Millet'],8),
#             ('millet','Khichdi','Multi Millet Khichdi','1 KG','src/products/millet_khichdi.png','Complete one-pot meal.',['Millet'],9),
#             ('millet','Khichdi','Foxtail Khichdi','1 KG','src/products/Foxtail-Khichdi.jpg','Low GI.',['Millet'],10),
#             ('millet','Khichdi','Kodo Khichdi','1 KG','src/products/Kodo Khichdi.png','Polyphenol-rich.',['Millet'],11),
#             ('millet','Khichdi','Quinoa Khichdi','1 KG','src/products/Quinoa Khichdi.png','Quinoa + lentil.',['Millet'],12),
#             ('millet','Biryani','Kodo Millet Biryani','1 KG','src/products/Kodo Millet Biryani.png','Whole spice biryani.',['Millet'],13),
#             ('millet','Lemon Rice','Little Millet Lemon Rice','1 KG','src/products/Little Millet Lemon Rice.png','Vitamin C enriched.',['Millet'],14),
#             ('millet','Upma','Jowar Oats Upma','1 KG','src/products/Jowar Oats Upma.png','Sustained energy upma.',['Millet'],15),
#             ('millet','Pongal','Foxtail Millet Sweet Pongal','1 KG','src/products/Foxtail Millet Sweet Pongal.png','Naturally sweetened.',['Millet'],16),
#             ('millet','Sheera','Multi Millet Sheera (Jaggery)','1 KG','src/products/sheera.png','Nutritious jaggery sheera.',['Millet'],17),
#             ('millet','Malt','Ragi Malt','1 KG','src/products/Ragi Malt.png','Sprouted ragi malt.',['Millet'],18),
#             ('millet','Malt','Ragi Malt (Sweet)','1 KG','src/products/Ragi Malt (Sweet).png','Pre-sweetened.',['Millet'],19),
#             ('millet','Chilla','Sprouted Moong Chilla','1 KG','src/products/Sprouted Moong Chilla.png','High protein.',['Millet'],20),
#             ('millet','Chilla','Sprouted Moong + Foxtail Chilla','1 KG','src/products/foxtail chilla.jpg','Low-GI protein chilla.',['Millet'],21),
#             ('millet','Chilla','Sprouted Moong + Jowar Chilla','1 KG','src/products/jowar chilla.png','Gluten-free chilla.',['Millet'],22),
#             ('millet','Soup','Bajra Soup','1 KG','src/products/Bajra Soup.png','Iron-rich bajra soup.',['Millet'],23),
#             ('millet','Pasta Sauce','Oats White Pasta Sauce (GF)','1 KG','src/products/White-Gravy.jpg','GF pasta sauce.',['Millet'],24),
#             ('nonmillet','Sheera','Pineapple Sheera','1 KG','src/products/PINEAPPLE SHEERA.png','Tangy-sweet sheera.',['Premix'],1),
#             ('nonmillet','Halwa','Moong Dal Halwa','1 KG','src/products/moong daal halwa.png','High-protein halwa.',['Premix'],2),
#             ('nonmillet','Halwa','Sooji / Rava Halwa','1 KG','src/products/rava halwa.png','Traditional rava halwa.',['Premix'],3),
#             ('nonmillet','Kheer','Rice Kheer','1 KG','src/products/rice kheer.png','Creamy kheer mix.',['Premix'],4),
#             ('nonmillet','Kheer','Vermicelli Kheer','1 KG','src/products/VERMICELLI KHEER.png','Fast-prep kheer.',['Premix'],5),
#             ('nonmillet','Pasta Sauce','White Sauce for Pasta','1 KG','src/products/White-Gravy.jpg','Bechamel sauce.',['Premix'],6),
#             ('nonmillet','Dosa','Rice Dosa Mix','1 KG','src/products/rice dosa mix.png','Crispy dosas.',['Premix'],7),
#             ('nonmillet','Idli','Rice Idli Mix','1 KG','src/products/sheera.png','Classic idli mix.',['Premix'],8),
#             ('nonmillet','Dhokla','Rice Dhokla Mix','1 KG','src/products/rice_dhokla.png','Gujarati snack.',['Premix'],9),
#             ('nonmillet','Upma','Sooji / Rava Upma','1 KG','src/products/Rava Upma.jpg','Rava upma.',['Premix'],10),
#             ('nonmillet','Khichdi','Rice Masala Khichdi','1 KG','src/products/rice masala khichdi.jpg','Complete meal.',['Premix'],11),
#             ('nonmillet','Biryani','Rice Biryani','1 KG','src/products/Veg-Biryani-Rice.jpg','Biryani blend.',['Premix'],12),
#             ('nonmillet','Lemon Rice','Lemon Rice Mix','1 KG','src/products/Lemon-Rice.jpg','Quick lemon rice.',['Premix'],13),
#         ]
#         for cat,sub,name,qty,img,note,tags,order in products:
#             p = Product(cat_slug=cat,sub=sub,name=name,qty=qty,img=img,note=note,active=True,sort_order=order)
#             p.tags_list = tags; db.session.add(p)
#         print(f'  ✓ {len(products)} products seeded')
#     db.session.commit()

# # ── ENTRY POINT ────────────────────────────────────────

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         seed_database()
#         print('\n✅  Abhyuday Foods backend ready')
#         print('   http://127.0.0.1:5000        ← website')
#         print('   http://127.0.0.1:5000/admin  ← admin panel')
#         print('   http://127.0.0.1:5000/api/   ← REST API')
#         print()
#         print('📧  Email config:')
#         print(f'    {SMTP_SERVER}:{SMTP_PORT}  →  {EMAIL_RECIPIENT}')
#         print()
#         print('🧪  Run test_email.py on this server to diagnose email issues')
#     app.run(debug=True, host='0.0.0.0', port=5000)






"""
=============================================================
  Abhyuday Bharat Food Cluster — Backend API
  File  : backend/app.py
=============================================================
"""
import smtplib, os, json, socket, sys
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets
from dotenv import load_dotenv

# Import db and models from models.py
from backend.models import db, Enquiry
from backend.config import DevelopmentConfig

# Load environment variables
load_dotenv()

# ── APP SETUP ──────────────────────────────────────────
BASE_DIR     = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')
DB_DIR       = os.path.join(BASE_DIR, '..', 'database')
os.makedirs(DB_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

# Apply configuration
app.config.from_object(DevelopmentConfig)

# Initialize db with app
db.init_app(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── EMAIL CONFIG ────────────────────────────────────────
EMAIL_SENDER    = os.environ.get("EMAIL_SENDER", "food@abhyuday.in")
EMAIL_PASSWORD  = os.environ.get("EMAIL_PASSWORD", "J@#nv!$200")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "food@abhyuday.in")
SMTP_SERVER     = os.environ.get("SMTP_SERVER", "smtp.office365.com")
SMTP_PORT       = int(os.environ.get("SMTP_PORT", 587))

# ── MODELS (other models) ──────────────────────────────────────

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)
    def to_dict(self): return {'id': self.id, 'username': self.username}

class Category(db.Model):
    __tablename__ = 'categories'
    id         = db.Column(db.Integer,  primary_key=True)
    slug       = db.Column(db.String(80),  unique=True, nullable=False)
    name       = db.Column(db.String(120), nullable=False)
    emoji      = db.Column(db.String(10),  default='📦')
    active     = db.Column(db.Boolean,  default=True)
    sort_order = db.Column(db.Integer,  default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products   = db.relationship('Product', backref='category_obj', lazy=True,
                                  foreign_keys='Product.cat_slug',
                                  primaryjoin='Category.slug == Product.cat_slug')
    def to_dict(self):
        return {'id': self.id,'slug': self.slug,'name': self.name,
                'emoji': self.emoji,'active': self.active,'sort_order': self.sort_order}

class Product(db.Model):
    __tablename__ = 'products'
    id         = db.Column(db.Integer,  primary_key=True)
    cat_slug   = db.Column(db.String(80), db.ForeignKey('categories.slug'), nullable=False)
    sub        = db.Column(db.String(120), nullable=False)
    name       = db.Column(db.String(200), nullable=False)
    qty        = db.Column(db.String(200), nullable=False)
    img        = db.Column(db.String(300), nullable=False)
    note       = db.Column(db.Text, default='')
    tags       = db.Column(db.Text, default='[]')
    active     = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer,  default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    @property
    def tags_list(self):
        try: return json.loads(self.tags)
        except: return []
    @tags_list.setter
    def tags_list(self, val): self.tags = json.dumps(val)
    def to_dict(self):
        return {'id': self.id,'cat': self.cat_slug,'sub': self.sub,'name': self.name,
                'qty': self.qty,'img': self.img,'note': self.note,'tags': self.tags_list,
                'active': self.active,'sort_order': self.sort_order}

class SiteContact(db.Model):
    __tablename__ = 'site_contact'
    id      = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.Text, default='')
    phone   = db.Column(db.String(40), default='')
    email   = db.Column(db.String(200), default='')
    hours   = db.Column(db.String(200), default='')
    def to_dict(self):
        return {'address': self.address,'phone': self.phone,'email': self.email,'hours': self.hours}

class AdminSession(db.Model):
    __tablename__ = 'admin_sessions'
    id         = db.Column(db.Integer, primary_key=True)
    token      = db.Column(db.String(64), unique=True, nullable=False)
    username   = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ── EMAIL FUNCTION ──────────────────────────────────────

def send_enquiry_email(enquiry):
    """
    Send enquiry notification to food@abhyuday.in via Office 365 SMTP.
    """
    now_str = datetime.now().strftime('%d %B %Y  %I:%M %p')

    print(f"\n📧 Sending enquiry email for: {enquiry.name} / {enquiry.company}")
    
    # ── Build email ────────────────────────────────────────────
    subject = f"📩 New Enquiry — {enquiry.name} ({enquiry.company})"

    html_body = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
body{{margin:0;padding:0;background:#f0e8d4;font-family:Arial,sans-serif;}}
.wrap{{max-width:600px;margin:24px auto;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,.12);}}
.head{{background:#3B2A14;padding:22px 28px;}}
.head h1{{margin:0;color:#F5C842;font-size:19px;}}
.head p{{margin:4px 0 0;color:rgba(255,255,255,.6);font-size:12px;}}
.alert{{background:#C0541A;padding:10px 28px;color:#fff;font-size:12px;font-weight:700;letter-spacing:.5px;}}
.body{{padding:28px;}}
table{{width:100%;border-collapse:collapse;}}
tr:nth-child(even){{background:#faf5ec;}}
td{{padding:12px 14px;font-size:14px;border-bottom:1px solid #f0e8d4;vertical-align:top;}}
.lbl{{width:35%;color:#7a6a55;font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.8px;white-space:nowrap;}}
.val{{color:#1C1208;}}
.msg{{background:#faf5ec;border-left:4px solid #C0541A;border-radius:4px;padding:14px 16px;margin-top:20px;font-size:14px;color:#3B2A14;line-height:1.75;white-space:pre-wrap;}}
.reply{{background:#e8f4fd;border:1px solid #bee3f8;border-radius:6px;padding:12px 16px;margin-top:16px;font-size:13px;color:#2b6cb0;}}
.foot{{background:#1C1208;padding:14px 28px;text-align:center;font-size:11px;color:rgba(255,255,255,.4);}}
</style></head><body>
<div class="wrap">
  <div class="head">
    <h1>✨ New B2B Enquiry Received</h1>
    <p>Abhyuday Bharat Food Cluster — Website Contact Form</p>
  </div>
  <div class="alert">🔔 ACTION REQUIRED — Reply to this enquiry</div>
  <div class="body">
    <table>
      <tr><td class="lbl">👤 Name</td><td class="val"><strong>{enquiry.name}</strong></td></tr>
      <tr><td class="lbl">🏢 Company</td><td class="val">{enquiry.company}</td></tr>
      <tr><td class="lbl">📞 Phone</td><td class="val"><a href="tel:{enquiry.phone}" style="color:#C0541A;">{enquiry.phone}</a></td></tr>
      <tr><td class="lbl">📧 Email</td><td class="val">{'<a href="mailto:' + enquiry.email + '" style="color:#C0541A;">' + enquiry.email + '</a>' if enquiry.email else '<span style="color:#aaa">Not provided</span>'}</td></tr>
      <tr><td class="lbl">💼 Business</td><td class="val">{enquiry.business_type or '<span style="color:#aaa">Not specified</span>'}</td></tr>
      <tr><td class="lbl">📅 Date</td><td class="val">{now_str}</td></tr>
    </table>
    <div class="msg"><strong style="font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:#C0541A;">📝 Message / Requirements</strong>
{enquiry.message or 'No message provided'}</div>
    {'<div class="reply">💡 <strong>Quick reply:</strong> Hit <em>Reply</em> on this email to respond directly to <strong>' + enquiry.email + '</strong></div>' if enquiry.email else ''}
  </div>
  <div class="foot">Abhyuday Bharat Food Cluster LLP · Thaltej, Ahmedabad · food@abhyuday.in · +91 9904166522</div>
</div></body></html>"""

    text_body = f"""NEW B2B ENQUIRY — Abhyuday Foods
{'='*45}
Name          : {enquiry.name}
Company       : {enquiry.company}
Phone         : {enquiry.phone}
Email         : {enquiry.email or 'Not provided'}
Business Type : {enquiry.business_type or 'Not specified'}
Date          : {now_str}
{'─'*45}
Message:
{enquiry.message or 'No message provided'}
{'='*45}
Check admin panel at /admin for full list.
"""

    msg = MIMEMultipart('alternative')
    msg['From']    = f"Abhyuday Foods <{EMAIL_SENDER}>"
    msg['To']      = EMAIL_RECIPIENT
    msg['Subject'] = subject
    if enquiry.email:
        msg['Reply-To'] = enquiry.email
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html',  'utf-8'))

    # ── Send email with error handling ──────────
    server = None
    try:
        print(f"   Connecting to {SMTP_SERVER}:{SMTP_PORT} ...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.ehlo("abhyuday.in")
        server.starttls()
        server.ehlo("abhyuday.in")
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"   ✅ EMAIL SENT to {EMAIL_RECIPIENT}")
        return True
    except Exception as e:
        print(f"   ❌ Email failed: {e}")
        return False
    finally:
        try:
            if server: server.quit()
        except: pass

# ── AUTH DECORATOR ─────────────────────────────────────

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header[7:] if auth_header.startswith('Bearer ') else request.args.get('token')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        if not AdminSession.query.filter_by(token=token).first():
            return jsonify({'error': 'Invalid or expired token'}), 401
        return f(*args, **kwargs)
    return decorated

def ok(data=None, msg='Success', **kwargs):
    p = {'success': True, 'message': msg}
    if data is not None: p['data'] = data
    p.update(kwargs)
    return jsonify(p)

def err(msg='Error', code=400):
    return jsonify({'success': False, 'error': msg}), code

# ── SERVE FRONTEND ─────────────────────────────────────

@app.route('/')
def serve_index(): return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/admin')
@app.route('/admin.html')
def serve_admin(): return send_from_directory(FRONTEND_DIR, 'admin.html')

@app.route('/<path:path>')
def serve_static(path):
    full = os.path.join(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, path) if os.path.isfile(full) \
           else send_from_directory(FRONTEND_DIR, 'index.html')

# ── AUTH ROUTES ────────────────────────────────────────

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = AdminUser.query.filter_by(username=data.get('username','').strip()).first()
    if not user or not user.check_password(data.get('password','')):
        return err('Invalid credentials', 401)
    token = secrets.token_hex(32)
    db.session.add(AdminSession(token=token, username=user.username))
    db.session.commit()
    return ok({'token': token, 'username': user.username}, 'Login successful')

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    auth_header = request.headers.get('Authorization', '')
    token = auth_header[7:] if auth_header.startswith('Bearer ') else None
    if token:
        AdminSession.query.filter_by(token=token).delete()
        db.session.commit()
    return ok(msg='Logged out')

@app.route('/api/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    data = request.get_json() or {}
    auth_header = request.headers.get('Authorization', '')
    token = auth_header[7:] if auth_header.startswith('Bearer ') else None
    sess = AdminSession.query.filter_by(token=token).first()
    user = AdminUser.query.filter_by(username=sess.username).first() if sess else None
    if not user: return err('Not authenticated', 401)
    if not user.check_password(data.get('current_password','')): return err('Current password incorrect')
    new_pw = data.get('new_password','')
    if len(new_pw) < 6: return err('New password must be at least 6 characters')
    user.set_password(new_pw)
    db.session.commit()
    return ok(msg='Password updated')

# ── PUBLIC ROUTES ──────────────────────────────────────

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return ok([c.to_dict() for c in Category.query.filter_by(active=True).order_by(Category.sort_order).all()])

@app.route('/api/products', methods=['GET'])
def get_products():
    q = Product.query.filter_by(active=True)
    cat = request.args.get('cat')
    if cat and cat != 'all': q = q.filter_by(cat_slug=cat)
    return ok([p.to_dict() for p in q.order_by(Product.sort_order, Product.id).all()])

@app.route('/api/contact', methods=['GET'])
def get_contact():
    c = SiteContact.query.first()
    return ok(c.to_dict() if c else {})

# ── ENQUIRY SUBMISSION ─────────────────────────────────

@app.route('/api/enquiry', methods=['POST'])
def submit_enquiry():
    try:
        data = request.get_json() or {}
        
        name    = (data.get('name') or '').strip()
        company = (data.get('company') or '').strip()
        phone   = (data.get('phone') or '').strip()

        if not name or not company or not phone:
            return err('Name, company and phone are required')

        print(f"\n📝 Received enquiry from: {name} / {company} / {phone}")

        # Create enquiry object
        enq = Enquiry(
            name=name,
            company=company,
            phone=phone,
            email=(data.get('email') or '').strip(),
            business_type=(data.get('business_type') or '').strip(),
            message=(data.get('message') or '').strip()
        )

        # Save to database
        db.session.add(enq)
        db.session.commit()
        
        enquiry_id = enq.id
        print(f"✅ Enquiry #{enquiry_id} saved to database successfully!")

        # Try to send email notification (don't fail if email doesn't work)
        email_sent = False
        try:
            email_sent = send_enquiry_email(enq)
        except Exception as email_error:
            print(f"⚠️ Email notification error: {email_error}")

        result = {
            'id': enquiry_id,
            'name': name,
            'company': company,
            'phone': phone,
            'email': enq.email,
            'business_type': enq.business_type,
            'message': enq.message,
            'email_sent': email_sent
        }
        
        msg = 'Enquiry saved successfully!'
        if email_sent:
            msg += ' Email notification sent.'
        else:
            msg += ' (Email notification pending)'
            
        return ok(result, msg)

    except Exception as e:
        print(f"❌ ERROR saving enquiry: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return err(f'Database error: {str(e)}', 500)

# ── ADMIN ROUTES ───────────────────────────────────────

@app.route('/api/admin/categories', methods=['GET'])
@require_auth
def admin_get_categories():
    return ok([c.to_dict() for c in Category.query.order_by(Category.sort_order).all()])

@app.route('/api/admin/categories', methods=['POST'])
@require_auth
def admin_add_category():
    data  = request.get_json() or {}
    slug  = (data.get('slug') or data.get('id') or '').strip().lower()
    name  = (data.get('name') or '').strip()
    if not slug or not name: return err('slug and name required')
    if Category.query.filter_by(slug=slug).first(): return err(f'Slug "{slug}" exists')
    max_o = db.session.query(db.func.max(Category.sort_order)).scalar() or 0
    cat = Category(slug=slug, name=name, emoji=(data.get('emoji') or '📦').strip(),
                   active=data.get('active', True), sort_order=max_o + 1)
    db.session.add(cat); db.session.commit()
    return ok(cat.to_dict(), 'Category added')

@app.route('/api/admin/categories/<int:cat_id>', methods=['PUT'])
@require_auth
def admin_update_category(cat_id):
    cat  = Category.query.get_or_404(cat_id)
    data = request.get_json() or {}
    if 'name'   in data: cat.name   = data['name'].strip()
    if 'emoji'  in data: cat.emoji  = data['emoji'].strip()
    if 'active' in data: cat.active = bool(data['active'])
    new_slug = (data.get('slug') or '').strip().lower()
    if new_slug and new_slug != cat.slug:
        if Category.query.filter_by(slug=new_slug).first(): return err(f'Slug in use')
        Product.query.filter_by(cat_slug=cat.slug).update({'cat_slug': new_slug})
        cat.slug = new_slug
    db.session.commit()
    return ok(cat.to_dict(), 'Category updated')

@app.route('/api/admin/categories/<int:cat_id>', methods=['DELETE'])
@require_auth
def admin_delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id); db.session.delete(cat); db.session.commit()
    return ok(msg='Category deleted')

@app.route('/api/admin/products', methods=['GET'])
@require_auth
def admin_get_products():
    q = Product.query
    cat = request.args.get('cat')
    if cat and cat != 'all': q = q.filter_by(cat_slug=cat)
    return ok([p.to_dict() for p in q.order_by(Product.cat_slug, Product.sort_order).all()])

@app.route('/api/admin/products', methods=['POST'])
@require_auth
def admin_add_product():
    data = request.get_json() or {}
    cat,sub,name,qty,img = (data.get(k,'').strip() for k in ['cat','sub','name','qty','img'])
    if not all([cat,sub,name,qty,img]): return err('cat, sub, name, qty, img required')
    if not Category.query.filter_by(slug=cat).first(): return err(f'Category "{cat}" not found')
    max_o = db.session.query(db.func.max(Product.sort_order)).scalar() or 0
    p = Product(cat_slug=cat, sub=sub, name=name, qty=qty, img=img,
                note=(data.get('note') or '').strip(), active=data.get('active', True),
                sort_order=max_o + 1)
    p.tags_list = data.get('tags', [])
    db.session.add(p); db.session.commit()
    return ok(p.to_dict(), 'Product added')

@app.route('/api/admin/products/<int:prod_id>', methods=['PUT'])
@require_auth
def admin_update_product(prod_id):
    p = Product.query.get_or_404(prod_id); data = request.get_json() or {}
    for k in ['cat','sub','name','qty','img','note']:
        if k in data: setattr(p, 'cat_slug' if k == 'cat' else k, data[k].strip())
    if 'active' in data: p.active = bool(data['active'])
    if 'tags'   in data: p.tags_list = data['tags']
    p.updated_at = datetime.utcnow(); db.session.commit()
    return ok(p.to_dict(), 'Product updated')

@app.route('/api/admin/products/<int:prod_id>', methods=['DELETE'])
@require_auth
def admin_delete_product(prod_id):
    p = Product.query.get_or_404(prod_id); db.session.delete(p); db.session.commit()
    return ok(msg='Product deleted')

@app.route('/api/admin/enquiries', methods=['GET'])
@require_auth
def admin_get_enquiries():
    enquiries = Enquiry.query.order_by(Enquiry.created_at.desc()).all()
    return ok([e.to_dict() for e in enquiries])

@app.route('/api/admin/enquiries/<int:enq_id>/seen', methods=['PUT'])
@require_auth
def admin_mark_seen(enq_id):
    e = Enquiry.query.get_or_404(enq_id)
    if hasattr(e, 'seen'):
        e.seen = True
        db.session.commit()
    return ok(msg='Marked as seen')

@app.route('/api/admin/enquiries/mark-all-seen', methods=['PUT'])
@require_auth
def admin_mark_all_seen():
    if hasattr(Enquiry, 'seen'):
        Enquiry.query.filter_by(seen=False).update({'seen': True})
        db.session.commit()
    return ok(msg='All marked as seen')

@app.route('/api/admin/enquiries/<int:enq_id>', methods=['DELETE'])
@require_auth
def admin_delete_enquiry(enq_id):
    e = Enquiry.query.get_or_404(enq_id)
    db.session.delete(e)
    db.session.commit()
    return ok(msg='Enquiry deleted')

@app.route('/api/admin/enquiries', methods=['DELETE'])
@require_auth
def admin_clear_enquiries():
    Enquiry.query.delete()
    db.session.commit()
    return ok(msg='All enquiries cleared')

@app.route('/api/admin/contact', methods=['GET'])
@require_auth
def admin_get_contact():
    c = SiteContact.query.first()
    return ok(c.to_dict() if c else {})

@app.route('/api/admin/contact', methods=['PUT'])
@require_auth
def admin_update_contact():
    data = request.get_json() or {}
    c = SiteContact.query.first()
    if not c: 
        c = SiteContact()
        db.session.add(c)
    for k in ['address','phone','email','hours']:
        if k in data: 
            setattr(c, k, data[k].strip())
    db.session.commit()
    return ok(c.to_dict(), 'Contact updated')

@app.route('/api/admin/stats', methods=['GET'])
@require_auth
def admin_stats():
    return ok({
        'total_products': Product.query.filter_by(active=True).count(),
        'total_cats': Category.query.filter_by(active=True).count(),
        'total_enquiries': Enquiry.query.count(),
        'new_enquiries': Enquiry.query.filter_by(seen=False).count() if hasattr(Enquiry, 'seen') else Enquiry.query.count()
    })

# ── TEST EMAIL (admin only) ────────────────────────────

@app.route('/api/admin/test-email', methods=['POST'])
@require_auth
def test_email():
    class FakeEnquiry:
        name='Test User'
        company='Test Pvt Ltd'
        phone='+91 9999999999'
        email='food@abhyuday.in'
        business_type='QSR / Cloud Kitchen'
        message='This is a test. If you see this email, notifications are working!'
    sent = send_enquiry_email(FakeEnquiry())
    return ok(msg='Test email sent!') if sent else err('Test email FAILED', 500)

# ── DATABASE SEED ──────────────────────────────────────

def seed_database():
    with app.app_context():
        # Only seed if tables are empty
        if not AdminUser.query.first():
            a = AdminUser(username='admin')
            a.set_password('admin123')
            db.session.add(a)
            print('  ✓ Admin created: admin / admin123')
        
        if not SiteContact.query.first():
            db.session.add(SiteContact(
                address='1001 & 1020 Time Square Arcade, Thaltej, Ahmedabad – 380059',
                phone='+91 9904166522',
                email='food@abhyuday.in',
                hours='Mon–Sat 9AM–6PM IST'
            ))
            print('  ✓ Contact info seeded')
        
        if not Category.query.first():
            categories = [
                ('vegs', 'Frozen Vegetables', '🥦', 1),
                ('fries', 'Frozen Fries', '🍟', 2),
                ('snacks', 'Frozen Snacks', '🥟', 3),
                ('breads', 'Breads & Paratha', '🫓', 4),
                ('curries', 'Curries & Gravy', '🍛', 5),
                ('combo', 'Combo Meals', '🍱', 6),
                ('millet', 'Millet Based Premixes', '🌾', 7),
                ('nonmillet', 'Non-Millet Premixes', '🍚', 8)
            ]
            for slug, name, emoji, order in categories:
                db.session.add(Category(slug=slug, name=name, emoji=emoji, active=True, sort_order=order))
            print('  ✓ Categories seeded')
        
        db.session.commit()
        print('\n✅ Database seeded successfully!')

# ── ENTRY POINT ────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
        print("\n📊 Database tables created/verified")
        
        # Seed data
        seed_database()
        
        print('\n' + '='*50)
        print('✅ Abhyuday Foods Backend Ready!')
        print('='*50)
        print(f'📍 Website:    http://127.0.0.1:5000')
        print(f'🔧 Admin:      http://127.0.0.1:5000/admin')
        print(f'📡 API:        http://127.0.0.1:5000/api/')
        print(f'💾 Database:   {app.config["SQLALCHEMY_DATABASE_URI"]}')
        print('='*50)
        print('\n📧 Email notifications are configured but won\'t stop the form from working')
        print('   Enquiries will be saved to database regardless of email status.\n')
        
    app.run(debug=True, host='0.0.0.0', port=5000)