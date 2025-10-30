import pkgutil
import importlib.util
# Compatibility shim: Python 3.14 removed pkgutil.get_loader; some libraries still call it.
if not hasattr(pkgutil, 'get_loader'):
    def _compat_get_loader(name):
        spec = importlib.util.find_spec(name)
        return spec.loader if spec else None
    pkgutil.get_loader = _compat_get_loader

from flask import Flask, jsonify, request, render_template, send_file
import json
import os

APP_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(APP_DIR, 'data', 'students.json')

app = Flask(__name__)

def ensure_data_dir():
    d = os.path.dirname(DATA_FILE)
    if not os.path.exists(d):
        os.makedirs(d)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_students():
    ensure_data_dir()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_students(lst):
    ensure_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(lst, f, ensure_ascii=False, indent=2)

def calc_gpa(courses):
    total1 = 0.0
    total2 = 0.0
    for c in courses:
        total1 += c.get('score', 0) * c.get('credit', 0)
        total2 += c.get('credit', 0)
    return total1 / total2 if total2 > 0 else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/students', methods=['GET'])
def api_list_students():
    students = load_students()
    for s in students:
        s['gpa'] = calc_gpa(s.get('courses', []))
    return jsonify(students)

@app.route('/api/students', methods=['POST'])
def api_add_student():
    data = request.json
    students = load_students()
    # check duplicate id
    if any(s['id'] == data['id'] for s in students):
        return jsonify({'error': '学号已存在'}), 400
    data['courses'] = []
    students.append(data)
    save_students(students)
    return jsonify({'ok': True})

@app.route('/api/students/<sid>', methods=['PUT'])
def api_modify_student(sid):
    data = request.json
    students = load_students()
    for s in students:
        if s['id'] == sid:
            # replace fields (except courses)
            for k in ['name','gender','age','college','classnum','plcstatus','phone','province','parphone']:
                if k in data:
                    s[k] = data[k]
            save_students(students)
            return jsonify({'ok': True})
    return jsonify({'error':'未找到该学号'}), 404

@app.route('/api/students/<sid>', methods=['DELETE'])
def api_delete_student(sid):
    students = load_students()
    new = [s for s in students if s['id'] != sid]
    if len(new) == len(students):
        return jsonify({'error':'未找到该学号'}), 404
    save_students(new)
    return jsonify({'ok': True})

@app.route('/api/students/<sid>/scores', methods=['POST'])
def api_add_score(sid):
    data = request.json
    students = load_students()
    for s in students:
        if s['id'] == sid:
            # find course
            for c in s.setdefault('courses', []):
                if c['name'] == data['name']:
                    c['credit'] = data.get('credit', c.get('credit', 0))
                    c['score'] = data.get('score', c.get('score', 0))
                    save_students(students)
                    return jsonify({'ok': True})
            # not found, append
            s.setdefault('courses', []).append({'name': data['name'], 'credit': data.get('credit',0), 'score': data.get('score',0)})
            save_students(students)
            return jsonify({'ok': True})
    return jsonify({'error':'未找到该学号'}), 404

@app.route('/api/rank', methods=['GET'])
def api_rank():
    students = load_students()
    students_sorted = sorted(students, key=lambda s: (calc_gpa(s.get('courses', [])) or -1), reverse=True)
    out = []
    for i,s in enumerate(students_sorted, start=1):
        gpa = calc_gpa(s.get('courses', []))
        out.append({'rank': i, 'id': s['id'], 'name': s.get('name',''), 'gpa': gpa})
    return jsonify(out)

@app.route('/api/export', methods=['GET'])
def api_export():
    ensure_data_dir()
    return send_file(DATA_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
