# Task Definition Template

Template เท่านั้น ไม่ใช่งานที่ active; แทนค่าทุกช่องก่อนเปลี่ยนสถานะเป็น READY

- Task ID: semantic-slug
- Goal: ผลลัพธ์ที่สังเกตและตรวจสอบได้
- Depends on: task/gate ที่ต้องผ่าน
- State: live state และ owner ให้อ้าง ACTIVE
- Source baseline: exact SHA และเวลา UTC ที่ตรวจ
- Scope: files/subsystems/operations ที่เปลี่ยนได้
- Non-goals: เรื่องที่ไม่ทำใน task นี้
- Inputs: source, area AGENTS, plan และ evidence ที่ต้องอ่าน
- Risks/uncertainty: สิ่งที่ยังไม่ทราบและวิธีพิสูจน์
- Allowed environment: isolated checkout/test host และ runtime ที่ห้ามกระทบ

## Execution

ระบุ path และ symbol ที่ตรวจพบจริง พร้อมขั้นเล็กที่ทำจบและ checkpoint ได้
production change ระบุ behavioral RED case, test command ของ repo, minimal change และ GREEN
อย่าเขียนเพียง “เพิ่ม tests” โดยไม่มีสิ่งที่ tests ต้องพิสูจน์
ถ้าข้อมูลไม่พอให้เป็น investigation task พร้อม output ที่ต้องค้นพบก่อน

## Acceptance

รายการผลตรวจที่ครบแล้วจึง DONE พร้อมตำแหน่งหลักฐาน
ระบุ required กับ optional และเงื่อนไข BLOCKED ชัดเจน

## Checkpoint and handoff

report path, tested SHA, local-only changes, remote commit, next executable action,
scope ของ retry และสิ่งที่ผลการทำงานยัง UNKNOWN
