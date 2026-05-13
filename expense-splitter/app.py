

from flask import Flask, render_template, request, jsonify, session
from splitter import calculate_splits
from whatsapp import send_whatsapp, build_message
import json

app = Flask(__name__)
app.secret_key = 'expense_splitter_secret_key'

# In-memory storage (resets when server restarts)
group_data = {
    'members': [],   # list of {name, phone}
    'expenses': []   # list of {paid_by, amount, description}
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_member', methods=['POST'])
def add_member():
    data = request.json
    name  = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    if not name or not phone:
        return jsonify({'success': False, 'message': 'Name and phone required'})
   
    for m in group_data['members']:
        if m['name'].lower() == name.lower():
            return jsonify({'success': False, 'message': 'Member already exists'})
    group_data['members'].append({'name': name, 'phone': phone})
    return jsonify({'success': True, 'members': group_data['members']})


@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    paid_by     = data.get('paid_by', '').strip()
    amount      = data.get('amount', 0)
    description = data.get('description', '').strip()
    if not paid_by or not amount or not description:
        return jsonify({'success': False, 'message': 'All fields required'})
    group_data['expenses'].append({
        'paid_by': paid_by,
        'amount': float(amount),
        'description': description
    })
    return jsonify({'success': True, 'expenses': group_data['expenses']})


@app.route('/calculate', methods=['GET'])
def calculate():
    if len(group_data['members']) < 2:
        return jsonify({'success': False, 'message': 'Add at least 2 members'})
    if len(group_data['expenses']) < 1:
        return jsonify({'success': False, 'message': 'Add at least 1 expense'})
    members  = [m['name'] for m in group_data['members']]
    result   = calculate_splits(members, group_data['expenses'])
    return jsonify({'success': True, 'result': result})


@app.route('/send_whatsapp', methods=['POST'])
def send_all_whatsapp():
    if len(group_data['members']) < 2:
        return jsonify({'success': False, 'message': 'Add members first'})
    members  = [m['name'] for m in group_data['members']]
    result   = calculate_splits(members, group_data['expenses'])
    sent     = []
    failed   = []
    for member in group_data['members']:
        msg = build_message(
            member['name'],
            result['transactions'],
            result['total'],
            result['share']
        )
        success = send_whatsapp(member['phone'], msg)
        if success:
            sent.append(member['name'])
        else:
            failed.append(member['name'])
    return jsonify({'success': True, 'sent': sent, 'failed': failed})


@app.route('/reset', methods=['POST'])
def reset():
    group_data['members']  = []
    group_data['expenses'] = []
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)