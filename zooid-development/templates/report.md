# Execution Report Template

Template เท่านั้น: ไม่มีช่องใดนับเป็นหลักฐานจน executor ใส่ค่าจริง

- Task ID / owner / claim ID:
- Started / checkpoint / ended at (UTC):
- Repository / working branch / base SHA:
- Tested source SHA / dirty-tree diff hash ถ้ามี:
- Result: PASS / FAIL / BLOCKED / NOT_RUN
- Publication: LOCAL_ONLY หรือ remote commit/link ที่ตรวจแล้ว

## Changes and rationale

ทำอะไร เพราะอะไร files/functions ที่เปลี่ยน และสิ่งที่ยังไม่สำเร็จ

## Evidence

| Command / cwd | Host/toolchain | Tested SHA | Exit code | Outcome | Log/artifact URL + hash |
| --- | --- | --- | --- | --- | --- |
| กรอกคำสั่งจริง | กรอกสภาพแวดล้อมจริง | exact SHA | ค่า actual | PASS/FAIL/BLOCKED/NOT_RUN | ตัด secrets ก่อนเผยแพร่ |

แยก baseline, RED, GREEN และ build/installer/host-native acceptance
report-only commit ที่ตามหลัง tested source ไม่ใช่ SHA ที่ผ่าน runtime tests
บันทึก artifact expiry และการเข้าถึง; อย่าอ้างแค่ “CI เขียว” โดยไม่มี run/commit

## Side effects and uncertainty

การกระทำที่เริ่มแล้ว, สิ่งที่สังเกตได้, ผลที่ UNKNOWN, วิธีตรวจโดยไม่ทำซ้ำ
บันทึกการไม่กระทบ live runtime เฉพาะเมื่อมีการตรวจ; อย่าคัดลอกข้อความนี้เป็นคำยืนยันอัตโนมัติ

## Acceptance, remaining work and next action

แต่ละ criterion พร้อม evidence; failed/not-run ต้องอยู่ในรายงาน
การแก้ภายหลังเพิ่ม attempt section ใหม่ ไม่ลบผลเก่า
อัปเดต STATUS/WORKLOG/ACTIVE ให้ตรงกันก่อนส่งต่องาน
