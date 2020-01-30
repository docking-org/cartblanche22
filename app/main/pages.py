from flask import render_template, request, jsonify
from app.main import application
from flask_login import current_user, login_required
from app.data.models.availableVendors import AvailableVendors, UserVendors
from app import db
import json

@application.route('/', methods=['GET'])
@application.route('/cartblanche', methods=['GET'])
def cartblanche():
    return render_template('cartblanche.html')

@application.route('/profile', methods=['GET'])
def profile():
    for i in AvailableVendors.query.all():
        if not UserVendors.query.filter_by(user_id=current_user.id, vendor_id=i.vendor_id).first():
            vendor = UserVendors(user_id=current_user.id, vendor_id=i.vendor_id, priority=i.priority)
            db.session.add(vendor)
            db.session.commit()
    return render_template('profile.html', data=current_user.vendors)

@application.route('/updateVendorPriority', methods=['POST'])
def updateVendorPriority():
    data = request.get_json()
    vendor = UserVendors.query.get(data['id'])
    if int(data['value']) > 100:
        vendor.priority = 100
    elif int(data['value']) < 0:
        vendor.priority = 0
    else:
        vendor.priority = int(data['value'])
    db.session.commit()
    return jsonify({'priority' : vendor.priority})