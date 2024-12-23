from flask import Flask, request, render_template
import pandas as pd
import datetime

app = Flask(__name__)
import qrcode
import pandas as pd

import os

# إنشاء مجلد "qrcodes" إذا لم يكن موجودًا
output_dir = "qrcodes"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# قائمة الأكواد
codes = [f"CODE{i:03}" for i in range(1, 301)]

# الرابط الأساسي
base_url = "https://yourdomain.com/submit?code="

# توليد رموز QR
for code in codes:
    qr = qrcode.make(f"{base_url}{code}")
    qr.save(f"qrcodes/{code}.png")

# حفظ الأكواد في ملف CSV
df = pd.DataFrame({"Code": codes})
df.to_csv("valid_codes.csv", index=False)
print("تم إنشاء رموز QR.")

# قراءة الأكواد المسموح بها من ملف
valid_codes = pd.read_csv("valid_codes.csv")["Code"].tolist()

# قائمة لتخزين الأكواد المستخدمة
used_codes = set()

# قائمة لتخزين بيانات الحضور
attendance_data = []

@app.route('/')
def home():
    return "مرحبًا! تأكد من مسح رمز QR الخاص بك للدخول."

@app.route('/submit', methods=['GET'])
def submit():
    # جمع الكود من الرابط (GET parameter)
    student_code = request.args.get('code')
    student_name = request.args.get('name')  # يمكن إضافته عبر النموذج بعد مسح QR
    subject = request.args.get('subject')   # يمكن إضافته أيضًا

    # التحقق من أن الكود تم تمريره عبر الرابط
    if not student_code:
        return "لم يتم إرسال الكود. يرجى التأكد من مسح رمز QR الصحيح.", 400

    # التحقق من صلاحية الكود
    if student_code not in valid_codes:
        return "الكود غير صالح.", 400

    # التحقق من أن الكود لم يتم استخدامه مسبقًا
    if student_code in used_codes:
        return "تم استخدام هذا الكود بالفعل.", 400

    # تسجيل الحضور
    timestamp = datetime.datetime.now()
    attendance_data.append({
        "Code": student_code,
        "Name": student_name or "غير محدد",  # إذا لم يتم تمرير الاسم
        "Subject": subject or "غير محدد",    # إذا لم يتم تمرير المادة
        "Timestamp": timestamp
    })

    # إضافة الكود إلى الأكواد المستخدمة
    used_codes.add(student_code)

    return "تم تسجيل الحضور بنجاح!"

@app.route('/export')
def export():
    # تصدير بيانات الحضور إلى Excel
    df = pd.DataFrame(attendance_data)
    df.to_excel("attendance.xlsx", index=False)
    return "تم تصدير بيانات الحضور إلى attendance.xlsx بنجاح!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
