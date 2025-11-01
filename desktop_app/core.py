import os
import sys
import json
import io
from typing import List, Dict, Any, Tuple

# Detect PyInstaller frozen
ROOT = os.path.dirname(__file__)
FROZEN = getattr(sys, 'frozen', False)
APP_HOME = os.path.join(os.path.expanduser("~"), ".student_info_mgmt") if FROZEN else os.path.abspath(os.path.join(ROOT, '..'))
DATA_FILE = os.path.join(APP_HOME, 'data', 'students.json')
EXPORT_DIR = os.path.join(APP_HOME, 'exports')
EXPORT_METADATA = os.path.join(EXPORT_DIR, 'exports.json')

STUDENT_FIELDS = ['id','name','gender','age','college','classnum','plcstatus','phone','province','parphone']
STUDENT_LABELS = {
    'id': '学号',
    'name': '姓名',
    'gender': '性别',
    'age': '年龄',
    'college': '学院',
    'classnum': '班级',
    'plcstatus': '政治面貌',
    'phone': '电话',
    'province': '生源省份',
    'parphone': '家长电话',
}


def ensure_data_dir() -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    os.makedirs(EXPORT_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    if not os.path.exists(EXPORT_METADATA):
        with open(EXPORT_METADATA, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def load_students() -> List[Dict[str, Any]]:
    ensure_data_dir()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_students(lst: List[Dict[str, Any]]) -> None:
    ensure_data_dir()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(lst, f, ensure_ascii=False, indent=2)


def calc_gpa(courses: List[Dict[str, Any]]):
    total1 = 0.0
    total2 = 0.0
    for c in courses or []:
        total1 += float(c.get('score', 0)) * float(c.get('credit', 0))
        total2 += float(c.get('credit', 0))
    return (total1 / total2) if total2 > 0 else None


def update_score_in_memory(students: List[Dict[str, Any]], sid: str, course: str, credit: float, score: float) -> bool:
    """Update or insert a course score for the student id in the provided list. Returns True if applied, False if sid not found."""
    for s in students:
        if s.get('id') == sid:
            courses = s.setdefault('courses', [])
            for c in courses:
                if c.get('name') == course:
                    c['credit'] = credit
                    c['score'] = score
                    return True
            courses.append({'name': course, 'credit': credit, 'score': score})
            return True
    return False


def import_scores(file_path: str) -> Tuple[int, int, int]:
    """
    Import scores from file.
    Supports CSV (id,course,credit,score) or whitespace-delimited with the same order.
    Returns (total_lines, applied, skipped_unknown_id).
    """
    ensure_data_dir()
    students = load_students()
    total = 0
    applied = 0
    skipped = 0
    try:
        import csv
        is_csv = str(file_path).lower().endswith('.csv')
        with open(file_path, 'r', encoding='utf-8') as f:
            if is_csv:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    total += 1
                    # Optional header check
                    if total == 1 and len(row) >= 4 and row[0].lower() in ('id','学号'):
                        total -= 1
                        continue
                    try:
                        sid, cname, credit, score = row[0], row[1], float(row[2]), float(row[3])
                    except Exception:
                        skipped += 1
                        continue
                    if update_score_in_memory(students, sid, cname, credit, score):
                        applied += 1
                    else:
                        skipped += 1
            else:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    total += 1
                    parts = line.split()
                    if len(parts) < 4:
                        skipped += 1
                        continue
                    sid, cname, credit_s, score_s = parts[0], parts[1], parts[2], parts[3]
                    try:
                        credit = float(credit_s)
                        score = float(score_s)
                    except Exception:
                        skipped += 1
                        continue
                    if update_score_in_memory(students, sid, cname, credit, score):
                        applied += 1
                    else:
                        skipped += 1
    except Exception:
        raise
    save_students(students)
    return total, applied, skipped


def rank_students() -> List[Dict[str, Any]]:
    """Return ranking list: [{'rank', 'id', 'name', 'gpa'}] sorted by GPA desc."""
    students = load_students()
    enriched = []
    for s in students:
        g = calc_gpa(s.get('courses', []))
        enriched.append({'id': s.get('id',''), 'name': s.get('name',''), 'gpa': g})
    enriched.sort(key=lambda x: (x['gpa'] if x['gpa'] is not None else -1), reverse=True)
    out = []
    r = 1
    for e in enriched:
        out.append({'rank': r, **e})
        r += 1
    return out


def export_students_csv(dest_path: str = None) -> str:
    """Export students to CSV (UTF-8 BOM). If dest_path is provided, write there; else write into EXPORT_DIR.
    Returns the file path written.
    """
    ensure_data_dir()
    students = load_students()
    header_keys = STUDENT_FIELDS
    header_labels = [STUDENT_LABELS.get(k, k) for k in header_keys]
    lines = [','.join(header_labels)]
    def esc(field: Any) -> str:
        f = str(field)
        if ',' in f or '"' in f or '\n' in f:
            f = '"' + f.replace('"','""') + '"'
        return f
    for s in students:
        row = [esc(s.get(k, '')) for k in header_keys]
        lines.append(','.join(row))
    data = ('\ufeff' + '\n'.join(lines)).encode('utf-8')
    import datetime
    if dest_path:
        fpath = dest_path
        os.makedirs(os.path.dirname(fpath) or '.', exist_ok=True)
        fname = os.path.basename(fpath)
    else:
        fname = f"students_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        fpath = os.path.join(EXPORT_DIR, fname)
    with open(fpath, 'wb') as fp:
        fp.write(data)
    # Only update export metadata if saved under EXPORT_DIR
    try:
        if os.path.abspath(os.path.dirname(fpath)) == os.path.abspath(EXPORT_DIR):
            _append_export_meta(fname)
    except Exception:
        pass
    return fpath


def export_students_xlsx(dest_path: str = None) -> str:
    """Export students to XLSX using openpyxl. If dest_path is provided, write there; else write into EXPORT_DIR.
    Returns the file path written.
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font
    ensure_data_dir()
    students = load_students()
    wb = Workbook()
    ws = wb.active
    ws.title = 'Students'
    header_keys = STUDENT_FIELDS
    header_labels = [STUDENT_LABELS.get(k, k) for k in header_keys]
    ws.append(header_labels)
    bold = Font(bold=True)
    for col_cell in ws[1]:
        col_cell.font = bold
    for s in students:
        ws.append([s.get(k, '') for k in header_keys])
    # auto width
    for column_cells in ws.columns:
        values = [str(c.value) if c.value is not None else '' for c in column_cells]
        length = max((len(v) for v in values), default=0)
        ws.column_dimensions[column_cells[0].column_letter].width = min(max(length + 2, 10), 50)
    ws.freeze_panes = 'A2'
    import datetime
    if dest_path:
        fpath = dest_path
        os.makedirs(os.path.dirname(fpath) or '.', exist_ok=True)
        fname = os.path.basename(fpath)
    else:
        fname = f"students_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        fpath = os.path.join(EXPORT_DIR, fname)
    wb.save(fpath)
    # Only update metadata when saving under exports dir
    try:
        if os.path.abspath(os.path.dirname(fpath)) == os.path.abspath(EXPORT_DIR):
            _append_export_meta(fname)
    except Exception:
        pass
    return fpath


def _append_export_meta(fname: str) -> None:
    try:
        with open(EXPORT_METADATA, 'r', encoding='utf-8') as mf:
            meta = json.load(mf)
    except Exception:
        meta = []
    try:
        mtime = int(os.stat(os.path.join(EXPORT_DIR, fname)).st_mtime)
    except Exception:
        mtime = None
    import time
    meta.append({'name': fname, 'mtime': mtime, 'saved_time': int(time.time())})
    try:
        with open(EXPORT_METADATA, 'w', encoding='utf-8') as mf:
            json.dump(meta, mf, ensure_ascii=False, indent=2)
    except Exception:
        pass
