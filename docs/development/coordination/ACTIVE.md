# Active Work

- Project state: PAUSED_BY_USER
- Reason: ผู้ใช้ต้องการทำ CogentNexus-OpenClaw ให้เสร็จก่อน แล้วจึงกลับมาพัฒนา Zooid
- Active implementation task: NONE
- Owner: UNASSIGNED
- Claim ID: NONE
- Resume candidate: [prepare-development-workspace](../tasks/prepare-development-workspace.md)
- Working branch at pause: agent/zooid-independence
- Repository: funggier/Zooid-Agent
- Last inspected HEAD before this documentation checkpoint: aeb72731591561586a97c4226b84fe6e1112ae19
- Source baseline: 089bb32886c8c18f7fa20182c7bf8826d6935ac5
- Review: [Draft PR #1](https://github.com/funggier/Zooid-Agent/pull/1)

## While paused

ไม่มีงาน implementation ที่อนุญาตให้รับอัตโนมัติจากเอกสารนี้
ไม่ claim task, ติดตั้ง dependencies, แก้ source, รัน installer หรือสร้าง scheduled task
เก็บเอกสารเพื่อส่งต่อเท่านั้น ไม่มีการติดตาม CogentNexus-OpenClaw หรือเริ่ม Zooid อัตโนมัติ

## Resume condition

รอผู้ใช้กลับมาสั่งทำ Zooid ต่อหลังจากจัดการ CogentNexus-OpenClaw ตามที่ต้องการแล้ว
ห้ามอนุมานว่าคำว่า DONE ใน repo อื่นหรือเวลาที่ผ่านไปเป็นคำสั่งเริ่มงาน Zooid
เมื่อผู้ใช้สั่งกลับมา ให้ตรวจ GitHub main/branch/PR สด อ่าน STATUS/WORKLOG และ root/area AGENTS
ตรวจว่า branch ยังอยู่หรือ merge ไปแล้ว; อย่า reset ไป SHA ที่บันทึกไว้ใน snapshot
จากนั้นเปลี่ยน project state เป็น ACTIVE และเปิด prepare-development-workspace เป็น READY ก่อน claim

## Execution boundaries after resume

ใช้ checkout/environment แยกจาก live Hermes/OpenClaw/CogentNexus
ไม่หยุด/reset/uninstall/update ระบบที่กำลังรับงานหรือ shared Ollama
ไม่ใช้ credentials/channel sessions ของระบบเดิมโดยอัตโนมัติ
ความพร้อมเครื่องผู้ใช้ยัง NOT_CHECKED; คู่มือเป็นแบบออกแบบ ยังไม่มี integration ที่ติดตั้งจริง
ดู [local guide](../guides/local-development.md) สำหรับ claim/checkpoint/recovery
