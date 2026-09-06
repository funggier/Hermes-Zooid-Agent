# Local Development with CogentNexus-OpenClaw

**งานแรกเปิดเป็น READY แล้ว** ใช้คู่มือนี้เมื่อผู้ใช้สั่งเริ่ม Zooid หลัง CogentNexus-OpenClaw เสร็จ
ก่อนคำสั่งเริ่มให้รอก่อน bootstrap/claim; ไม่ต้องขอปลด pause ซ้ำ
ไม่มีการติดตามหรือเริ่มงานจากความสำเร็จของ repo อื่นโดยอัตโนมัติ

## บทบาทและขอบเขต

ใช้ CogentNexus-OpenClaw ที่ติดตั้งอยู่เป็นผู้รับคำสั่งและรันเครื่องมือพัฒนา Zooid
เอกสาร Git/Markdown เป็น shared artifact ที่ agent ต่าง session อ่านต่อได้
ยังไม่ได้ตรวจความสามารถของ runtime บนเครื่องผู้ใช้ในรอบนี้ จึงไม่สมมติว่ามีคำสั่ง
สร้าง ticket, spawn agent, push Git หรืออ่านโฟลเดอร์ทุกตำแหน่งได้

เริ่มผ่านช่องทางที่ผู้ใช้ใช้งาน CogentNexus-OpenClaw ได้อยู่แล้ว
ใช้ shell/file/Git tools ที่ runtime เปิดให้จริง ถ้าสิ่งใดไม่มีให้บันทึก BLOCKED เฉพาะส่วนนั้น
ไม่ต้องติดตั้ง plugin/skill ใหม่เพียงเพื่ออ่านแผนนี้ และไม่แก้ runtime ที่กำลังใช้ทำงาน

## ตำแหน่งทำงาน

ตัวอย่าง checkout: `$env:USERPROFILE\source\Zooid-Agent`
ตัวอย่างพื้นที่หลักฐานนอก Git: `$env:LOCALAPPDATA\ZooidDevelopment\evidence`
ตำแหน่งเหล่านี้เป็นข้อเสนอ ไม่ใช่ค่าที่ตรวจพบจากเครื่อง
ห้ามวาง checkout ภายใน live Hermes/OpenClaw/CogentNexus installation หรือ workspace ที่ระบบเดิมจัดการอยู่
ตรวจ path จริงรวม junction/symlink ก่อนใช้ ห้ามลบหรือทับ directory ที่มีอยู่โดยไม่ตรวจ

ใช้ venv ของ checkout โดยเฉพาะ ไม่ลง package ทับ interpreter ของ Hermes
ค่า ZOOID_HOME เป็น contract เป้าหมาย ยังไม่ถือว่า source ปัจจุบันรองรับ
ก่อน home isolation เสร็จ ให้ test harness ใช้ HERMES_HOME ชั่วคราวใน child process ตามเดิม
ห้าม setx HERMES_HOME หรือแก้ environment ถาวรของผู้ใช้เพื่อให้ Zooid ทำงาน

## Bootstrap แบบตรวจสอบได้

ตัวอย่างต่อไปนี้ใช้ PowerShell รันทีละขั้น ตรวจผลและ exit code ก่อนขั้นถัดไป
หาก tool มีไม่ครบ หยุดเฉพาะขั้นที่ต้องใช้ ไม่อ้างว่า baseline ผ่าน

```powershell
Get-Command git, python, node, npm, bash -ErrorAction SilentlyContinue
git --version
git ls-remote https://github.com/funggier/Zooid-Agent.git refs/heads/main refs/heads/agent/zooid-independence
```

เมื่อยืนยันตำแหน่งว่างและได้รับสิทธิ์อ่าน/เขียน directory นั้นแล้ว:

```powershell
$ZooidSourceRoot = Join-Path $env:USERPROFILE 'source'
$ZooidCheckout = Join-Path $ZooidSourceRoot 'Zooid-Agent'
Test-Path $ZooidCheckout
```

ถ้า False จึงสร้าง parent ที่ยังไม่มีและ clone:

```powershell
New-Item -ItemType Directory -Force -Path $ZooidSourceRoot
git clone --branch agent/zooid-independence --single-branch https://github.com/funggier/Zooid-Agent.git $ZooidCheckout
Set-Location $ZooidCheckout
git remote -v
git status --short --branch
git rev-parse HEAD
```

ถ้า checkout มีอยู่แล้ว ตรวจ remote, dirty files, branch และเจ้าของก่อนใช้งาน
ห้าม reset --hard, clean หรือ stash งานของผู้อื่นเพื่อทำให้เริ่มได้ง่าย
ถ้า branch นี้ merge ไปแล้ว ให้ตรวจ PR และเลือก branch ใหม่จาก main ล่าสุด พร้อมแก้ ACTIVE

อ่าน root AGENTS และเอกสารตาม README ก่อนติดตั้ง dependencies
ตรวจเวอร์ชันจาก .python-version, pyproject.toml, .nvmrc, package.json และ lockfiles ของ HEAD ที่ใช้จริง
อย่าใช้เวอร์ชันจากความจำ อย่ารัน installer เดิมเพื่อเตรียม developer environment เพราะยังชี้ไป Hermes

## การทดสอบ

Python ใช้ scripts/run_tests.sh ตาม root AGENTS.md ผ่าน Git Bash ที่ตรวจแล้ว
เริ่มจาก test files ที่สัมพันธ์กับงาน ค้นหาด้วย rg --files tests และอ่านก่อนเลือก
หาก runner ใช้ venv ร่วมกับ Hermes เป็น fallback ต้องเตรียม venv ของ checkout ให้ถูกต้องก่อนรัน
ห้ามเปิด gateway/update/install จาก source เดิมโดยคิดว่าเปลี่ยนชื่อ repo แล้วปลอดภัย

ตรวจ test harness ว่า home ชั่วคราวและ credential isolation ทำงานจริง
ใช้ fake provider และ local skill fixture สำหรับ baseline ไม่เรียกโมเดลเสียเงินหรือส่งข้อความภายนอก
host-specific behavior ต้องทดสอบบน OS จริง; WSL/Linux ไม่ใช่หลักฐาน native Windows
JS/build ใช้ scripts ที่มีจริงใน package.json; Rust/bootstrap ทำเฉพาะ task ที่ต้องแตะ
บันทึกคำสั่งเต็ม working directory, OS/toolchain, exit code, tested SHA และผลล้มเหลวเดิม
การอ่านเอกสารอย่างเดียวไม่ต้องรัน full runtime suite

## รับงานและป้องกันการเขียนชนกัน

ค่าเริ่มต้นคือ executor เดียว ไม่สมมติว่ามี distributed lock หรือ server lease

1. fetch branch และอ่าน ACTIVE จาก remote ล่าสุด ตรวจ owner และ claim
2. หาก READY/UNASSIGNED ให้ใส่ owner ที่ระบุ session ได้, claim ID ไม่ซ้ำ, เวลา UTC,
   base SHA, scope และ IN_PROGRESS แล้ว commit/push แบบ fast-forward
3. อ่าน remote กลับ ยืนยัน claim ยังเป็นของตนก่อนแก้ source
4. ถ้า push ถูกปฏิเสธเพราะมีงานใหม่ ให้ fetch แล้วเทียบ อย่า force หรือ merge claim ของสองเจ้าของเข้าด้วยกัน
5. ถ้ามี owner อื่นให้ประสานงานผ่านผู้ใช้/ช่องทางที่ได้รับอนุญาต ไม่ยึด claim ด้วย timeout อัตโนมัติ
6. ก่อน push ผลงานตรวจ remote อีกครั้ง ถ้ามีคนเปลี่ยนงานหรือขอบเขต ให้ reconcile ก่อนดำเนินต่อ

protocol นี้ประสานผู้เขียนที่ร่วมมือกัน ไม่ใช่การบังคับ lock ด้วยโค้ด
ผู้ช่วยที่เข้ามาเพิ่มควรอ่านอย่างเดียวจนผู้รับงานเดิมคืนงานหรือผู้ใช้มอบหมายชัดเจน

## วงจรทำงานและ checkpoint

อ่าน goal → ตรวจ source → ทำขั้นเล็ก → ทดสอบ → commit ผล → ลด context → ทำต่อ
production repair ใช้ RED → minimal fix → GREEN; baseline FAIL ต้องแยกจาก regression ใหม่
ใช้ [task template](../templates/task.md) และ [report template](../templates/report.md)
ไม่ต้องถามอนุญาตซ้ำสำหรับการอ่าน/แก้ source/test/docs ปกติที่อยู่ใน scope ที่ผู้ใช้มอบหมายแล้ว
live install/reset/uninstall หรือการเปลี่ยนระบบที่ใช้รัน executor ต้องตรวจขอบเขตการอนุญาตจริงก่อน
ถ้าไม่มีการอนุญาตที่ครอบคลุม ให้เตรียม candidate และหลักฐานให้ตรวจได้ก่อนถามเฉพาะการกระทบนั้น

checkpoint แต่ละครั้งอัปเดต report, STATUS, ACTIVE และ WORKLOG ใน commit เดียวกันเท่าที่ทำได้
รายงาน tested SHA แยกจาก documentation commit; ห้ามใส่ SHA ของ commit ตัวเองที่ยังไม่ถูกสร้าง
ผลที่ยัง push ไม่สำเร็จคือ LOCAL_ONLY ไม่ใช่ remote completion
เมื่อ task DONE ให้ ACTIVE ชี้ task ถัดไปที่เขียนครบแล้ว ไม่ทิ้งคำว่า “ทำต่อ” โดยไม่มี next action
รายงานจุดสำคัญและ blocker ระหว่างทำ ไม่เงียบจนผู้ใช้ไม่รู้ว่าทำอะไรอยู่

## กลับมาหลังขัดข้อง

ตรวจสถานะจริงก่อนอ่านข้อสรุปเก่า: remote/local HEAD, dirty files, claim, report ล่าสุด
อย่ารัน installer, reset หรือ external side effect ซ้ำเพียงเพราะไม่มีคำตอบใน chat
หากผลการกระทำยังไม่ทราบ ให้บันทึก UNKNOWN และตรวจ artifact/process/registration ก่อนตัดสินใจ
ถ้า dependency/network ใช้ไม่ได้ ระบุคำสั่งและ error ที่ตัด secret แล้วพร้อม next action
ไม่ถือว่า blocker ของ ChatGPT workspace จะเกิดบนเครื่องผู้ใช้ด้วย

## ข้อความเริ่มงานสำหรับผู้ใช้

เก็บข้อความนี้ไว้ส่งหลัง CogentNexus-OpenClaw เสร็จและผู้ใช้พร้อมกลับมาทำ Zooid:

> CogentNexus-OpenClaw เสร็จแล้ว เริ่มงาน Zooid ที่เปิด READY ไว้ได้เลย
> พัฒนา Zooid-Agent ตาม https://github.com/funggier/Zooid-Agent
> ตรวจ main, PR #1 และ branch agent/zooid-independence จาก GitHub สดก่อน
> อ่าน AGENTS.md และ docs/development/README.md แล้วอ่าน coordination/ACTIVE.md กับ STATUS.md
> รับงานตาม task ที่ ACTIVE ชี้ไปและทำต่อเป็นขั้นเล็ก พร้อมบันทึกหลักฐานลง repo
> ใช้ checkout และ environment แยกจาก Hermes/OpenClaw/CogentNexus ที่ติดตั้งอยู่
> ไม่หยุดหรือแก้ระบบที่กำลังใช้รับงาน ไม่รัน installer เดิม และไม่ใช้ credentials ของระบบเดิมโดยอัตโนมัติ
> ทำต่อเนื่องตาม roadmap ช่วง independence ไม่รอคำสั่งต่อทุก task ส่งอัปเดตสั้นระหว่างทำ
> บันทึก exact HEAD, สิ่งที่เปลี่ยน, ผลทดสอบ, blocker และ next action ใน repo
> ถ้าเครื่องมือไม่มี ให้บอก capability ที่ขาดตามจริง ห้ามสมมติคำสั่งของ CogentNexus

ข้อความนี้เป็นคำสั่งที่เตรียมไว้ ยังไม่ได้ถูกส่งหรือสร้าง ticket จาก session ที่จัดทำเอกสาร

## Continuous execution after start

คำสั่งเริ่มจากผู้ใช้อนุญาตให้พัฒนาต่อเนื่องในขอบเขต product independence ของ roadmap
ตั้งแต่ prepare-development-workspace ถึง qualify-coexistence ไม่ใช่ทำ preparation แล้วหยุดรอคำว่า “ต่อ”
ขั้น design-native-execution และ design-owned-updates ยัง DEFERRED ตามขอบเขตที่ตกลงไว้

- เมื่อ task ผ่าน ให้บันทึก report/STATUS/WORKLOG, เตรียม task ถัดไปตาม template,
  เปลี่ยน ACTIVE และรับงานถัดไปได้ทันทีโดยไม่ขออนุมัติ routine source/test/docs/CI repair ซ้ำ
- หากต้องแบ่งงานเพิ่ม ให้ทำเองตาม root cause/dependency พร้อมเหตุผล ไม่เปลี่ยนเป้าหมายหรือเพิ่ม feature นอก scope
- ทำ commit/checkpoint เป็นระยะและ push แบบ fast-forward; อัปเดต draft PR ที่เกี่ยวข้อง
- รายละเอียดหลักฐานอยู่ใน repo; ในบทสนทนาส่งอัปเดตสั้นเมื่อมีผลสำคัญ เปลี่ยนขั้น หรือพบ blocker
  ระหว่างทำงานต่อเนื่องควรอัปเดตอย่างน้อยทุกประมาณ 3 นาทีเมื่อช่องทางรองรับ
- ไม่ส่ง final handoff และรอผู้ใช้ตอบหลังจบทุก task; ทำต่อจน independence gates ครบ
  หรือมี blocker ที่ทำให้ดำเนินต่ออย่างถูกต้องไม่ได้
- Blocker เฉพาะส่วน: บันทึกหลักฐานแล้วทำงานอิสระที่ยังอยู่ใน scope ต่อได้
  หากต้องการข้อมูล/สิทธิ์/การตัดสินใจจากผู้ใช้จริง ให้ถามเฉพาะจุดนั้นพร้อมผลที่เตรียมแล้ว
- ไม่อ้างว่าส่งข้อความในอนาคตหรือทำงานเบื้องหลังต่อได้หาก runtime/session ไม่มีความสามารถนั้น
  ถ้าถูกจำกัดเวลา/context/เครื่องมือ ให้บันทึก checkpoint ที่ resume ได้และแจ้งเหตุผลจริง
- เกณฑ์และข้อจำกัดเรื่อง live runtime, shared providers, external messages และข้อมูลผู้ใช้ยังมีผล
  เตรียม candidate และทดสอบในพื้นที่แยกก่อนการกระทำที่ต้องใช้สิทธิ์เพิ่มเติม
- เมื่อครบขอบเขต ให้สรุปผลสุดท้ายครั้งเดียวพร้อม exact candidate, gates และสิ่งที่ยัง deferred
