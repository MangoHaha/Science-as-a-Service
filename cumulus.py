##!/usr/bin/env python2.7

"""
Cumulus Laboratories
David Kuhta
Feng Gao

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import pdb
import datetime
import ast
from distutils.util import strtobool
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects.postgresql import ARRAY
from flask import Flask, request, render_template, g, redirect, Response, session, url_for, flash, escape, json
import hashlib
from flask_login import LoginManager
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required
from functools import wraps
import json

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = os.urandom(33)
app.jinja_env.add_extension('jinja2.ext.autoescape')

DATABASEURI = "postgresql://dk2723:34n47@104.196.175.120/postgres"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request

    The variable g is globally accessible
    """
    try:
        g.conn = engine.connect()
    except:
        print "uh oh, problem connecting to database"
        import traceback; traceback.print_exc()
        g.conn = None
    g.user = None
    if 'user_id' in session:
        g.user = session['user_id']
    if 'user_id' not in session and request.endpoint not in ('login','static'):
        return redirect(url_for('login'))
    nav_protocol_cursor = g.conn.execute('SELECT id, name FROM Protocols WHERE template = true ORDER BY id');
    g.nav_protocol_list = [{key: value for (key, value) in protocol.items()} for protocol in nav_protocol_cursor]
    nav_protocol_cursor.close()

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass

def admin_required(f):
    @wraps(f)
    def admin_function(*args, **kwargs):
        if session['user_admin'] is False:
            flash("Sorry that page is restricted to admins", 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return admin_function

# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/

@app.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    error = ' '
    try:
        if request.method == 'POST':
            session.pop('user',None)
            user = g.conn.execute("SELECT * FROM users WHERE email = (%s)", request.form['username'])
            password = hashlib.md5(request.form['password'])
            password = password.hexdigest()
            cur_user = user.first()
            user_pw = cur_user[3]
            is_admin = cur_user[4]
            if not cur_user[6]:
              flash("This user is no longer active! ")
              return render_template("loginout/login.html")

            if user_pw == password:
                session['logged_in'] = True
                session['user_id'] = cur_user[0]
                session['user_name'] = cur_user[1]
                session['user_email'] = cur_user[2]
                session['user_admin'] = is_admin
                if is_admin:
                    print "Render Admin"
                    flash("Welcome %s! Time to manage some labs!" % cur_user[1], 'info')
                    return redirect(url_for('admin'))
                else:
                    print "Render customer"
                    flash("Welcome %s! Thanks for using Cumulus Labs" % cur_user[1], 'info')
                    return redirect(url_for('home'))
            else:
                flash("Passwords don't match", 'error')
                print "Passwords don't match"
                return render_template("loginout/login.html")
        else:
            print "Non-POST request"
            return render_template("loginout/login.html")
    except:
        print "Problem"
        return render_template("loginout/login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You are logged out!", 'positive')
    return redirect(url_for('login'))

@app.route('/')
def index():
    return  redirect(url_for('login'))

@app.route('/summary')
def summary():
    return render_template("summary.html")
# CREATE SEQUENCE equipment_id_seq START WITH 17;
# ALTER TABLE equipment ALTER COLUMN id SET DEFAULT nextval('equipment_id_seq');

## Dashboard Routes ##
# Admin Dashboard
@app.route('/admin/dashboard/')
@admin_required
def admin():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """
    #  pdb.set_trace()
    # DEBUG: this is debugging code to see what request looks like
    print request.args

    lab_cursor = g.conn.execute("SELECT * FROM labs ORDER BY id")
    equip_cursor = g.conn.execute("SELECT equipment.id, equipment.lab_id, equipment.mac_address, \
    equipment.function, equipment.description, equipment.serial_number, equipment.manufacturer, \
    equipment.date_purchased, equipment.usage_fee, equipment.active, equipment.last_inspection, \
    labs.name as lab_name \
    FROM equipment JOIN labs ON equipment.id = labs.id ORDER BY equipment.id")
    user_cursor = g.conn.execute("SELECT * FROM users ORDER BY id")
    order_cursor = g.conn.execute("SELECT * FROM orders ORDER BY user_id")
    sample_cursor = g.conn.execute("SELECT * FROM samples ORDER BY id")
    protocol_cursor = g.conn.execute("SELECT * FROM protocols ORDER BY id")

    lab_list = [{key: value for (key, value) in lab.items()} for lab in lab_cursor]
    equip_list = [{key: value for (key, value) in equip.items()} for equip in equip_cursor]
    user_list = [{key: value for (key, value) in user.items()} for user in user_cursor]
    order_list = [{key: value for (key, value) in order.items()} for order in order_cursor]
    sample_list = [{key: value for (key, value) in sample.items()} for sample in sample_cursor]
    protocol_list = [{key: value for (key, value) in protocol.items()} for protocol in protocol_cursor]

    lab_cursor.close()
    equip_cursor.close()
    user_cursor.close()
    order_cursor.close()
    sample_cursor.close()
    protocol_cursor.close()

    context = dict(labs = lab_list, users = user_list, equips = equip_list, orders = order_list, samples = sample_list, protocols = protocol_list)

    return render_template("dashboard/admin.html", **context)

# Customer Dashboard
@app.route('/dashboard/')
def home():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """
    #  pdb.set_trace()
    # DEBUG: this is debugging code to see what request looks like
    print request.args
    print session

    protocol_order_cmd = 'SELECT * FROM Protocols JOIN Orders ON Protocols.id = Orders.protocol_id \
        WHERE Orders.user_id = :user_id ORDER BY Protocols.id';
    protocol_order_cursor = g.conn.execute(text(protocol_order_cmd), user_id = session['user_id']);
    protocol_order_list = [{key: value for (key, value) in protocol_order.items()} for protocol_order in protocol_order_cursor]
    protocol_order_cursor.close()
    context = dict(orders = protocol_order_list, protocols = protocol_order_list)

    return render_template("dashboard/home.html", **context)

# Lab routes
# GET new lab
@app.route('/labs/new', methods=['GET'])
def lab_new():
    return render_template("lab/new.js")

# POST new lab
@app.route('/labs', methods=['POST'])
def create_lab():
    address = request.form['lab[address]']
    usage_fee = request.form['lab[usage_fee]']
    safety_level = request.form['lab[safety_level]']
    name = request.form['lab[name]']
    active = request.form['lab[active]'] or "false"
    area = request.form['lab[area]']
    insert_lab_cmd = 'INSERT INTO labs(address, usage_fee, safety_level,name, active, area) \
                    VALUES (:address, :usage_fee, :safety_level,:name, :active, :area) \
                    RETURNING id';
    results = g.conn.execute(text(insert_lab_cmd), address = address,
        usage_fee = usage_fee, safety_level = safety_level,name = name, active = active, area = area);
    id = results.fetchone()[0]
    context = dict(address = address, usage_fee = usage_fee, safety_level = safety_level, name = name,
    active = strtobool(active), area = area, id = id)
    return render_template("lab/create.js", **context)

# GET existing lab
@app.route('/labs/<int:lab_id>/edit', methods=['GET'])
def edit_lab(lab_id):
    edit_lab_cmd = 'SELECT * FROM labs WHERE id = :lab_id';
    lab_cursor = g.conn.execute(text(edit_lab_cmd), lab_id = lab_id);
    lab = {key: value for (key, value) in lab_cursor.fetchone().items()}
    route = '/labs/%s' % lab['id']
    context = dict(lab = lab, route = route)
    lab_cursor.close()
    return render_template("lab/edit.js", **context)

# PATCH existing lab
@app.route('/labs/<int:lab_id>', methods=['PATCH'])
def update_lab(lab_id):
    address = request.form['lab[address]']
    usage_fee = request.form['lab[usage_fee]']
    safety_level = request.form['lab[safety_level]']
    name = request.form['lab[name]']
    active = request.form['lab[active]']
    area = request.form['lab[area]']
    update_lab_cmd = 'UPDATE labs SET address = :address1, usage_fee = :usage_fee1, \
        safety_level = :safety_level1,name = :name1, active = :active1, area = :area1 WHERE id = :lab_id1';
    results = g.conn.execute(text(update_lab_cmd), address1 = address,
        usage_fee1 = usage_fee, safety_level1 = safety_level, name1 = name, active1 = active,
        area1 = area, lab_id1 = lab_id);
    id = lab_id
    context = dict(address = address, usage_fee = usage_fee, safety_level = safety_level, name = name,
    active = strtobool(active), area = area, id = id)
    return render_template("lab/update.js", **context)

# DELETE existing lab
@app.route('/labs/<int:lab_id>', methods=['DELETE'])
def delete_lab(lab_id):
    delete_lab_cmd = 'DELETE FROM labs WHERE id = :lab_id1';
    g.conn.execute(text(delete_lab_cmd), lab_id1 = lab_id);
    context = dict(lab_id = lab_id)
    return render_template("lab/delete.js", **context)

## Equipment routes ##
@app.route('/equipment/new')
def equipment_new():
    lab_cursor = g.conn.execute("SELECT id, name FROM labs ORDER BY id")
    lab_list = [{key: value for (key, value) in lab.items()} for lab in lab_cursor]
    lab_cursor.close()
    context = dict(labs = lab_list)
    print lab_list
    return render_template("equipment/new.js", **context)

@app.route('/equipment', methods=['POST'])
def create_equipment():
    print request.form
    function = request.form['equipment[function]']
    lab_id = request.form['equipment[lab_id]']
    description = request.form['equipment[description]']
    serial_number = request.form['equipment[serial_number]']
    manufacturer = request.form['equipment[manufacturer]']
    date_purchased = request.form['equipment[date_purchased]']
    mac_address = request.form['equipment[mac_address]']
    usage_fee = request.form['equipment[usage_fee]']
    active = request.form['equipment[active]'] or "false"
    insert_equipment_cmd = 'INSERT INTO equipment(function, description, \
        serial_number, manufacturer, date_purchased, mac_address, usage_fee, active) \
        VALUES (:function, :description, :serial_number, :manufacturer, \
        :date_purchased, :mac_address, :usage_fee, :active) \
        RETURNING id';
    results = g.conn.execute(text(insert_equipment_cmd), function = function,
        description = description, serial_number = serial_number,
        manufacturer = manufacturer, date_purchased = date_purchased,
        mac_address = mac_address, usage_fee = usage_fee, active = active,
        lab_id = lab_id);
    id = results.first()[0]

    # Get lab name
    lab_name_cmd = 'SELECT name FROM labs WHERE id = :lab_id'
    lab_cursor = g.conn.execute(text(lab_name_cmd), lab_id = lab_id)
    lab_name = lab_cursor.first()[0]

    context = dict(function = function, description = description, serial_number = serial_number,
        manufacturer = manufacturer, mac_address = mac_address, usage_fee = usage_fee,
        date_purchased = datetime.datetime.strptime(date_purchased, "%Y-%m-%d"),
        active = strtobool(active), lab_name = lab_name, id = id)
    return render_template("equipment/create.js", **context)

@app.route('/equipment/<int:equipment_id>/edit', methods=['GET'])
def edit_equipment(equipment_id):
    lab_cursor = g.conn.execute("SELECT id, name FROM labs ORDER BY id")
    lab_list = [{key: value for (key, value) in lab.items()} for lab in lab_cursor]
    lab_cursor.close()
    edit_equipment_cmd = 'SELECT * FROM equipment WHERE id = :equipment_id';
    equipment_cursor = g.conn.execute(text(edit_equipment_cmd), equipment_id = equipment_id);
    equipment = {key: value for (key, value) in equipment_cursor.fetchone().items()}
    route = '/equipment/%s' % equipment['id']
    context = dict(labs = lab_list, equipment = equipment, route = route)
    equipment_cursor.close()
    return render_template("equipment/edit.js", **context)

@app.route('/equipment/<int:equipment_id>', methods=['PATCH'])
def update_equipment(equipment_id):
    function = request.form['equipment[function]']
    lab_id = request.form['equipment[lab_id]']
    description = request.form['equipment[description]']
    serial_number = request.form['equipment[serial_number]']
    manufacturer = request.form['equipment[manufacturer]']
    date_purchased = request.form['equipment[date_purchased]']
    mac_address = request.form['equipment[mac_address]']
    usage_fee = request.form['equipment[usage_fee]']
    active = request.form['equipment[active]'] or "false"
    update_equipment_cmd = 'UPDATE equipment SET function = :function, \
        description = :description, serial_number = :serial_number, \
        manufacturer = :manufacturer, date_purchased = :date_purchased, \
        mac_address = :mac_address, usage_fee = :usage_fee, active = :active \
        WHERE id = :equipment_id';
    g.conn.execute(text(update_equipment_cmd), function = function,
        description = description, serial_number = serial_number,
        manufacturer = manufacturer, date_purchased = date_purchased,
        mac_address = mac_address, usage_fee = usage_fee, active = active,
        lab_id = lab_id, equipment_id = equipment_id);
    id = equipment_id

    # Get lab name
    lab_name_cmd = 'SELECT id, name FROM labs WHERE id = :lab_id'
    results = g.conn.execute(text(lab_name_cmd), lab_id = lab_id)
    lab_name = lab_cursor.first()[0]

    context = dict(function = function, description = description, serial_number = serial_number,
        manufacturer = manufacturer, mac_address = mac_address, usage_fee = usage_fee,
        date_purchased = datetime.datetime.strptime(date_purchased, "%Y-%m-%d"),
        active = strtobool(active), lab_name = lab_name, id = id)
    return render_template("equipment/update.js", **context)

@app.route('/equipment/<int:equipment_id>', methods=['DELETE'])
def delete_equipment(equipment_id):
    delete_equipment_cmd = 'DELETE FROM equipment WHERE id = :equipment_id';
    g.conn.execute(text(delete_equipment_cmd), equipment_id = equipment_id);
    context = dict(equipment_id = equipment_id)
    return render_template("equipment/delete.js", **context)

## Order Routes ##
@app.route('/orders/<int:order_id>')
def order_show(protocol_id):
    context = dict(protocol = protocol, instructions = instruction_list)
    return render_template("order/show.html", **context)

## Protocol Routes ##
@app.route('/protocols/<int:protocol_id>')
def show_protocol(protocol_id):
    order_cmd = 'SELECT * FROM orders WHERE protocol_id = :protocol_id';
    order_cursor = g.conn.execute(text(order_cmd), protocol_id = protocol_id);
    order = {key: value for (key, value) in order_cursor.fetchone().items()}
    order_cursor.close()

    protocol_cmd = 'SELECT * FROM protocols WHERE id = :protocol_id';
    protocol_cursor = g.conn.execute(text(protocol_cmd), protocol_id = protocol_id);
    protocol = {key: value for (key, value) in protocol_cursor.first().items()}
    protocol_cursor.close()

    instructions_cmd = 'SELECT instructions.protocol_id, instructions.sequence, \
        instructions.function, instructions.complete, instructions.equipment_id, \
        instructions.description, instructions.approved, protocols.template, \
        orders.status as order_status \
        FROM instructions JOIN protocols ON instructions.protocol_id = protocols.id \
        JOIN orders ON instructions.protocol_id = orders.protocol_id \
        WHERE instructions.protocol_id = :protocol_id ORDER BY instructions.sequence';
    instruction_cursor = g.conn.execute(text(instructions_cmd), protocol_id = protocol_id);
    instruction_list = [{key: value for (key, value) in instruction.items()} for instruction in instruction_cursor]
    instruction_cursor.close()

    ###shield###
    shield_cmd = 'SELECT shields.protocol_id, shields.sequence, \
        shields.seal, shields.reverse, samples.name as sample_name, \
        protocols.template, orders.status as order_status \
        FROM shields JOIN samples ON shields.sample_id = samples.id \
        JOIN protocols ON shields.protocol_id = protocols.id \
        JOIN orders ON shields.protocol_id = orders.protocol_id \
        WHERE shields.protocol_id = :protocol_id ORDER BY sequence';
    shield_cursor = g.conn.execute(text(shield_cmd), protocol_id = protocol_id);
    shield_list = [{key: value for (key, value) in shield.items()} for shield in shield_cursor]
    shield_cursor.close()

    ###incubate###
    incubate_cmd = 'SELECT incubates.protocol_id, incubates.sequence, \
        incubates.duration, incubates.temperature, incubates.shaking, \
        incubates.co2_percent, samples.name as sample_name, protocols.template, \
        orders.status as order_status \
        FROM incubates JOIN samples ON incubates.sample_id = samples.id \
        JOIN protocols ON incubates.protocol_id = protocols.id \
        JOIN orders ON incubates.protocol_id = orders.protocol_id \
        WHERE incubates.protocol_id = :protocol_id ORDER BY sequence';
    incubate_cursor = g.conn.execute(text(incubate_cmd), protocol_id = protocol_id);
    incubate_list = [{key: value for (key, value) in incubate.items()} for incubate in incubate_cursor]
    incubate_cursor.close()

    ###spectros###
    spectro_cmd = 'SELECT spectros.protocol_id, spectros.sequence, spectros.type, \
        spectros.temperature, spectros.duration,spectros.wells, spectros.amplitude, \
        spectros.excitation, spectros.gain, spectros.wavelength, spectros.emission, \
        spectros.orbital, spectros.num_flashes, spectros.sample_id, samples.name as sample_name, \
        protocols.template, orders.status as order_status \
        FROM spectros JOIN samples ON spectros.sample_id = samples.id \
        JOIN protocols ON spectros.protocol_id = protocols.id \
        JOIN orders ON spectros.protocol_id = orders.protocol_id \
        WHERE spectros.protocol_id = :protocol_id ORDER BY sequence';
    spectro_cursor = g.conn.execute(text(spectro_cmd), protocol_id = protocol_id);
    spectro_list = [{key: value for (key, value) in spectro.items()} for spectro in spectro_cursor]
    spectro_cursor.close()

    ###transfers###
    transfer_cmd = 'SELECT transfers.protocol_id, transfers.sequence, transfers.type, \
        transfers.volume, transfers.aspirate_speed, transfers.dispense_speed, \
        transfers.size, transfers.wells, transfers.rows, transfers.columns, \
        transfers.mix_speed_before, transfers.mix_repetition_before, transfers.mix_volume_before, \
        transfers.mix_speed_after, transfers.mix_repetition_after, transfers.mix_volume_after, \
        transfers.from_sample_id, transfers.to_sample_id, transfers.tip_layout, \
        from_sample.name as from_sample_name, to_sample.name as to_sample_name, \
        protocols.template, orders.status as order_status \
        FROM transfers \
        JOIN samples as from_sample ON transfers.from_sample_id = from_sample.id \
        JOIN samples as to_sample ON transfers.to_sample_id = to_sample.id \
        JOIN protocols ON transfers.protocol_id = protocols.id \
        JOIN orders ON transfers.protocol_id = orders.protocol_id \
        WHERE transfers.protocol_id = :protocol_id ORDER BY sequence';
    transfer_cursor = g.conn.execute(text(transfer_cmd), protocol_id = protocol_id);
    transfer_list = [{key: value for (key, value) in transfer.items()} for transfer in transfer_cursor]
    transfer_cursor.close()
    print "Transfer count"
    print len(transfer_list)

    context = dict(order = order, protocol = protocol, instructions = instruction_list, shields = shield_list, incubates = incubate_list, spectros = spectro_list, transfers = transfer_list)
    return render_template("protocol/show.html", **context)

@app.route('/orders/protocol/<int:protocol_id>')
def show_order(protocol_id):
    order_cmd = 'SELECT * FROM orders WHERE protocol_id = :protocol_id';
    order_cursor = g.conn.execute(text(order_cmd), protocol_id = protocol_id);
    order = {key: value for (key, value) in order_cursor.fetchone().items()}
    order_cursor.close()

    protocol_cmd = 'SELECT * FROM protocols WHERE id = :protocol_id';
    protocol_cursor = g.conn.execute(text(protocol_cmd), protocol_id = protocol_id);
    protocol = {key: value for (key, value) in protocol_cursor.fetchone().items()}
    protocol_cursor.close()


    unappr_instr_cmd = 'SELECT * FROM instructions WHERE protocol_id = :protocol_id AND approved = false';
    unappr_instrs_cursor = g.conn.execute(text(unappr_instr_cmd), protocol_id = protocol_id);
    unappr_instrs_list = [{key: value for (key, value) in instr.items()} for instr in unappr_instrs_cursor]
    unappr_instrs_cursor.close()
    if len(unappr_instrs_list) == 0:
        order_approvable = True
    else:
        order_approvable = False

    instructions_cmd = 'SELECT instructions.protocol_id, instructions.sequence, \
        instructions.function, instructions.complete, instructions.equipment_id, \
        instructions.description, instructions.approved, protocols.template, \
        orders.status as order_status \
        FROM instructions JOIN protocols ON instructions.protocol_id = protocols.id \
        JOIN orders ON instructions.protocol_id = orders.protocol_id \
        WHERE instructions.protocol_id = :protocol_id ORDER BY instructions.sequence';
    instruction_cursor = g.conn.execute(text(instructions_cmd), protocol_id = protocol_id);
    instruction_list = [{key: value for (key, value) in instruction.items()} for instruction in instruction_cursor]
    instruction_cursor.close()

    ###shield###
    shield_cmd = 'SELECT shields.protocol_id, shields.sequence, \
        shields.seal, shields.reverse, samples.name as sample_name, \
        protocols.template, orders.status as order_status, instructions.approved \
        FROM shields JOIN samples ON shields.sample_id = samples.id \
        JOIN protocols ON shields.protocol_id = protocols.id \
        JOIN orders ON shields.protocol_id = orders.protocol_id \
        JOIN instructions ON shields.protocol_id = instructions.protocol_id \
        AND shields.sequence = instructions.sequence \
        WHERE shields.protocol_id = :protocol_id ORDER BY sequence';
    shield_cursor = g.conn.execute(text(shield_cmd), protocol_id = protocol_id);
    shield_list = [{key: value for (key, value) in shield.items()} for shield in shield_cursor]
    shield_cursor.close()

    ###incubate###
    incubate_cmd = 'SELECT incubates.protocol_id, incubates.sequence, \
        incubates.duration, incubates.temperature, incubates.shaking, \
        incubates.co2_percent, samples.name as sample_name, protocols.template, \
        orders.status as order_status, instructions.approved \
        FROM incubates JOIN samples ON incubates.sample_id = samples.id \
        JOIN protocols ON incubates.protocol_id = protocols.id \
        JOIN orders ON incubates.protocol_id = orders.protocol_id \
        JOIN instructions ON incubates.protocol_id = instructions.protocol_id \
        AND incubates.sequence = instructions.sequence \
        WHERE incubates.protocol_id = :protocol_id ORDER BY sequence';
    incubate_cursor = g.conn.execute(text(incubate_cmd), protocol_id = protocol_id);
    incubate_list = [{key: value for (key, value) in incubate.items()} for incubate in incubate_cursor]
    incubate_cursor.close()

    ###spectros###
    spectro_cmd = 'SELECT spectros.protocol_id, spectros.sequence, spectros.type, \
        spectros.temperature, spectros.duration,spectros.wells, spectros.amplitude, \
        spectros.excitation, spectros.gain, spectros.wavelength, spectros.emission, \
        spectros.orbital, spectros.num_flashes, spectros.sample_id, samples.name as sample_name, \
        protocols.template, orders.status as order_status, instructions.approved \
        FROM spectros JOIN samples ON spectros.sample_id = samples.id \
        JOIN protocols ON spectros.protocol_id = protocols.id \
        JOIN orders ON spectros.protocol_id = orders.protocol_id \
        JOIN instructions ON spectros.protocol_id = instructions.protocol_id \
        AND spectros.sequence = instructions.sequence \
        WHERE spectros.protocol_id = :protocol_id ORDER BY sequence';
    spectro_cursor = g.conn.execute(text(spectro_cmd), protocol_id = protocol_id);
    spectro_list = [{key: value for (key, value) in spectro.items()} for spectro in spectro_cursor]
    spectro_cursor.close()

    ###transfers###
    transfer_cmd = 'SELECT transfers.protocol_id, transfers.sequence, transfers.type, \
        transfers.volume, transfers.aspirate_speed, transfers.dispense_speed, \
        transfers.size, transfers.wells, transfers.rows, transfers.columns, \
        transfers.mix_speed_before, transfers.mix_repetition_before, transfers.mix_volume_before, \
        transfers.mix_speed_after, transfers.mix_repetition_after, transfers.mix_volume_after, \
        transfers.from_sample_id, transfers.to_sample_id, transfers.tip_layout, \
        from_sample.name as from_sample_name, to_sample.name as to_sample_name, \
        protocols.template, orders.status as order_status, instructions.approved \
        FROM transfers \
        JOIN samples as from_sample ON transfers.from_sample_id = from_sample.id \
        JOIN samples as to_sample ON transfers.to_sample_id = to_sample.id \
        JOIN protocols ON transfers.protocol_id = protocols.id \
        JOIN orders ON transfers.protocol_id = orders.protocol_id \
        JOIN instructions ON transfers.protocol_id = instructions.protocol_id \
        AND transfers.sequence = instructions.sequence \
        WHERE transfers.protocol_id = :protocol_id ORDER BY sequence';
    transfer_cursor = g.conn.execute(text(transfer_cmd), protocol_id = protocol_id);
    transfer_list = [{key: value for (key, value) in transfer.items()} for transfer in transfer_cursor]
    transfer_cursor.close()
    print "transfer list count"
    print len(transfer_list)

    context = dict(order = order, protocol = protocol, instructions = instruction_list,
        shields = shield_list, incubates = incubate_list, spectros = spectro_list,
        transfers = transfer_list, order_approvable=order_approvable)
    return render_template("order/show.html", **context)

## Edit Protocol Instructions
@app.route('/protocol/<int:protocol_id>/instruction/<int:sequence>/<string:type>', methods=['GET'])
def edit_instruction(protocol_id, sequence, type):
    instruction_types = ['shields', 'incubates', 'spectros', 'transfers']
    sample_cursor = g.conn.execute("SELECT id, name FROM samples");
    sample_list = [{key: value for (key, value) in sample.items()} for sample in sample_cursor]
    sample_cursor.close()

    edit_instruction_cmd = 'SELECT * FROM %s \
        WHERE protocol_id = :protocol_id AND sequence = :sequence' % type;
    instruction_cursor = g.conn.execute(text(edit_instruction_cmd),
        protocol_id = protocol_id, sequence = sequence);
    instruction = {key: value for (key, value) in instruction_cursor.first().items()}

    route = '/protocol/%s/instruction/%s/%s' % (instruction['protocol_id'], instruction['sequence'], type)
    context = dict(samples = sample_list, route = route)
    if type == "shields":
        print "Shield instruction"
        context['shields'] = instruction
        return render_template("instruction/shields/edit.js", **context)
    elif type == "incubates":
        print "Incubate instruction"
        context['incubates'] = instruction
        return render_template("instruction/incubates/edit.js", **context)
    elif type == "spectros":
        print "Spectro instruction"
        context['spectros'] = instruction
        return render_template("instruction/spectros/edit.js", **context)
    elif type == "transfers":
        print "Transfer instruction"
        context['transfers'] = instruction
        return render_template("instruction/transfers/edit.js", **context)
    else:
        print "Instruction Error"
        flash("Error: Editing instruction", 'error')
        return redirect(url_for('show_protocol', protocol_id = instruction['protocol_id']))

### Edit Shields ISA Instruction ###
@app.route('/protocol/<int:protocol_id>/instruction/<int:sequence>/shields', methods=['PATCH'])
def update_shield(protocol_id, sequence):
    seal = strtobool(request.form['shields[seal]']) or False
    reverse = strtobool(request.form['shields[reverse]']) or False
    sample_id = request.form['shields[sample_id]']
    update_shield_cmd = 'UPDATE shields SET seal = (:seal)::boolean, \
        reverse = (:reverse)::boolean, sample_id = :sample_id \
        WHERE protocol_id = :protocol_id AND sequence = :sequence';
    results = g.conn.execute(text(update_shield_cmd), protocol_id = protocol_id, sequence = sequence,
        seal = seal, reverse = reverse, sample_id = sample_id);
    order_cmd = 'SELECT * FROM orders WHERE protocol_id = :protocol_id';
    order_cursor = g.conn.execute(text(order_cmd), protocol_id = protocol_id);
    order = {key: value for (key, value) in order_cursor.first().items()}
    # Get sample name
    sample_name_cmd = 'SELECT name FROM samples WHERE id = :sample_id'
    sample_cursor = g.conn.execute(text(sample_name_cmd), sample_id = sample_id)
    sample_name = sample_cursor.first()[0]
    context = dict(protocol_id = protocol_id, sequence = sequence, order = order,
        seal = seal, reverse = reverse, sample_id = sample_id, sample_name=sample_name,
        order_status = order['status'])
    return render_template("instruction/shields/update.js", **context)

### Edit Incubates ISA Instruction ###
@app.route('/protocol/<int:protocol_id>/instruction/<int:sequence>/incubates', methods=['PATCH'])
def update_incubate(protocol_id, sequence):
    print protocol_id
    print sequence
    duration = request.form['incubates[duration]']
    print duration
    temperature = request.form['incubates[temperature]'] or 98
    print temperature
    shaking = request.form['incubates[shaking]'] or "false"
    print shaking
    co2_percent = request.form['incubates[co2_percent]'] or 0.00
    print co2_percent
    sample_id = request.form['incubates[sample_id]']
    print sample_id
    update_incubate_cmd = 'UPDATE incubates SET duration = :duration, \
        temperature = :temperature, sample_id = :sample_id, \
	shaking = :shaking,co2_percent = :co2_percent WHERE protocol_id = :protocol_id AND sequence = :sequence';
    results = g.conn.execute(text(update_incubate_cmd), protocol_id = protocol_id, sequence = sequence,
        duration = duration, temperature = temperature, shaking = shaking, co2_percent = co2_percent, sample_id = sample_id);
    order_cmd = 'SELECT * FROM orders WHERE protocol_id = :protocol_id';
    order_cursor = g.conn.execute(text(order_cmd), protocol_id = protocol_id);
    order = {key: value for (key, value) in order_cursor.first().items()}
    # Get sample name
    sample_name_cmd = 'SELECT name FROM samples WHERE id = :sample_id'
    sample_cursor = g.conn.execute(text(sample_name_cmd), sample_id = sample_id)
    sample_name = sample_cursor.first()[0]
    context = dict(protocol_id = protocol_id, sequence = sequence, order = order,
        duration = duration, temperature = temperature, shaking = shaking,
        co2_percent = co2_percent, sample_id = sample_id, sample_name = sample_name,
        order_status = order['status'])
    return render_template("instruction/incubates/update.js", **context)

### Edit Spectros ISA Instruction ###
@app.route('/protocol/<int:protocol_id>/instruction/<int:sequence>/spectros', methods=['PATCH'])
def update_spectro(protocol_id, sequence):
    print protocol_id
    print sequence
    # Common Required
    type = request.form['spectros[type]']
    print type
    temperature = request.form['spectros[temperature]']
    print temperature
    sample_id = request.form['spectros[sample_id]']
    print sample_id

    # wells = request.form['spectros[wells]']
    # print wells

    # Common Optional shaking elements:
    duration = request.form['spectros[duration]'] or None
    print duration
    amplitude = request.form['spectros[amplitude]'] or None
    print amplitude
    orbital = request.form['spectros[orbital]'] or None
    print orbital

    # Absorbance
    wavelength = request.form['spectros[wavelength]']
    print wavelength

    # fluorescence
    excitation = request.form['spectros[excitation]']
    print excitation
    gain = request.form['spectros[gain]'] or None
    print gain
    emission = request.form['spectros[emission]']
    print emission

    # Absorbance and Fluorescence
    fluor_num_flashes = request.form['spectros[fluor_num_flashes]']
    abs_num_flashes = request.form['spectros[abs_num_flashes]']

    if type == 'fluorescence':
        wavelength = None
        num_flashes = fluor_num_flashes
    elif type == 'absorbance':
        excitation = None
        emission = None
        gain = None
        num_flashes = abs_num_flashes
    else:
        excitation = None
        emission = None
        gain = None
        wavelength = None
        num_flashes = None

    update_spectro_cmd = 'UPDATE spectros SET \
        type = :type, temperature = :temperature, sample_id = :sample_id, \
        excitation = :excitation, emission = :emission, gain = :gain, \
        wavelength = :wavelength, num_flashes = :num_flashes, \
        duration = :duration, amplitude = :amplitude, orbital = :orbital \
        WHERE protocol_id = :protocol_id AND sequence = :sequence';
    results = g.conn.execute(text(update_spectro_cmd), protocol_id = protocol_id,
        sequence = sequence, temperature = temperature, duration = duration,
        type = type, amplitude = amplitude, excitation = excitation, # wells = wells
        gain = gain, wavelength = wavelength, emission = emission,
        orbital = orbital, num_flashes = num_flashes, sample_id = sample_id);
    order_cmd = 'SELECT * FROM orders WHERE protocol_id = :protocol_id';
    order_cursor = g.conn.execute(text(order_cmd), protocol_id = protocol_id);
    order = {key: value for (key, value) in order_cursor.first().items()}
    # Get sample name
    sample_name_cmd = 'SELECT name FROM samples WHERE id = :sample_id'
    sample_cursor = g.conn.execute(text(sample_name_cmd), sample_id = sample_id)
    sample_name = sample_cursor.first()[0]
    context = dict(protocol_id = protocol_id, sequence = sequence, order = order, #, wells = wells
        temperature = temperature,type = type, amplitude = amplitude, duration = duration,
        excitation = excitation, gain = gain, wavelength = wavelength,
        emission = emission, orbital = orbital, num_flashes = num_flashes,
        sample_name = sample_name, order_status = order['status'] );
    return render_template("instruction/spectros/update.js", **context)

### Edit Transfer ISA Instruction ###
@app.route('/protocol/<int:protocol_id>/instruction/<int:sequence>/transfers', methods=['PATCH'])
def update_transfer(protocol_id, sequence):
    print request
    print protocol_id
    print sequence
    type = request.form['transfers[type]']
    print type
    volume = request.form['transfers[volume]']
    print volume
    aspirate_speed = request.form['transfers[aspirate_speed]'] or None
    print aspirate_speed
    dispense_speed = request.form['transfers[dispense_speed]'] or None
    print dispense_speed
    wells = ast.literal_eval(request.form['transfers[wells]']) or []
    print request.form['transfers[wells]']
    print "Wells"
    print wells
    rows = request.form['transfers[rows]']
    print rows
    columns = request.form['transfers[columns]']
    print columns
    mix_speed_before = request.form['transfers[mix_speed_before]'] or None
    print mix_speed_before
    mix_repetition_before = request.form['transfers[mix_repetition_before]'] or None
    print mix_repetition_before
    mix_volume_before = request.form['transfers[mix_volume_before]'] or None
    print mix_volume_before
    mix_speed_after = request.form['transfers[mix_speed_after]'] or None
    print mix_speed_after
    mix_repetition_after = request.form['transfers[mix_repetition_after]'] or None
    print mix_repetition_after
    mix_volume_after = request.form['transfers[mix_volume_after]'] or None
    print mix_volume_after
    from_sample_id = request.form['transfers[from_sample_id]'] or None
    print from_sample_id
    to_sample_id = request.form['transfers[to_sample_id]'] or None
    print to_sample_id
    # tip_layout = request.form['transfers[tip_layout]'] or None
    # print tip_layout
    #tip_layout=:tip_layout, size=:size
    update_transfer_cmd = 'UPDATE transfers SET protocol_id = :protocol_id, sequence = :sequence, type = :type, \
        volume = :volume, aspirate_speed = :aspirate_speed, dispense_speed = :dispense_speed, \
        wells = (:wells)::integer[], rows = :rows, columns = :columns, mix_speed_before = :mix_speed_before, \
        mix_repetition_before = :mix_repetition_before, mix_volume_before = :mix_volume_before, \
        mix_speed_after = :mix_speed_after, mix_repetition_after = :mix_repetition_after, \
        from_sample_id = :from_sample_id, to_sample_id = :to_sample_id \
        WHERE protocol_id = :protocol_id AND sequence = :sequence';
    results = g.conn.execute(text(update_transfer_cmd),
        protocol_id = protocol_id, sequence = sequence, type = type,
        volume = volume, aspirate_speed = aspirate_speed, dispense_speed = dispense_speed,
        wells = wells, rows = rows, columns = columns, mix_speed_before = mix_speed_before,
        mix_repetition_before = mix_repetition_before, mix_volume_before = mix_volume_before,
        mix_speed_after = mix_speed_after, mix_repetition_after = mix_repetition_after,
        from_sample_id = from_sample_id, to_sample_id = to_sample_id
        );
    order_cmd = 'SELECT * FROM orders WHERE protocol_id = :protocol_id';
    order_cursor = g.conn.execute(text(order_cmd), protocol_id = protocol_id);
    order = {key: value for (key, value) in order_cursor.first().items()}

    # Get from sample name
    from_sample_name_cmd = 'SELECT name FROM samples WHERE id = :from_sample_id'
    from_sample_cursor = g.conn.execute(text(from_sample_name_cmd), from_sample_id = from_sample_id)
    from_sample_name = from_sample_cursor.first()[0]

    # Get to sample name
    to_sample_name_cmd = 'SELECT name FROM samples WHERE id = :to_sample_id'
    to_sample_cursor = g.conn.execute(text(to_sample_name_cmd), to_sample_id = to_sample_id)
    to_sample_name = to_sample_cursor.first()[0]

    context = dict(protocol_id = protocol_id, sequence = sequence, order = order, type = type,
        volume = volume, aspirate_speed = aspirate_speed, dispense_speed = dispense_speed,
        wells = wells, rows = rows, columns = columns, mix_speed_before = mix_speed_before,
        mix_repetition_before = mix_repetition_before, mix_volume_before = mix_volume_before,
        mix_speed_after = mix_speed_after, mix_repetition_after = mix_repetition_after,
        from_sample_id = from_sample_id, to_sample_id = to_sample_id,
        from_sample_name = from_sample_name, to_sample_name = to_sample_name,
        order_status = order['status']);
    return render_template("instruction/transfers/update.js", **context)

# Approve Instructions
@app.route('/protocol/<int:protocol_id>/instruction/<int:sequence>/approve', methods=['GET'])
def approve_instruction(protocol_id, sequence):
    appr_instr_cmd = 'UPDATE instructions SET approved = true \
        WHERE protocol_id = :protocol_id AND sequence = :sequence RETURNING protocol_id, sequence';
    result = g.conn.execute(text(appr_instr_cmd), protocol_id = protocol_id, sequence = sequence);
    instr = result.first()
    protocol_id = instr[0]
    sequence = instr[1]
    unappr_instr_cmd = 'SELECT * FROM instructions WHERE protocol_id = :protocol_id AND approved = false';
    unappr_instrs_cursor = g.conn.execute(text(unappr_instr_cmd), protocol_id = protocol_id);
    unappr_instrs_list = [{key: value for (key, value) in instr.items()} for instr in unappr_instrs_cursor]
    unappr_instrs_cursor.close()
    if len(unappr_instrs_list) == 0:
        print "Order approvable"
        print len(unappr_instrs_list)
        order_approvable = True
    else:
        print "Order Unapprovable"
        len(unappr_instrs_list)
        order_approvable = False
    context = dict(protocol_id = protocol_id, sequence = sequence, order_approvable = order_approvable)
    return render_template("instruction/approve/approve.js", **context)

# Unapprove Instructions
@app.route('/protocol/<int:protocol_id>/instruction/<int:sequence>/unapprove', methods=['GET'])
def unapprove_instruction(protocol_id, sequence):
    unappr_instr_cmd = 'UPDATE instructions SET approved = false \
        WHERE protocol_id = :protocol_id AND sequence = :sequence RETURNING protocol_id, sequence';
    result = g.conn.execute(text(unappr_instr_cmd), protocol_id = protocol_id, sequence = sequence);
    instr = result.first()
    protocol_id = instr[0]
    sequence = instr[1]
    unappr_instr_cmd = 'SELECT * FROM instructions WHERE protocol_id = :protocol_id AND approved = false';
    unappr_instrs_cursor = g.conn.execute(text(unappr_instr_cmd), protocol_id = protocol_id);
    unappr_instrs_list = [{key: value for (key, value) in instr.items()} for instr in unappr_instrs_cursor]
    unappr_instrs_cursor.close()
    if len(unappr_instrs_list) == 0:
        print "Order approvable"
        print len(unappr_instrs_list)
        order_approvable = True
    else:
        print "Order Unapprovable"
        len(unappr_instrs_list)
        order_approvable = False
    context = dict(protocol_id = protocol_id, sequence = sequence, order_approvable = order_approvable)
    return render_template("instruction/approve/unapprove.js", **context)

# GET new orders
@app.route('/protocols/<int:template_id>/order', methods=['GET'])
def new_protocol_order(template_id):
    print "template_id"
    print template_id

    # Generate a new PROTOCOL
    proto_copy_cmd = 'INSERT INTO protocols (name, description) \
        SELECT name, description FROM protocols WHERE id = :template_id RETURNING id';
    protocol_copy_id = g.conn.execute(text(proto_copy_cmd), template_id = template_id).first()[0];
    print "Protocol copy id"
    print protocol_copy_id
    print "Protocol copied successfully"

    # Generate a new ORDER
    new_order_cmd = 'INSERT INTO orders(user_id, protocol_id, status, paid) VALUES \
    (:user_id, :protocol_id, :status, :paid)';
    new_order = g.conn.execute(text(new_order_cmd), protocol_id = protocol_copy_id,
        user_id = session['user_id'], status = 'created', paid = 'false');
    new_order.close()
    print "New order generated successfully"

    # Duplicate INSTRUCTIONs
    instr_copy_cmd = 'INSERT INTO instructions(protocol_id, sequence, function, description) \
        SELECT :new_protocol_id, sequence, function, description \
        FROM instructions WHERE protocol_id = :template_id';
    instr_copy_cursor = g.conn.execute(text(instr_copy_cmd), new_protocol_id = protocol_copy_id,
        template_id = template_id);
    instr_copy_cursor.close()
    print "Instruction copies generated successfully"

    # Duplicate Sub-typed ISA INSTRUCTION copies
    # SHIELD Duplicates
    shield_copy_cmd = 'INSERT INTO shields(protocol_id, sequence, seal, reverse, sample_id) \
        SELECT :new_protocol_id, sequence, seal, reverse, sample_id \
        FROM shields WHERE protocol_id = :template_id';
    shield_copy_cursor = g.conn.execute(text(shield_copy_cmd), new_protocol_id = protocol_copy_id,
        template_id = template_id);
    shield_copy_cursor.close()
    print "Shield copies generated successfully"

    # INCUBATE Duplicates
    incubate_copy_cmd = 'INSERT INTO incubates(protocol_id, sequence, duration, temperature, \
        shaking, co2_percent, sample_id) \
        SELECT :new_protocol_id, sequence, duration, temperature, shaking, co2_percent, sample_id \
        FROM incubates WHERE protocol_id = :template_id';
    incubate_copy_cursor = g.conn.execute(text(incubate_copy_cmd), new_protocol_id = protocol_copy_id,
        template_id = template_id);
    incubate_copy_cursor.close()
    print "Incubate copies generated successfully"

    # SPECTROPHOTOMETRIC Duplicates
    spectro_copy_cmd = 'INSERT INTO spectros(protocol_id, sequence, type, temperature, \
    duration, wells, amplitude, excitation, gain, wavelength, emission, orbital, \
    num_flashes, sample_id) \
        SELECT :new_protocol_id, sequence, type, temperature, duration, wells, \
        amplitude, excitation, gain, wavelength, emission, orbital, num_flashes, sample_id \
        FROM spectros WHERE protocol_id = :template_id';
    spectro_copy_cursor = g.conn.execute(text(spectro_copy_cmd), new_protocol_id = protocol_copy_id,
        template_id = template_id);
    spectro_copy_cursor.close()
    print "Spectrophotometric copies generated successfully"

    # TRANSFER Duplicates
    transfer_copy_cmd = 'INSERT INTO transfers(protocol_id, sequence, type, volume, \
        aspirate_speed, dispense_speed, size, wells, rows, columns, \
        mix_speed_before, mix_repetition_before, mix_volume_before, \
        mix_speed_after, mix_repetition_after, mix_volume_after, \
        from_sample_id, to_sample_id, tip_layout) \
        SELECT :new_protocol_id, sequence, type, volume, \
        aspirate_speed, dispense_speed, size, wells, rows, columns, \
        mix_speed_before, mix_repetition_before, mix_volume_before, \
        mix_speed_after, mix_repetition_after, mix_volume_after, \
        from_sample_id, to_sample_id, tip_layout \
        FROM transfers WHERE protocol_id = :template_id';
    transfer_copy_cursor = g.conn.execute(text(transfer_copy_cmd), new_protocol_id = protocol_copy_id,
        template_id = template_id);
    transfer_copy_cursor.close()
    print "Transfer copies generated successfully"

    flash("Order generated successfully", 'positive')
    return redirect(url_for('show_order', protocol_id = protocol_copy_id))

#orders paid
@app.route('/users/<int:user_id>/protocols/<int:protocol_id>/paid', methods=['GET'])
@admin_required
def paid_order(user_id, protocol_id):
    paid_order_cmd = 'UPDATE orders SET paid = true \
        WHERE user_id = :user_id AND protocol_id = :protocol_id RETURNING user_id, protocol_id';
    result = g.conn.execute(text(paid_order_cmd), user_id = user_id, protocol_id = protocol_id);
    order = result.first()
    user_id = order[0]
    protocol_id = order[1]
    context = dict(user_id = user_id, protocol_id = protocol_id)
    return render_template("order/paid/paid.js", **context)

#orders paid
@app.route('/users/<int:user_id>/protocols/<int:protocol_id>/unpaid', methods=['GET'])
@admin_required
def unpaid_order(user_id, protocol_id):
    unpaid_order_cmd = 'UPDATE orders SET paid = false \
        WHERE user_id = :user_id AND protocol_id = :protocol_id RETURNING user_id, protocol_id';
    result = g.conn.execute(text(unpaid_order_cmd), user_id = user_id, protocol_id = protocol_id);
    order = result.first()
    user_id = order[0]
    protocol_id = order[1]
    context = dict(user_id = user_id, protocol_id = protocol_id)
    return render_template("order/paid/unpaid.js", **context)

#orders approved
@app.route('/protocols/<int:protocol_id>/approved', methods=['GET'])
def approve_order(protocol_id):
    unappr_instr_cmd = 'SELECT * FROM instructions WHERE protocol_id = :protocol_id AND approved = false';
    unappr_instrs_cursor = g.conn.execute(text(unappr_instr_cmd), protocol_id = protocol_id);
    unappr_instrs_list = [{key: value for (key, value) in instr.items()} for instr in unappr_instrs_cursor]
    unappr_instrs_cursor.close()
    if len(unappr_instrs_list) == 0:
        approve_order_cmd = "UPDATE orders SET status = 'queuing' \
            WHERE protocol_id = :protocol_id RETURNING protocol_id";
        result = g.conn.execute(text(approve_order_cmd), protocol_id = protocol_id);
        order = result.first()
        flash("Order approved and queuing", 'positive')
        return redirect(url_for('show_order', protocol_id=protocol_id))
    else:
        flash("All instructions are not approved", 'error')
        return redirect(url_for('show_order', protocol_id=protocol_id))

# activate/deactivate users
@app.route('/users/<int:user_id>/activate', methods=['GET'])
@admin_required
def activate_user(user_id):
    activate_user_cmd = 'UPDATE users SET active = true WHERE id = :user_id RETURNING ID';
    result = g.conn.execute(text(activate_user_cmd), user_id = user_id);
    user_id = result.first()[0]
    context = dict(user_id = user_id)
    return render_template("user/active/activate.js", **context)

# activate/deactivate users
@app.route('/users/<int:user_id>/deactivate', methods=['GET'])
@admin_required
def deactivate_user(user_id):
    deactivate_user_cmd = 'UPDATE users SET active = false WHERE id = :user_id RETURNING ID';
    result = g.conn.execute(text(deactivate_user_cmd), user_id = user_id);
    user_id = result.first()[0]
    context = dict(user_id = user_id)
    return render_template("user/active/deactivate.js", **context)

#statistics
@app.route('/stat_func/<string:type>')
@admin_required
def stat_func(type):
  if type == "theoretical_equipment_revenue":
    return redirect(url_for('theoretical_equipment_revenue'))
  elif type == "paid_order_revenue":
    return redirect(url_for('paid_order_revenue'))
  elif type == "spectrophotometric_revenue":
    return redirect(url_for('spectrophotometric_revenue'))
  elif type == "shield_revenue":
    return redirect(url_for('shield_revenue'))
  elif type == "transfer_revenue":
    return redirect(url_for('transfer_revenue'))
  else:
    return redirect(url_for('admin'))

@app.route('/theoretical_equipment_revenue')
@admin_required
def theoretical_equipment_revenue():
  stat_cursor = g.conn.execute("SELECT e.id, e.manufacturer, e.serial_number, e.function, \
   count(i.protocol_id) as operations_performed, ((count(i.protocol_id) * e.usage_fee)/100) as theoretical_revenue \
   FROM Instructions AS i INNER JOIN Equipment AS e ON i.equipment_id = e.id GROUP BY e.id ORDER BY e.id")
  stat_list = [{key: value for (key, value) in stat.items()} for stat in stat_cursor]

  total = 0
  for node in stat_list:
    total = total + int(node.values()[1])

  context = dict( stat = stat_list, total = total)
  stat_cursor.close()
  return render_template("stat/index.html", **context)

@app.route('/paid_order_revenue')
@admin_required
def paid_order_revenue():
  stat_cursor = g.conn.execute("SELECT o.protocol_id as protocol, o.user_id as user, l.id as lab, \
    l.usage_fee as lab_fees, sum(e.usage_fee/100) as equipment_fees, \
    (l.usage_fee + sum(e.usage_fee/100)) as order_revenue FROM Orders AS o INNER JOIN Protocols AS p \
    ON o.protocol_id = p.id INNER JOIN Instructions AS i ON i.protocol_id = p.id INNER JOIN Equipment AS e \
    ON i.equipment_id = e.id INNER JOIN Labs AS l ON e.lab_id = l.id WHERE o.paid = true GROUP BY o.protocol_id,\
    o.user_id, p.lab_id, l.usage_fee, l.id")
  stat_list = [{key: value for (key, value) in stat.items()} for stat in stat_cursor]

  total = 0
  for node in stat_list:
    total = total + int(node.values()[5])

  context = dict( stat = stat_list, total = total)
  stat_cursor.close()

  return render_template("stat/index.html", **context)

@app.route('/spectrophotometric_revenue')
@admin_required
def spectrophotometric_revenue():
  stat_cursor = g.conn.execute("SELECT e.id, e.serial_number, sum(e.usage_fee/100) as revenue FROM Spectros as s INNER JOIN Instructions AS i ON s.protocol_id = i.protocol_id AND s.sequence = i.sequence INNER JOIN Equipment AS e ON i.equipment_id = e.id GROUP BY e.id")
  stat_list = [{key: value for (key, value) in stat.items()} for stat in stat_cursor]

  total = 0
  for node in stat_list:
    total = total + int(node.values()[2])

  context = dict( stat = stat_list, total = total)
  stat_cursor.close()
  return render_template("stat/index.html", **context)

@app.route('/transfer_revenue')
@admin_required
def transfer_revenue():
  stat_cursor = g.conn.execute("SELECT e.id, e.serial_number, sum(e.usage_fee/100) as Revenue FROM Transfers as s INNER JOIN Instructions AS i ON s.protocol_id = i.protocol_id AND s.sequence = i.sequence INNER JOIN Equipment AS e ON i.equipment_id = e.id GROUP BY e.id")
  stat_list = [{key: value for (key, value) in stat.items()} for stat in stat_cursor]

  total = 0
  for node in stat_list:
    total = total + int(node.values()[2])

  context = dict(stat = stat_list, total = total)
  stat_cursor.close()
  return render_template("stat/index.html", **context)

@app.route('/shield_revenue')
@admin_required
def shield_revenue():
  stat_cursor = g.conn.execute("SELECT e.id, e.serial_number, sum(e.usage_fee/100) as revenue FROM shields as s INNER JOIN Instructions AS i ON s.protocol_id = i.protocol_id AND s.sequence = i.sequence INNER JOIN Equipment AS e ON i.equipment_id = e.id GROUP BY e.id")
  stat_list = [{key: value for (key, value) in stat.items()} for stat in stat_cursor]

  total = 0
  for node in stat_list:
    total = total + int(node.values()[2])

  context = dict( stat = stat_list, total = total)
  stat_cursor.close()
  return render_template("stat/index.html", **context)

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """

        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
