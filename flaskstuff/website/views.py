# stores standard routes for website
# ie. where users can go to 
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

#from backend.shipping_objects import *
from backend.backend import *

# blueprint defines a bunch of URLs
# naming it 'views' is optional but simplifies things
views = Blueprint('views', __name__)

# define route for homepage
# home() will run whenever user goes to homepage
# (ie. root directory '/')
# view orders from here
@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added', category='success')
    # applies html template to homepage
    # passes user as a variable to be used in template
    return render_template("home.html", user=current_user, shipment=shipment)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    # request is sent as data parameter of request object (not form)
    # request.data is json string sent from index.js

    note = json.loads(request.data) # loads js object defined in index.js
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    
    return jsonify({})  # jsonify empty python dictionary

@views.route('/delete-package', methods=['POST'])
def delete_package():
    # request is sent as data parameter of request object (not form)
    # request.data is json string sent from index.js
    pk_object = json.loads(request.data)    # js object defined in index.js
    pk_id = pk_object['pk_id']
    shipment.remove_package(pk_id)

    return jsonify({})  # jsonify empty python dictionary

# VIEW/EDIT PACKAGE INFO HERE
# consignee/consignee info: name, email, phone, address
# additional info: has batteries, wants insurance
# region view/edit package details
@views.route('/pkg/<int:pk_id>', methods=['GET', 'POST'])
def pk_details(pk_id):
    package = shipment.package(pk_id)
    if request.method == 'POST':
        form_data = request.form
        if form_data['save_btn'] == 'shipper-info':
            package.shipper.name = form_data['shipper_name']
            package.shipper.email = form_data['shipper_email']
            package.shipper.phone = form_data['shipper_phone']
            package.shipper.address = form_data['shipper_address']
        elif form_data['save_btn'] == 'consignee-info':
            package.consignee.name = form_data['consignee_name']
            package.consignee.email = form_data['consignee_email']
            package.consignee.phone = form_data['consignee_phone']
            package.consignee.address = form_data['consignee_address']
        elif form_data['save_btn'] == 'additional-info':
            package.has_batteries = True if 'has_batteries' in form_data else False
            package.insurance = True if 'wants_insurance' in form_data else False
        else:
            raise ValueError("Do not recognize save button value, check pk_details.html")

    return render_template('pk_details.html', pk=package)
# endregion

# region view/edit package details
@views.route('/add-order', methods=['GET', 'POST'])
def add_order():
    global shipment
    if request.method == 'POST':
        form_data = request.form
        action = form_data.get('action')

        customer = None
        package = None
        # NOTE: 
        # default unit for weight is kg
        # delivery address == consignee address
        # fragile option doesn't do anything; need to add to shipping_objects
        if action == 'add':
            # assumes shipper = customer
            name = form_data['shipper-name']
            address = form_data['shipper-address']
            city = form_data['shipper-city']
            state = form_data['shipper-state']
            zipcode = form_data['shipper-zip']
            phone = form_data['shipper-phone']
            email = form_data['shipper-email']
            customer = Customer(name, address, city, state, zipcode, phone, email)
            shipper = Shipper(name, address, city, state, zipcode, phone, email)

            name = form_data['consignee-name']
            address = form_data['consignee-address']
            city = form_data['consignee-city']
            state = form_data['consignee-state']
            zipcode = form_data['consignee-zip']
            phone = form_data['consignee-phone']
            email = form_data['consignee-email']
            consignee = Consignee(name, address, city, state, zipcode, phone, email)
            
            pickup_address = None
            if form_data.get('office-drop-off') == 'drop-off':
                office_dropoff = True
            else:
                office_dropoff = False
                pickup_address = form_data.get('pickup-address')
            # delivery address is consignee address by default
            office_pickup = True if form_data.get('office-pickup') == 'pick-up' else False
            insurance = True if form_data.get('insurance') == 'on' else False
            order = CustomerOrder(customer, "", office_dropoff, office_pickup, insurance)
            order.assign_shipment(shipment)

            # region BOXES
            box_num = form_data.get('number-of-boxes')
            if box_num is None or int(box_num) == 0:
                error_message = "Please enter a valid number of boxes (greater than 0)."
                return render_template('add_order.html', error=error_message)
            
            box_num = int(box_num)
            for i in range(1, box_num+1):
                dim = (form_data.get(f'length-{i}'),
                       form_data.get(f'width-{i}'),
                       form_data.get(f'height-{i}'))
                units = form_data.get(f'units-{i}')
                weight = int(form_data[f'weight-{i}'])
                desc = form_data[f'box-cargo-description-{i}']
                batteries = True if form_data.get(f'box-lithium-batteries-{i}') == 'on' else False
                fragile = True if form_data.get(f'box-fragile-{i}') == 'on' else False  # does nothing
                pk = Package(dim, units, weight, order, shipper, consignee, desc, batteries)
                order.add_package(pk)
            # endregion
            print(shipment) #FIXME not working
            print(order)
            flash('Order added', category='success')
            return render_template('add_order.html')
        elif action == 'cancel':
            return redirect(url_for('views.home'))
        
    autofill_dict = {
        'shipper_name': 'John Doe',
        'shipper_address': '123 street',
        'shipper_city': 'Johns city',
        'shipper_state': 'Johns state',
        'shipper_zip': 'zip code',
        'shipper_phone': '2983748932',
        'shipper_email': 'john@gmail.com',
        'consignee_name': 'somebody',
        'consignee_address': 'address',
        'consignee_city': 'sombody city',
        'consignee_state': 'somebody state',
        'consignee_zip': 'somebody zip',
        'consignee_phone': '4873983',
        'consignee_email': '',
        'office_dropoff': False,
        'office_pickup': False,
        'insurance': True,
        'box_num': 1
    }

    #for i in range(1, autofill_dict['box_num']):
    box = {
        'length': 2,
        'width': 10,
        'height': 3,
        'units': 'inch',
        'weight': 234,
        'description': 'contains items',
        'batteries': True,
        'fragile': False,
    }
    autofill_dict['boxes'] = box
    
    # region chunk
    """
    if form_data['save_btn'] == 'shipper-info':
        package.shipper.name = form_data['shipper_name']
        package.shipper.email = form_data['shipper_email']
        package.shipper.phone = form_data['shipper_phone']
        package.shipper.address = form_data['shipper_address']
    elif form_data['save_btn'] == 'consignee-info':
        package.consignee.name = form_data['consignee_name']
        package.consignee.email = form_data['consignee_email']
        package.consignee.phone = form_data['consignee_phone']
        package.consignee.address = form_data['consignee_address']
    elif form_data['save_btn'] == 'additional-info':
        package.has_batteries = True if 'has_batteries' in form_data else False
        package.insurance = True if 'wants_insurance' in form_data else False
    else:
        raise ValueError("Do not recognize save button value, check pk_details.html")
    """
    # endregion

    return render_template('add_order.html', data=autofill_dict)
# endregion

#TODO:
# use text files to store data
# finish add order and add package routes