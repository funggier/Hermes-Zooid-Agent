# Zooid Development

ศูนย์กลางแผนและความคืบหน้าของ **Zooid — Powered by CogentNexus**
สำหรับผู้ใช้, ChatGPT, CogentNexus-OpenClaw และ agent ที่รับงานต่อ

**สถานะโครงการ: READY_TO_START** งานแรกเปิดเป็น READY และยังไม่มีผู้รับงาน
ผู้ใช้จะทำ CogentNexus-OpenClaw ให้เสร็จก่อน แล้วสั่งเริ่ม Zooid ได้ทันที
ไม่มีขั้นขอปลด pause ซ้ำ และไม่มีการรัน/ส่งงาน/ติดตามสถานะอัตโนมัติ

## เริ่มอ่านตรงนี้

1. อ่าน root `AGENTS.md` แล้วอ่าน [ACTIVE](coordination/ACTIVE.md) และ [STATUS](coordination/STATUS.md)
2. เปิดไฟล์ task ที่ ACTIVE ชี้ไป อ่าน scope, acceptance และข้อจำกัด
3. อ่าน `AGENTS.md` เฉพาะพื้นที่ที่จะเปลี่ยน
4. ตรวจ branch/HEAD บน GitHub สด แล้วทำตาม [คู่มือพัฒนาบนเครื่อง](guides/local-development.md)
5. บันทึกผลตาม [แบบรายงาน](templates/report.md) และอัปเดต coordination ก่อนส่งต่องาน

ชื่อ repo ไม่ใช่หลักฐานว่าโปรแกรมแยกจาก Hermes แล้ว อ่านสถานะการทดสอบก่อนติดตั้ง

## โครงสร้างเอกสาร

| ตำแหน่ง | หน้าที่ |
| --- | --- |
| [roadmap.md](roadmap.md) | ลำดับงานและเงื่อนไขผ่านแต่ละช่วง |
| [naming-conventions.md](naming-conventions.md) | ชื่อไฟล์ โฟลเดอร์ และการจัดประวัติ |
| [plans/product-independence.md](plans/product-independence.md) | แผนแยกโปรแกรมและหลักฐานสำรวจ source เริ่มต้น |
| [guides/local-development.md](guides/local-development.md) | วิธีใช้ CogentNexus-OpenClaw พัฒนาจากเครื่องผู้ใช้ |
| [coordination/ACTIVE.md](coordination/ACTIVE.md) | งานที่ควรทำตอนนี้ ผู้รับงาน และจุดทำต่อ |
| [coordination/STATUS.md](coordination/STATUS.md) | สถานะงานรวมพร้อมหลักฐาน |
| [coordination/WORKLOG.md](coordination/WORKLOG.md) | ประวัติสิ่งที่เกิดขึ้นจริงแบบเพิ่มรายการ |
| [tasks/prepare-development-workspace.md](tasks/prepare-development-workspace.md) | งานแรกพร้อมเงื่อนไขสำเร็จ |
| [acceptance/coexistence.md](acceptance/coexistence.md) | เกณฑ์พิสูจน์ Zooid อยู่ร่วมกับ Hermes |
| [templates/task.md](templates/task.md) | รูปแบบกำหนดงานถัดไป |
| [templates/report.md](templates/report.md) | รูปแบบรายงานหลักฐาน |
| [reports/README.md](reports/README.md) | วิธีเก็บรายงานและผลทดสอบ |

GitHub commit/Actions/artifact คือหลักฐานการทำงาน เอกสารสถานะเป็นดัชนีชี้หลักฐาน
ถ้าข้อมูลขัดกัน ให้ตรวจหลักฐานแล้วแก้ดัชนี ไม่เลือกเชื่อข้อความล่าสุดโดยไม่มีหลักฐาน
เอกสารนี้เป็น workflow ผ่าน Git/Markdown ยังไม่ใช่ integration ที่ติดตั้งใน CogentNexus อัตโนมัติ

## เมื่อผู้ใช้สั่งเริ่ม

ทำต่อเนื่องตาม roadmap ช่วง independence จนผ่าน qualify-coexistence
ไม่จบแต่ละ task ด้วยการรอคำสั่ง “ต่อ”; เก็บรายงานละเอียดใน repo และส่งอัปเดตสั้นระหว่างทำ
ดูขอบเขตและเงื่อนไขหยุดใน [คู่มือ](guides/local-development.md)
