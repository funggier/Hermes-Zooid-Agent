# Prepare Development Workspace

- Task ID: prepare-development-workspace
- Definition state: READY; execution NOT_STARTED รอคำสั่งเริ่ม; live owner/state ดู [ACTIVE](../coordination/ACTIVE.md)
- Depends on: ผู้ใช้สั่งกลับมาพัฒนา Zooid และเอกสาร workflow ใน branch ปัจจุบัน
- Goal: มี checkout/environment แยกที่ตรวจ source และ baseline สำหรับ independence ได้
- Non-goals: แก้ production, ติดตั้ง Zooid จริง, ปิด updater จริง, ทดสอบ reset/uninstall บนระบบผู้ใช้

## Inputs และการอ่าน

[local guide](../guides/local-development.md), [independence plan](../plans/product-independence.md),
root/area AGENTS.md, remote HEAD สด และ package/lockfiles ที่ HEAD นั้น
อ่านเฉพาะ subsystem ที่สำรวจ ไม่บรรทุกทั้งประวัติการพัฒนาเข้า context

## Steps

- [ ] ตรวจ tool availability, path จริง, สิทธิ์ GitHub read/push โดยไม่แสดง token
- [ ] เตรียม checkout แยกตามคู่มือ ตรวจ origin และ dirty files
- [ ] Claim ACTIVE แล้วเผยแพร่ก่อนเริ่มงานที่มีการแก้ไข
- [ ] บันทึก OS, Git/Python/Node/Git Bash และ manifest constraints
- [ ] เตรียม environment ของ checkout ตามเอกสาร upstream ที่อ่านแล้ว โดยไม่เรียก installer เดิม
- [ ] ตรวจ test isolation เลือก baseline ของ constants/home, update และ skills จากไฟล์จริง
- [ ] รัน baseline ผ่าน runner ของ repo เก็บคำสั่ง/exit code/ผล; missing dependency ไม่ใช่ test PASS
- [ ] สำรวจ updater caller map: CLI, banner, gateway, web, TUI, Desktop, bootstrap และ fallback
- [ ] เขียน tasks/disable-upstream-updates.md ตาม template พร้อมไฟล์/ฟังก์ชันที่ค้นพบจริงและ RED cases
- [ ] เขียน reports/prepare-development-workspace.md แล้วอัปเดต STATUS/WORKLOG/ACTIVE

## Outputs

รายงานต้องมี local checkout path (ตัดข้อมูลส่วนบุคคลที่ไม่จำเป็น), exact base/tested SHA,
remote branch, toolchain, dependency setup, baseline results, caller map และ next action
paths ที่ยังหาไม่พบระบุ NOT_FOUND พร้อม search scope; ห้ามเดาฟังก์ชัน

## Acceptance

- Checkout/environment ไม่ซ้อน live Hermes/OpenClaw/CogentNexus และไม่ใช้ venv ร่วม
- Remote HEAD/branch และ claim ยืนยันได้
- Baseline ที่จำเป็นรันจริงและผลตีความได้; ถ้า FAIL ต้องมี issue/blocker ที่จำแนกได้
- ไม่เปลี่ยน live service/task/provider/config; ไม่มี installation lifecycle operation
- มี task ถัดไปที่ executable และ report ที่อ้างหลักฐานได้

DONE เมื่อเกณฑ์ครบ; หาก baseline/setup ยังไม่พร้อมให้ BLOCKED พร้อมสาเหตุและขั้นปลดบล็อก
ไม่รายงานว่า Zooid รองรับ coexistence จากการผ่าน task เตรียม environment

## Risks และ recovery

Python/Node อาจไม่ตรง manifest, test runner อาจ fallback ไป venv เดิม, inherited HERMES_HOME
อาจชี้ live data, installer อาจดึง upstream และ owner อื่นอาจแก้ branch พร้อมกัน
ตรวจทั้งหมดก่อนรัน; หากหยุดกลางงานให้คง dirty files และรายงาน LOCAL_ONLY ก่อน resume
