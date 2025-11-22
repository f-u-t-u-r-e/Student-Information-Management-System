import sys
import os
from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog,
    QFileDialog, QLabel, QDialog, QLineEdit, QHeaderView, QFormLayout,
    QSpinBox, QComboBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QTimer

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

        # 加载样式表
        self.load_stylesheet()

        # 创建搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 搜索学号、姓名、学院...")
        self.search_box.textChanged.connect(self.filter_table)
        self.search_box.setMaximumWidth(300)

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(len(STUDENT_FIELDS) + 1)
        headers = [STUDENT_LABELS.get(k, k) for k in STUDENT_FIELDS] + ['GPA']
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)  # 启用斑马纹

        # 设置表格列宽自适应
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        for i in range(len(STUDENT_FIELDS)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        # 创建按钮
        self.btn_reload = QPushButton("🔄 刷新")
        self.btn_reload.setObjectName("btn_reload")
        self.btn_reload.setToolTip("重新加载数据")

        self.btn_add = QPushButton("➕ 添加")
        self.btn_add.setObjectName("btn_add")
        self.btn_add.setToolTip("添加新学生")

        self.btn_edit = QPushButton("✏️ 编辑")
        self.btn_edit.setToolTip("编辑选中的学生信息")

        self.btn_delete = QPushButton("🗑️ 删除")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.setToolTip("删除选中的学生")

        self.btn_save = QPushButton("💾 保存")
        self.btn_save.setObjectName("btn_save")
        self.btn_save.setToolTip("保存所有更改")

        self.btn_export_csv = QPushButton("📄 导出CSV")
        self.btn_export_csv.setObjectName("btn_export_csv")
        self.btn_export_csv.setToolTip("导出为CSV格式")

        self.btn_export_xlsx = QPushButton("📊 导出XLSX")
        self.btn_export_xlsx.setObjectName("btn_export_xlsx")
        self.btn_export_xlsx.setToolTip("导出为Excel格式")

        self.btn_manage_scores = QPushButton("📝 管理成绩")
        self.btn_manage_scores.setToolTip("管理选中学生的课程成绩")

        self.btn_import_scores = QPushButton("📥 导入成绩")
        self.btn_import_scores.setToolTip("从CSV文件导入成绩")

        self.btn_show_rank = QPushButton("🏆 成绩排名")
        self.btn_show_rank.setToolTip("查看学生成绩排名")

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("status_label")
        self.status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # 布局
        top = QWidget()
        v = QVBoxLayout(top)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(10)

        # 顶部工具栏（搜索框和按钮）
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        toolbar.addWidget(self.search_box)
        toolbar.addSpacing(10)
        toolbar.addWidget(self.btn_reload)
        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addWidget(self.btn_save)
        toolbar.addSpacing(10)
        toolbar.addWidget(self.btn_manage_scores)
        toolbar.addWidget(self.btn_import_scores)
        toolbar.addWidget(self.btn_show_rank)
        toolbar.addStretch(1)
        toolbar.addWidget(self.btn_export_csv)
        toolbar.addWidget(self.btn_export_xlsx)

        v.addLayout(toolbar)
        v.addWidget(self.table)
        v.addWidget(self.status_label)
        self.setCentralWidget(top)

        # 连接信号
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
        self.filtered_students = []  # 用于搜索过滤
        self.reload()

    def load_stylesheet(self):
        """加载QSS样式表"""
        try:
            style_path = os.path.join(os.path.dirname(__file__), 'style.qss')
            if os.path.exists(style_path):
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
        except Exception as e:
            print(f"加载样式表失败: {e}")

    def filter_table(self):
        """根据搜索框内容过滤表格"""
        search_text = self.search_box.text().lower()

        if not search_text:
            self.filtered_students = self.students.copy()
        else:
            self.filtered_students = [
                s for s in self.students
                if search_text in str(s.get('id', '')).lower()
                or search_text in str(s.get('name', '')).lower()
                or search_text in str(s.get('college', '')).lower()
                or search_text in str(s.get('classnum', '')).lower()
            ]

        self.refresh_table()

    def set_status(self, text: str, status_type: str = "info"):
        """设置状态栏文本，支持不同状态类型的图标"""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        icon = icons.get(status_type, "ℹ️")
        self.status_label.setText(f"{icon} {text}")

    def reload(self):
        try:
            self.students = load_students()
            self.filtered_students = self.students.copy()
            self.refresh_table()
            self.set_status("数据加载成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据失败:\n{e}")
            self.set_status("数据加载失败", "error")

    def refresh_table(self):
        self.table.setRowCount(0)
        display_students = self.filtered_students if hasattr(self, 'filtered_students') else self.students

        for s in display_students:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, key in enumerate(STUDENT_FIELDS):
                item = QTableWidgetItem(str(s.get(key, "")))
                self.table.setItem(row, col, item)
            gpa = calc_gpa(s.get('courses', []))
            self.table.setItem(row, len(STUDENT_FIELDS), QTableWidgetItem("" if gpa is None else f"{gpa:.2f}"))

        # 更新状态栏显示总数和过滤数
        total = len(self.students)
        shown = len(display_students)
        if shown < total:
            self.set_status(f"显示 {shown}/{total} 条记录", "info")
        else:
            self.set_status(f"共 {total} 条记录", "info")

    def get_selected_index(self):
        rows = sorted(set(i.row() for i in self.table.selectedIndexes()))
        if not rows:
            return None
        # 返回在原始students列表中的索引
        if rows[0] < len(self.filtered_students):
            selected_student = self.filtered_students[rows[0]]
            return self.students.index(selected_student)
        return None

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
        self.filtered_students = self.students.copy()
        self.refresh_table()
        self.set_status(f"已添加学生 {name}，请记得保存", "warning")

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
        self.set_status(f"已编辑学生 {s.get('name', '')}，请记得保存", "warning")

    def delete_student(self):
        idx = self.get_selected_index()
        if idx is None:
            QMessageBox.information(self, "提示", "请先选择一行")
            return
        sid = self.students[idx].get('id', '')
        sname = self.students[idx].get('name', '')
        if QMessageBox.question(self, "确认删除", f"确定删除学号 {sid} ({sname}) 吗？") == QMessageBox.Yes:
            self.students.pop(idx)
            self.filtered_students = self.students.copy()
            self.refresh_table()
            self.set_status(f"已删除学生 {sname}，请记得保存", "warning")

    def save_changes(self):
        try:
            for s in self.students:
                try:
                    s['age'] = int(s['age']) if str(s.get('age', '')).strip() != '' else ''
                except Exception:
                    pass
            save_students(self.students)
            self.set_status("数据保存成功", "success")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{e}")
            self.set_status("保存失败", "error")

    def do_export_csv(self):
        try:
            path, _ = QFileDialog.getSaveFileName(self, "导出为 CSV", "", "CSV 文件 (*.csv);;所有文件 (*.*)")
            if not path:
                return
            if not path.lower().endswith('.csv'):
                path = path + '.csv'
            fpath = export_students_csv(path)
            self.set_status(f"CSV 已导出至: {os.path.basename(fpath)}", "success")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败:\n{e}")
            self.set_status("CSV 导出失败", "error")

    def do_export_xlsx(self):
        try:
            path, _ = QFileDialog.getSaveFileName(self, "导出为 XLSX", "", "Excel 工作簿 (*.xlsx);;所有文件 (*.*)")
            if not path:
                return
            if not path.lower().endswith('.xlsx'):
                path = path + '.xlsx'
            fpath = export_students_xlsx(path)
            self.set_status(f"XLSX 已导出至: {os.path.basename(fpath)}", "success")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败:\n{e}")
            self.set_status("XLSX 导出失败", "error")

    def manage_scores(self):
        idx = self.get_selected_index()
        if idx is None:
            QMessageBox.information(self, "提示", "请先选择一行")
            return
        s = self.students[idx]
        dlg = ScoresDialog(self, s)
        if dlg.exec() == QDialog.Accepted:
            self.refresh_table()
            self.set_status(f"已修改 {s.get('name', '')} 的成绩，请记得保存", "warning")

    def do_import_scores(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择成绩文件", "", "CSV/TXT (*.csv *.txt);;All (*.*)")
        if not path:
            return
        try:
            total, applied, skipped = import_scores(path)
            self.reload()
            QMessageBox.information(self, "导入完成", f"读取: {total}\n应用: {applied}\n跳过: {skipped}")
            self.set_status(f"成绩导入完成: {applied}/{total}", "success")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败:\n{e}")
            self.set_status("成绩导入失败", "error")

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
        self.setWindowTitle(f"📝 管理成绩 - {student.get('name','')} ({student.get('id','')})")
        self.setMinimumSize(600, 400)
        self.student = student

        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["课程", "学分", "成绩"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # 创建按钮
        self.btn_add = QPushButton("➕ 添加课程")
        self.btn_add.setObjectName("btn_add")
        self.btn_edit = QPushButton("✏️ 编辑课程")
        self.btn_delete = QPushButton("🗑️ 删除课程")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_ok = QPushButton("✅ 完成")
        self.btn_ok.setObjectName("btn_save")
        self.btn_cancel = QPushButton("❌ 取消")

        # 布局
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        # 按钮栏
        h = QHBoxLayout()
        h.setSpacing(8)
        h.addWidget(self.btn_add)
        h.addWidget(self.btn_edit)
        h.addWidget(self.btn_delete)
        h.addStretch(1)
        lay.addLayout(h)

        lay.addWidget(self.table)

        # 底部按钮
        h2 = QHBoxLayout()
        h2.addStretch(1)
        h2.addWidget(self.btn_ok)
        h2.addWidget(self.btn_cancel)
        lay.addLayout(h2)

        # 连接信号
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
        self.setWindowTitle("🏆 学生成绩排名")
        self.setMinimumSize(700, 500)

        # 创建表格
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["排名", "学号", "姓名", "GPA"])
        table.setRowCount(0)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 设置列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # 填充数据
        for r in ranks:
            row = table.rowCount()
            table.insertRow(row)
            rank_item = QTableWidgetItem(str(r.get('rank', '')))
            # 为前三名添加特殊标记
            rank_val = r.get('rank', 999)
            if rank_val == 1:
                rank_item.setText("🥇 1")
            elif rank_val == 2:
                rank_item.setText("🥈 2")
            elif rank_val == 3:
                rank_item.setText("🥉 3")

            table.setItem(row, 0, rank_item)
            table.setItem(row, 1, QTableWidgetItem(str(r.get('id', ''))))
            table.setItem(row, 2, QTableWidgetItem(str(r.get('name', ''))))
            g = r.get('gpa', None)
            table.setItem(row, 3, QTableWidgetItem("" if g is None else f"{g:.2f}"))

        # 布局
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.addWidget(table)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(close_btn)
        lay.addLayout(btn_layout)

def main():
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle("Fusion")

    w = MainWindow()

    # 设置窗口大小并居中显示
    w.resize(1280, 720)

    # 窗口居中
    screen = app.primaryScreen().geometry()
    size = w.geometry()
    w.move(
        (screen.width() - size.width()) // 2,
        (screen.height() - size.height()) // 2
    )

    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
