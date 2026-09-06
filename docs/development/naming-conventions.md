# Naming Conventions

## หลักการ

ชื่อบอกหน้าที่และเนื้อหา อายุการใช้งานไม่ผูกกับ release ของโปรแกรม
โฟลเดอร์และชื่อไฟล์เป็นภาษาอังกฤษ เนื้อหาอธิบายใช้ภาษาไทยได้
ใช้ lowercase-kebab-case สำหรับเอกสารทั่วไป คงชื่อมาตรฐาน README.md, AGENTS.md,
ACTIVE.md, STATUS.md และ WORKLOG.md เพื่อให้ค้นหาได้ง่าย

| ควรใช้ | หลีกเลี่ยง |
| --- | --- |
| product-independence.md | zooid-v1-plan.md |
| runtime-recovery.md | recovery-v093-final.md |
| isolate-runtime-storage.md | task-001-new-final2.md |
| windows-coexistence.md | windows-latest.md |
| local-development.md | openclaw-2026-setup-new.md |

## แยกตัวตนออกจากประวัติ

- เวอร์ชัน dependency, source SHA, วันที่ UTC, run ID และ schema revision ใส่ในเนื้อหา
- แก้ living document ที่ไฟล์เดิม ให้ Git เก็บประวัติ ไม่สร้างสำเนา final/new/latest
- Task ID ใช้ semantic slug เช่น prepare-development-workspace ไม่ใช่ release number
- แผนเปลี่ยนได้ แต่เก็บเหตุผลและผลกระทบต่อ acceptance ใน WORKLOG
- งานเสร็จคง task ไว้พร้อมลิงก์รายงาน; ACTIVE เปลี่ยนเป็น task ถัดไป
- รายงานแต่ละงานใช้ reports/<task-slug>.md เมื่อมีหลายความพยายามเพิ่มหัวข้อภายใน
  พร้อม attempt ID, เวลา, tested SHA และผลเดิม ห้ามลบทับความล้มเหลวให้ดูเหมือนไม่เคยเกิด
- Log ขนาดใหญ่เก็บเป็น CI artifact หรือหลักฐานที่เข้าถึงได้ ระบุ URL, hash และวันหมดอายุ
  หากต้องรักษานาน ให้เก็บสำเนาที่ได้รับอนุญาตก่อน artifact หมดอายุ
- ไม่เติม version suffix ให้ module/class เพื่อเลี่ยงการปรับของเดิม
  ชื่อไฟล์โค้ดใช้ convention ของภาษา/พื้นที่นั้น เช่น Python snake_case
- ข้อยกเว้นที่มีความหมายจริง เช่น migration sequence, protocol compatibility และ release assets
  ใช้เลขที่จำเป็นได้ พร้อมอธิบาย ไม่เปลี่ยน dependency identifier, license หรือชื่อ tool ของผู้อื่นโดยพลการ

## ย้ายเอกสาร

อัปเดตลิงก์ภายในและจุดเริ่มอ่านทั้งหมดใน commit เดียวกัน
ลิงก์ประวัติใช้ commit permalink; ไม่ต้องเก็บสำเนาเนื้อหาซ้ำเพื่อรักษาชื่อเก่า
