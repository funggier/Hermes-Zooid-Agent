# Execution Reports

เก็บรายงานตาม task ด้วยชื่อเชิงความหมาย เช่น prepare-development-workspace.md
ใช้ [report template](../templates/report.md) เพิ่ม attempt sections ในไฟล์เดิมเมื่อ retry
ทุก attempt ต้องมีเวลา UTC, tested SHA, คำสั่งและผลจริง; Git เก็บประวัติการแก้ไข

ยังไม่มีรายงานการรันบนเครื่องผู้ใช้ รายงานแรกจะสร้างโดย executor ของ task เตรียม workspace
หลักฐานการสำรวจ source เริ่มต้นอยู่ใน [แผน](../plans/product-independence.md)
และ [WORKLOG](../coordination/WORKLOG.md)

ไม่ commit secrets, raw .env, token, personal chat หรือ log ที่ไม่ผ่านการตัดข้อมูล
ผล tests ขนาดใหญ่ให้อ้าง artifact ที่เข้าถึงได้พร้อม hash/expiry
