// Student Management System by Wxy
#include <bits/stdc++.h>
#include <string>
#include <vector>
#ifdef _WIN32
#include <windows.h>
#endif
using namespace std;
class Course {// 课程类
public:
    string name;   // 课程名称
    double credit; // 学分
    double score;  // 成绩
    Course(string n = "", double c = 0, double s = 0):name(n), credit(c), score(s) {}
};
class Student {
public:
    string id, name, gender, college, classnum, plcstatus, phone, province, parphone;// 学生基本信息
    int age;// 年龄
    vector<Course> courses; // 课程列表
    Student *next; // 链表指针
    Student(string id="", string name="", string gender="", int age=0, string college="", string classnum="",
            string plcstatus="", string phone="", string province="", string parphone=""):id(id), name(name), gender(gender), age(age), college(college), classnum(classnum),plcstatus(plcstatus), phone(phone), province(province), parphone(parphone), next(nullptr) {}
    // 学生基本信息修改
    void modify(string newname, string newgender, int newage, string newcollege,
                string newclassnum, string newplcstatus, string newphone,
                string newprovince, string newparphone);
    // 成绩录入或修改
    void inputScore(string coursename, double credit, double score);
    // 计算加权平均分
    double calcGPA();
    // 打印学生信息
    void printDetail();
    // 打印成绩信息
    void printScores();
};
class Studentm {//学生管理系统
private:
    Student *head;// 链表头指针
public:
    Studentm() : head(nullptr) {};// 构造函数
    Student *findStudent(string id);// 查找学生
    void addStudent(string id, string name, string gender, int age, string college, string classnum,
                    string plcstatus, string phone, string province, string parphone);// 添加学生
    void delStudent(string id);// 删除学生
    void modifyStudent(string id, string newname, string newgender, int newage, string newcollege,
                       string newclassnum, string newplcstatus, string newphone, string newprovince, string newparphone);
    void inputScore(string id, string coursename, double credit, double score);// 成绩录入或修改
    void queryScore(string id);// 成绩查询
    void queryStudent(string id);// 学生信息查询
    void displayStudents();// 显示所有学生
    void rankStudents();// 成绩排名
    void iptstudts(const string &filename);// 导入学生信息
    void iptscores(const string &filename);// 导入成绩信息
    void etStudents(const string &filename);// 导出学生信息
    void etScores(const string &filename);// 导出成绩信息
};
void Student::modify(string newname, string newgender, int newage, string newcollege,string newclassnum, string newplcstatus, string newphone,string newprovince, string newparphone) {
    name = newname;
    gender = newgender;
    age = newage;
    college = newcollege;
    classnum = newclassnum;
    plcstatus = newplcstatus;
    phone = newphone;
    province = newprovince;
    parphone = newparphone;
}
void Student::inputScore(string coursename, double credit, double score) {// 如果课程已存在则更新成绩，否则添加新课程
    for (auto &c : courses) {
        if (c.name == coursename) {
            c.credit = credit;
            c.score = score;
            cout << "更新成绩成功" << endl;
            return;
        }
    }
    courses.push_back(Course(coursename, credit, score));// 添加新课程
    cout << "导入成绩成功" << endl;
}
double Student::calcGPA() {// 计算加权平均分
    if (courses.empty()) return -1;// 无成绩返回-1
    double total1 = 0, total2 = 0;// total1为成绩*学分之和，total2为学分之和
    for (auto &c : courses) {
        total1 += c.score * c.credit;
        total2 += c.credit;
    }
    return total2 > 0 ? total1 / total2 : -1;// 避免除以0
}
void Student::printDetail() {// 打印学生详细信息
    cout << "姓名: " << name << endl;
    cout << "性别: " << gender << endl;
    cout << "年龄: " << age << endl;
    cout << "学号: " << id << endl;
    cout << "学院: " << college << endl;
    cout << "班级: " << classnum << endl;
    cout << "政治面貌: " << plcstatus << endl;
    cout << "电话: " << phone << endl;
    cout << "生源省份: " << province << endl;
    cout << "家长电话: " << parphone << endl;
    if (calcGPA() >= 0)// 如果有成绩则打印GPA
        cout << "加权平均分: " << calcGPA() << endl;
}
void Student::printScores() {// 打印成绩信息
    if (courses.empty()) {// 无成绩
        cout << "该学生还没有录入任何成绩" << endl;
        return;
    }
    cout << name << " 的成绩：" << endl;
    for (auto &c : courses) {// 遍历课程列表
        cout << "课程: " << c.name << " 学分: " << c.credit << " 成绩: " << c.score << endl;
    }
    cout << "加权平均分: " << calcGPA() << endl;
}

Student *Studentm::findStudent(string id) {// 查找学生
    Student *p = head;// 从链表头开始查找
    while (p) {// 遍历链表
        if (p->id == id) return p;
        p = p->next;
    }
    return nullptr;
}
void Studentm::addStudent(string id, string name, string gender, int age, string college, string classnum,
                               string plcstatus, string phone, string province, string parphone) {// 添加学生
    Student *newstdt = new Student(id, name, gender, age, college, classnum, plcstatus, phone, province, parphone);
    if (!head) {// 链表为空，直接插入第一个学生
        head = newstdt;
    } else {// 链表不为空，插入到链表末尾
        Student *p = head;
        while (p->next) p = p->next;
        p->next = newstdt;
    }
    cout << "学生添加成功" << endl;
}
void Studentm::delStudent(string id) {// 删除学生
    if (!head) {
        cout << "未找到此学生" << endl;
        return;
    }
    Student *p = head, *pre = nullptr;
    while (p && p->id != id) {
        pre = p;
        p = p->next;
    }
    if (!p) {
        cout << "未找到该学号" << endl;
        return;
    }
    if (!pre) head = head->next;
    else pre->next = p->next;
    delete p;
    cout << "学生删除成功" << endl;
}
void Studentm::modifyStudent(string id, string newname, string newgender, int newage, string newcollege,
                                  string newclassnum, string newplcstatus, string newphone, string newprovince, string newparphone) {
    Student *p = findStudent(id);
    if (!p) {
        cout << "未找到该学生" << endl;
        return;
    }
    p->modify(newname, newgender, newage, newcollege, newclassnum, newplcstatus, newphone, newprovince, newparphone);
    cout << "学生信息修改成功" << endl;
}
void Studentm::inputScore(string id, string coursename, double credit, double score) {// 成绩录入或修改
    Student *p = findStudent(id);
    if (!p) {
        cout << "未找到此学生" << endl;
        return;
    }
    p->inputScore(coursename, credit, score);//利用成绩录入直接覆盖
}
void Studentm::queryScore(string id) {// 成绩查询
    Student *p = findStudent(id);
    if (!p) {
        cout << "未找到此学生" << endl;
        return;
    }
    p->printScores();
}
void Studentm::queryStudent(string id) {// 学生信息查询
    Student *p = findStudent(id);
    if (!p) {
        cout << "未找到该学生" << endl;
        return;
    }
    p->printDetail();
}
void Studentm::displayStudents() {// 显示所有学生
    if (!head) {
        cout << "无学生信息" << endl;
        return;
    }
    cout << "学生信息如下：" << endl;
    Student *p = head;
    while (p) {
        cout << " 姓名: " << p->name << " 性别: " << p->gender << " 年龄: " << p->age
             << " 学号: " << p->id << " 学院: " << p->college << " 班级: " << p->classnum
             << " 政治面貌: " << p->plcstatus << " 电话: " << p->phone << " 生源省份: " << p->province
             << " 家长电话: " << p->parphone;
        if (p->calcGPA() >= 0) cout << " 加权平均分: " << p->calcGPA();
        cout << endl;
        p = p->next;
    }
}
void Studentm::rankStudents() {// 成绩排名
    if (!head) {
        cout << "无学生信息" << endl;
        return;
    }
    vector<Student *> arr;
    Student *p = head;
    while (p) {
        arr.push_back(p);
        p = p->next;
    }
    sort(arr.begin(), arr.end(), [](Student *a, Student *b) { return a->calcGPA() > b->calcGPA(); });// 按GPA降序排序
    cout << "成绩排名：" << endl;
    for (size_t i = 0; i < arr.size(); i++) {
        double gpa = arr[i]->calcGPA();
        cout << i + 1 << " 学号: " << arr[i]->id
             << " 姓名: " << arr[i]->name
             << " GPA: " << (gpa >= 0 ? to_string(gpa) : "未录入") << endl;
    }
}
void Studentm::iptstudts(const string &filename) {// 利用文本文件导入学生信息
    ifstream fin(filename);// 打开文件
    if (!fin.is_open()) {
        cout << "无法打开文件 " << filename << endl;
        return;
    }
    string id, name, gender, college, classnum, plcstatus, phone, province, parphone;
    int age;
    while (fin >> id >> name >> gender >> age >> college >> classnum >> plcstatus >> phone >> province >> parphone) {
        addStudent(id, name, gender, age, college, classnum, plcstatus, phone, province, parphone);
    }
    fin.close();//关闭文件
    cout << "学生信息批量导入完成" << endl;
}
void Studentm::iptscores(const string &filename) {// 利用文本文件导入成绩信息
    ifstream fin(filename);// 打开文件
    if (!fin.is_open()) {
        cout << "无法打开文件 " << filename << endl;
        return;
    }
    string id, course;
    double credit, score;
    while (fin >> id >> course >> credit >> score) {
        inputScore(id, course, credit, score);// 调用成绩录入函数
    }
    fin.close();//关闭文件
    cout << "成绩信息批量导入完成" << endl;
}
void Studentm::etStudents(const string &filename) {//导出学生信息到文本文件
    ofstream fout(filename);// 打开文件
    if (!fout.is_open()) {
        cout << "无法写入文件 " << filename << endl;
        return;
    }
    Student *p = head;
    while (p) {
        //按照指定格式写入文件
        fout << p->id << " " << p->name << " " << p->gender << " " << p->age << " "
             << p->college << " " << p->classnum << " " << p->plcstatus << " "
             << p->phone << " " << p->province << " " << p->parphone << endl;
        p = p->next;
    }
    fout.close();
    cout << "学生信息已导出到 " << filename << endl;
}
void Studentm::etScores(const string &filename) {//导出成绩信息到文本文件
    ofstream fout(filename);
    if (!fout.is_open()) {
        cout << "无法写入文件 " << filename << endl;
        return;
    }
    Student *p = head;
    while (p) {
        for (auto &c : p->courses) {
            fout << p->id << " " << c.name << " " << c.credit << " " << c.score << endl;
        }
        p = p->next;
    }
    fout.close();
    cout << "成绩信息已导出到 " << filename << endl;
}
int main() {
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);//控制编码使得不会出现乱码
#endif
    Studentm sys;
    while (true) {
        cout << "===== 学生管理系统 =====" << endl;
        cout << "1. 添加学生" << endl;
        cout << "2. 删除学生" << endl;
        cout << "3. 修改学生信息" << endl;
        cout << "4. 显示所有学生" << endl;
        cout << "5. 成绩录入/修改" << endl;
        cout << "6. 成绩查询" << endl;
        cout << "7. 成绩排名" << endl;
        cout << "8. 学生信息查询" << endl;
        cout << "9. 导出学生信息到文件" << endl;
        cout << "10. 导出成绩信息到文件" << endl;
        cout << "0. 退出系统" << endl;
        cout << "请输入选项: ";
        int x; cin >> x;
        if (cin.fail()) {//忽略错误输入防止报错
            cin.clear();
            cin.ignore(10000, '\n');
            cout << "输入无效，请输入数字！" << endl;
            continue;
        }
        if (x == 0) break;//退出系统
        string id, name, course, gender, college, classnum, plcstatus, phone, province, parphone, filename;
        int age; double credit, score;
        if (x == 1) {
            int mode;
            cout << "请选择输入方式：1. 逐个输入  2. 批量导入文件" << endl;
            cin >> mode;
            if (mode == 1) {
                cout << "请输入学号、姓名、性别、年龄、学院、班级、政治面貌、电话、生源省份和家长电话:" << endl;
                cin >> id >> name >> gender >> age >> college >> classnum >> plcstatus >> phone >> province >> parphone;
                sys.addStudent(id, name, gender, age, college, classnum, plcstatus, phone, province, parphone);
            } else if (mode == 2) {
                cout << "请输入学生信息文件名: ";
                cin >> filename;
                sys.iptstudts(filename);
            } else cout << "无效选择" << endl;
        }
        else if (x == 2) {
            cout << "请输入要删除的学生的学号: ";
            cin >> id;
            sys.delStudent(id);
        }
        else if (x == 3) {
            cout << "请输入要修改的学生的学号: ";
            cin >> id;
            cout << "请输入新的姓名、性别、年龄、学院、班级、政治面貌、电话、生源省份和家长电话:" << endl;
            cin >> name >> gender >> age >> college >> classnum >> plcstatus >> phone >> province >> parphone;
            sys.modifyStudent(id, name, gender, age, college, classnum, plcstatus, phone, province, parphone);
        }
        else if (x == 4) {
            sys.displayStudents();
        }
        else if (x == 5) {
            int mode;
            cout << "请选择录入方式：1. 逐个录入  2. 批量导入文件" << endl;
            cin >> mode;
            if (mode == 1) {
                cout << "请输入学生学号、课程名、学分和成绩: ";
                cin >> id >> course >> credit >> score;
                sys.inputScore(id, course, credit, score);
            } else if (mode == 2) {
                cout << "请输入成绩信息文件名: ";
                cin >> filename;
                sys.iptscores(filename);
            } else cout << "无效选择" << endl;
        }
        else if (x == 6) {
            cout << "请输入要查询成绩的学生的学号: ";
            cin >> id;
            sys.queryScore(id);
        }
        else if (x == 7) {
            sys.rankStudents();
        }
        else if (x == 8) {
            cout << "请输入要查询的学号: ";
            cin >> id;
            sys.queryStudent(id);
        }
        else if (x == 9) {
            cout << "请输入导出学生信息文件名: ";
            cin >> filename;
            sys.etStudents(filename);
        }
        else if (x == 10) {
            cout << "请输入导出成绩信息文件名: ";
            cin >> filename;
            sys.etScores(filename);
        }
        else {
            cout << "无效" << endl;
        }
    }
    cout << "END" << endl;
    return 0;
}