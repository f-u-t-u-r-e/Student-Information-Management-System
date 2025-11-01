import sys
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog,
    QFileDialog, QLabel, QDialog
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

try:
    from .core import (
        load_students, save_students, calc_gpa,
        export_students_csv, export_students_xlsx, STUDENT_FIELDS, STUDENT_LABELS,
        import_scores, rank_students
    )
except Exception:
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from desktop_app.core import (
        load_students, save_students, calc_gpa,
        export_students_csv, export_students_xlsx, STUDENT_FIELDS, STUDENT_LABELS,
        import_scores, rank_students
    )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("学生信息管理系统（桌面版）")
        self.setWindowIcon(QIcon("app.ico"))

        self.table = QTableWidget()
        self.table.setColumnCount(len(STUDENT_FIELDS) + 1)
        headers = [STUDENT_LABELS.get(k, k) for k in STUDENT_FIELDS] + ['gpa']
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.btn_reload = QPushButton("刷新")
        self.btn_add = QPushButton("添加")
        self.btn_edit = QPushButton("编辑")
        self.btn_delete = QPushButton("删除")
        self.btn_save = QPushButton("保存")
        self.btn_export_csv = QPushButton("导出CSV")
        self.btn_export_xlsx = QPushButton("导出XLSX")
        self.btn_manage_scores = QPushButton("管理成绩")
        self.btn_import_scores = QPushButton("导入成绩")
        self.btn_show_rank = QPushButton("成绩排名")

        self.status_label = QLabel()
        self.status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        top = QWidget()
        v = QVBoxLayout(top)
        h = QHBoxLayout()
        h.addWidget(self.btn_reload)
        h.addWidget(self.btn_add)
        h.addWidget(self.btn_edit)
        h.addWidget(self.btn_delete)
        h.addWidget(self.btn_save)
        h.addWidget(self.btn_manage_scores)
        h.addWidget(self.btn_import_scores)
        h.addWidget(self.btn_show_rank)
        h.addStretch(1)
        h.addWidget(self.btn_export_csv)
        h.addWidget(self.btn_export_xlsx)
        v.addLayout(h)
        v.addWidget(self.table)
        v.addWidget(self.status_label)
        self.setCentralWidget(top)

        self.btn_reload.clicked.connect(self.reload)
        self.btn_add.clicked.connect(self.add_student)
        self.btn_edit.clicked.connect(self.edit_student)
        self.btn_delete.clicked.connect(self.delete_student)
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_export_csv.clicked.connect(self.do_export_csv)
        self.btn_export_xlsx.clicked.connect(self.do_export_xlsx)
        self.btn_manage_scores.clicked.connect(self.manage_scores)
        self.btn_import_scores.clicked.connect(self.do_import_scores)
        self.btn_show_rank.clicked.connect(self.show_rank)

        self.students = []
        self.reload()

    def set_status(self, text: str):
        self.status_label.setText(text)

    def reload(self):
        try:
            self.students = load_students()
            self.refresh_table()
            self.set_status("已加载数据")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据失败:\n{e}")

    def refresh_table(self):
        self.table.setRowCount(0)
        for s in self.students:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, key in enumerate(STUDENT_FIELDS):
                item = QTableWidgetItem(str(s.get(key, "")))
                self.table.setItem(row, col, item)
            gpa = calc_gpa(s.get('courses', []))
            self.table.setItem(row, len(STUDENT_FIELDS), QTableWidgetItem("" if gpa is None else f"{gpa:.2f}"))

    def get_selected_index(self):
        rows = sorted(set(i.row() for i in self.table.selectedIndexes()))
        if not rows:
            return None
        return rows[0]

    def add_student(self):
        sid, ok = QInputDialog.getText(self, "添加学生", "学号:")
        if not ok or not sid:
            return
        if any(s.get('id') == sid for s in self.students):
            QMessageBox.warning(self, "提示", "学号已存在")
            return
        name, ok = QInputDialog.getText(self, "添加学生", "姓名:")
        if not ok:
            return
        s = {k: "" for k in STUDENT_FIELDS}
        s['id'] = sid
        s['name'] = name
        s['gender'] = ""
        s['age'] = ""
        s['courses'] = []
        self.students.append(s)
        self.refresh_table()
        self.set_status("已添加，未保存")

    def edit_student(self):
        idx = self.get_selected_index()
        if idx is None:
            QMessageBox.information(self, "提示", "请先选择一行")
            return
        s = self.students[idx]
        for field in ['name', 'gender', 'age', 'college', 'classnum', 'plcstatus', 'phone', 'province', 'parphone']:
            current = str(s.get(field, ""))
            prompt = f"{STUDENT_LABELS.get(field, field)}:"
            val, ok = QInputDialog.getText(self, "编辑信息", prompt, text=current)
            if ok:
                s[field] = val
        self.refresh_table()
        self.set_status("已编辑，未保存")

    def delete_student(self):
        idx = self.get_selected_index()
        if idx is None:
            QMessageBox.information(self, "提示", "请先选择一行")
            return
        sid = self.students[idx].get('id', '')
        if QMessageBox.question(self, "确认删除", f"确定删除学号 {sid} 吗？") == QMessageBox.Yes:
            self.students.pop(idx)
            self.refresh_table()
            self.set_status("已删除，未保存")

    def save_changes(self):
        try:
            for s in self.students:
                try:
                    s['age'] = int(s['age']) if str(s.get('age', '')).strip() != '' else ''
                except Exception:
                    pass
            save_students(self.students)
            self.set_status("已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{e}")

    def do_export_csv(self):
        try:
            # let user choose where to save
            path, _ = QFileDialog.getSaveFileName(self, "导出为 CSV", "", "CSV 文件 (*.csv);;所有文件 (*.*)")
            if not path:
                return
            if not path.lower().endswith('.csv'):
                path = path + '.csv'
            fpath = export_students_csv(path)
            self.set_status(f"CSV 已导出: {fpath}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败:\n{e}")

    def do_export_xlsx(self):
        try:
            path, _ = QFileDialog.getSaveFileName(self, "导出为 XLSX", "", "Excel 工作簿 (*.xlsx);;所有文件 (*.*)")
            if not path:
                return
            if not path.lower().endswith('.xlsx'):
                path = path + '.xlsx'
            fpath = export_students_xlsx(path)
            self.set_status(f"XLSX 已导出: {fpath}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败:\n{e}")

    def manage_scores(self):
        idx = self.get_selected_index()
        if idx is None:
            QMessageBox.information(self, "提示", "请先选择一行")
            return
        s = self.students[idx]
        dlg = ScoresDialog(self, s)
        if dlg.exec() == QDialog.Accepted:
            self.refresh_table()
            self.set_status("成绩已修改，未保存")

    def do_import_scores(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择成绩文件", "", "CSV/TXT (*.csv *.txt);;All (*.*)")
        if not path:
            return
        try:
            total, applied, skipped = import_scores(path)
            self.reload()
            QMessageBox.information(self, "导入完成", f"读取: {total}\n应用: {applied}\n跳过: {skipped}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败:\n{e}")

    def show_rank(self):
        try:
            try:
                for s in self.students:
                    try:
                        s['age'] = int(s['age']) if str(s.get('age', '')).strip() != '' else ''
                    except Exception:
                        pass
                save_students(self.students)
            except Exception:
                pass
            ranks = rank_students()
            dlg = RankDialog(self, ranks)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"排名失败:\n{e}")


class ScoresDialog(QDialog):
    def __init__(self, parent, student: dict):
        super().__init__(parent)
        self.setWindowTitle(f"管理成绩 - {student.get('name','')}({student.get('id','')})")
        self.student = student
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["课程", "学分", "成绩"])
        self.btn_add = QPushButton("添加课程")
        self.btn_edit = QPushButton("编辑课程")
        self.btn_delete = QPushButton("删除课程")
        self.btn_ok = QPushButton("完成")
        self.btn_cancel = QPushButton("取消")
        lay = QVBoxLayout(self)
        h = QHBoxLayout()
        h.addWidget(self.btn_add)
        h.addWidget(self.btn_edit)
        h.addWidget(self.btn_delete)
        h.addStretch(1)
        lay.addLayout(h)
        lay.addWidget(self.table)
        h2 = QHBoxLayout()
        h2.addStretch(1)
        h2.addWidget(self.btn_ok)
        h2.addWidget(self.btn_cancel)
        lay.addLayout(h2)

        self.btn_add.clicked.connect(self.add_course)
        self.btn_edit.clicked.connect(self.edit_course)
        self.btn_delete.clicked.connect(self.delete_course)
        self.btn_ok.clicked.connect(lambda: self.done(QDialog.Accepted))
        self.btn_cancel.clicked.connect(lambda: self.done(QDialog.Rejected))

        self.refresh()

    def refresh(self):
        courses = self.student.setdefault('courses', [])
        self.table.setRowCount(0)
        for c in courses:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(c.get('name',''))))
            self.table.setItem(row, 1, QTableWidgetItem(str(c.get('credit',''))))
            self.table.setItem(row, 2, QTableWidgetItem(str(c.get('score',''))))

    def current_row(self):
        rows = sorted(set(i.row() for i in self.table.selectedIndexes()))
        return rows[0] if rows else None

    def add_course(self):
        cname, ok = QInputDialog.getText(self, "添加课程", "课程名:")
        if not ok or not cname:
            return
        credit_s, ok = QInputDialog.getText(self, "添加课程", "学分:")
        if not ok:
            return
        score_s, ok = QInputDialog.getText(self, "添加课程", "成绩:")
        if not ok:
            return
        try:
            credit = float(credit_s)
            score = float(score_s)
        except Exception:
            QMessageBox.warning(self, "提示", "学分/成绩必须为数字")
            return
        courses = self.student.setdefault('courses', [])
        for c in courses:
            if c.get('name') == cname:
                c['credit'] = credit
                c['score'] = score
                self.refresh(); return
        courses.append({'name': cname, 'credit': credit, 'score': score})
        self.refresh()

    def edit_course(self):
        row = self.current_row()
        if row is None:
            QMessageBox.information(self, "提示", "请选择一行课程")
            return
        courses = self.student.setdefault('courses', [])
        c = courses[row]
        cname, ok = QInputDialog.getText(self, "编辑课程", "课程名:", text=str(c.get('name','')))
        if not ok or not cname:
            return
        credit_s, ok = QInputDialog.getText(self, "编辑课程", "学分:", text=str(c.get('credit','')))
        if not ok:
            return
        score_s, ok = QInputDialog.getText(self, "编辑课程", "成绩:", text=str(c.get('score','')))
        if not ok:
            return
        try:
            credit = float(credit_s)
            score = float(score_s)
        except Exception:
            QMessageBox.warning(self, "提示", "学分/成绩必须为数字")
            return
        c['name'] = cname
        c['credit'] = credit
        c['score'] = score
        self.refresh()

    def delete_course(self):
        row = self.current_row()
        if row is None:
            QMessageBox.information(self, "提示", "请选择一行课程")
            return
        courses = self.student.setdefault('courses', [])
        del courses[row]
        self.refresh()


class RankDialog(QDialog):
    def __init__(self, parent, ranks: list[dict]):
        super().__init__(parent)
        self.setWindowTitle("成绩排名")
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["排名", "学号", "姓名", "GPA"])
        table.setRowCount(0)
        for r in ranks:
            row = table.rowCount(); table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(r.get('rank',''))))
            table.setItem(row, 1, QTableWidgetItem(str(r.get('id',''))))
            table.setItem(row, 2, QTableWidgetItem(str(r.get('name',''))))
            g = r.get('gpa', None)
            table.setItem(row, 3, QTableWidgetItem("" if g is None else f"{g:.2f}"))
        lay = QVBoxLayout(self)
        lay.addWidget(table)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(1100, 600)
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
