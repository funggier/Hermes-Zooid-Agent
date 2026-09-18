# Coexistence Acceptance

สถานะเริ่มต้นทุกแถว: NOT_RUN ไม่มีผลทดสอบจากเอกสารนี้เอง
เริ่มใน Windows VM/test account ที่แยกก่อนทดสอบบนเครื่องใช้งานจริง
รายงาน OS, installed Hermes version/source, Zooid candidate SHA, installer SHA-256,
commands, logs, before/after state และขอบเขตสิทธิ์ของการทดสอบ

| Gate | การทดสอบ | หลักฐานที่ต้องเห็น |
| --- | --- | --- |
| Home isolation | inherited HERMES_HOME, default/custom Zooid root, profiles, child processes | Zooid ไม่เลือก root ของ Hermes; sentinel data ไม่เปลี่ยน |
| Package/CLI | ติดตั้งและเรียก hermes กับ zooid จาก shell ใหม่ | launcher/interpreter/install path แยก |
| Desktop | เปิดทั้งสองแอป | app ID, userData, protocol, shortcut และ single-instance lock แยก |
| Network/IPC | listeners ทุกตัวพร้อมกัน และ occupied-port case | ports/pipe/socket แยก; conflict error ไม่หยุดอีกผลิตภัณฑ์ |
| Lifecycle | Zooid start/stop/restart รวมทุก profile | Hermes/OpenClaw/executor/shared provider ยังทำงาน |
| Update disable | explicit/background checks และ UI/CLI update entrypoints | ไม่มี program update network/git/dependency/lifecycle side effects |
| Skills | local fixture install/load/update/remove | Zooid skills/lock/quarantine/cache เปลี่ยนเฉพาะ root ของตน |
| Install-over | candidate ติดตั้งทับ Zooid | ข้อมูลที่ contract กำหนดคงอยู่; Hermes ไม่เปลี่ยน |
| Reset | ยืนยัน scope แล้ว reset Zooid | ล้างเฉพาะข้อมูลตาม contract; Hermes sentinel อยู่ครบ |
| Uninstall | ถอน Zooid | ลบเฉพาะ owned paths/registrations; Hermes เรียกใช้งานได้ |
| Boundaries | custom roots, symlink/junction, profiles | ไม่มี cleanup ข้าม root แม้ชื่อหรือ path คล้ายกัน |

sentinel checksum อย่างเดียวไม่พิสูจน์ทุกอย่าง ต้องรวม process/registration/command targets
การตรวจ sentinel ใน VM ทำกับข้อมูลทดสอบ ไม่คัดลอก secrets จริงลง report หรือ repo
external provider เช่น Ollama อาจแชร์โดยตั้งใจได้ แต่ไม่อยู่ในขอบเขต cleanup ของ Zooid
bot-token/session conflict ต้องใช้ identity แยกตามข้อกำหนดของ provider
skill fixture ผ่านไม่แปลว่า skills ภายนอกทุกตัว compatible หรือมี license เหมือนกัน

## สรุป candidate

รายงานแต่ละ gate เป็น PASS/FAIL/BLOCKED/NOT_RUN
ห้ามเรียก candidate ว่า qualified หาก required gate ยังไม่ผ่าน
เมื่อ production source หรือ packaging เปลี่ยนหลังทดสอบ ให้ประเมินและรันทดสอบที่ได้รับผลกระทบ
ผลจากคนละ SHA นำมารวมเป็นการผ่าน candidate เดียวไม่ได้โดยไม่มีคำอธิบายความเทียบเท่า
