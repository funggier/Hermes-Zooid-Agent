# Active Work

- Project state: READY_TO_START
- Task ID: prepare-development-workspace
- Task state: READY
- Task file: [prepare-development-workspace](../tasks/prepare-development-workspace.md)
- Owner: UNASSIGNED
- Claim ID: NONE
- Execution: NOT_STARTED — รอคำสั่งเริ่มจากผู้ใช้หลัง CogentNexus-OpenClaw เสร็จ
- Working branch: agent/zooid-independence
- Repository: funggier/Zooid-Agent
- Last inspected HEAD before this documentation checkpoint: 1bb57bb290f94b6e9fb43844fa501db58ceb502e
- Source baseline: 089bb32886c8c18f7fa20182c7bf8826d6935ac5
- Review: [Draft PR #1](https://github.com/funggier/Zooid-Agent/pull/1)

## Start condition

ผู้ใช้เปิดงานเตรียมไว้แล้ว ไม่ต้องเปิด task หรือขอปลด pause อีกครั้ง
เมื่อผู้ใช้สั่งเริ่ม Zooid หลัง CogentNexus-OpenClaw เสร็จ ให้ตรวจ GitHub main/branch/PR สด
อ่าน root/area AGENTS, STATUS, WORKLOG และ task จากนั้น claim งานและทำได้ทันทีตาม scope
ตรวจว่า branch ยังอยู่หรือ merge ไปแล้ว; อย่า reset ไป SHA ที่บันทึกไว้ใน snapshot
เปลี่ยน project เป็น ACTIVE และ task เป็น IN_PROGRESS เมื่อเผยแพร่ claim สำเร็จ

## Waiting behavior

READY หมายถึง task พร้อมรับ ไม่ใช่คำสั่งรันอัตโนมัติหรือหลักฐานว่า workspace พร้อมแล้ว
ก่อนผู้ใช้สั่งเริ่ม ไม่มีการ claim, ติดตั้ง dependencies, แก้ source หรือรัน installer
ไม่มีการติดตาม CogentNexus-OpenClaw หรือ scheduled task และไม่อนุมานเวลาเริ่มจาก repo อื่น

## Execution boundaries

ใช้ checkout/environment แยกจาก live Hermes/OpenClaw/CogentNexus
ไม่หยุด/reset/uninstall/update ระบบที่กำลังรับงานหรือ shared Ollama
ไม่ใช้ credentials/channel sessions ของระบบเดิมโดยอัตโนมัติ
ความพร้อมเครื่องผู้ใช้ยัง NOT_CHECKED; คู่มือเป็นแบบออกแบบ ยังไม่มี integration ที่ติดตั้งจริง
ดู [local guide](../guides/local-development.md) สำหรับ claim/checkpoint/recovery

## Execution mode after start

CONTINUOUS: ทำตาม roadmap ตั้งแต่งานแรกจนถึง qualify-coexistence
หลัง task ผ่าน เตรียม/รับ task ถัดไปและทำต่อเอง ไม่รอผู้ใช้สั่งต่อทีละงาน
บันทึกรายงานละเอียดใน repo ส่งเฉพาะอัปเดตสั้นระหว่างทำ
หยุดเมื่อขอบเขตครบ ผู้ใช้สั่งหยุด หรือมี blocker ที่ต้องอาศัยผู้ใช้จริง
native execution และ owned updater ยังเป็นงานภายหลัง ไม่รวมในคำสั่งเริ่มช่วง independence
ดู continuous execution ในคู่มือ; ข้อจำกัดการกระทบ live runtime ยังมีผล
