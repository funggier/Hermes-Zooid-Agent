# Development Roadmap

Project READY_TO_START: งานแรก READY/UNASSIGNED รอผู้ใช้สั่งเริ่ม Zooid
การทำ CogentNexus-OpenClaw ให้เสร็จเป็นลำดับความสำคัญของผู้ใช้ ไม่มี automatic start trigger

เป้าหมายแรก: Zooid ติดตั้งและทำงานแยกจาก Hermes โดยคง skills ที่เข้ากันได้
การพัฒนาผ่าน CogentNexus-OpenClaw เป็นวิธีทำงาน ไม่ใช่ dependency runtime ของ Zooid

สถานะปัจจุบันอยู่ที่ [STATUS](coordination/STATUS.md) ตารางนี้เป็นลำดับและเกณฑ์ ไม่ใช่ผลทดสอบ

| ลำดับ / Task ID | งานและผลที่ต้องได้ | ขึ้นกับ | เกณฑ์ผ่าน |
| --- | --- | --- | --- |
| prepare-development-workspace | checkout แยก, toolchain inventory, baseline และ source map | ไม่มี | ระบุ exact HEAD, ทดสอบ baseline ที่เกี่ยวข้อง, ไม่มีการแตะ live runtime |
| disable-upstream-updates | ปิด program check/notify/update ทุก surface ที่เข้าถึงได้ เก็บโค้ด dormant | workspace | ไม่มี updater network/git/process mutation; skill fixture ยังใช้ได้ |
| isolate-runtime-storage | home/env/config/profile/database/cache/log/secret boundary | workspace | inherited HERMES_HOME ไม่ทำให้ Zooid เขียนข้อมูล Hermes; child process ใช้ Zooid root |
| separate-package-entrypoints | distribution, isolated environment, zooid CLI และ launcher | storage | เปิด zooid และ hermes คนละ environment ได้; lockfile/build สอดคล้อง |
| isolate-lifecycle-resources | process/service/task/IPC/port/single-instance ownership | entrypoints | Zooid stop/restart ไม่เลือก Hermes หรือ shared provider |
| separate-installation-identity | Windows installer/Desktop registration, fallback URLs, repair path | lifecycle + updater | bootstrap มาจาก Zooid และติดตั้งลงพื้นที่ตัวเอง |
| verify-skill-compatibility | load/install/update/remove พร้อม lock/cache/quarantine ของตัวเอง | storage + entrypoints | fixture ผ่าน; ระบุ skill ที่ต้องปรับ; ไม่ใช้โฟลเดอร์ร่วม |
| qualify-coexistence | build, install-over, reset/uninstall, coexistence | ทุกแถวก่อนหน้า | [acceptance matrix](acceptance/coexistence.md) ผ่านบน candidate ที่ระบุ |
| design-native-execution | Ticket-first, durable state, scheduler หนึ่งโมเดล, recovery/evidence/delivery | coexistence | ออกแบบและพิสูจน์วงจรเล็กก่อนเพิ่มความซับซ้อน |
| design-owned-updates | release channel และ updater ของ Zooid | release ที่ผ่าน coexistence | update/recovery ไม่พึ่ง Hermes upstream |

แผนเดิมเรียง home ก่อน updater; execution queue นี้ให้ปิด updater ก่อนตามความต้องการผู้ใช้
งานสองส่วนยังต้องผ่านก่อนติดตั้ง ไม่ถือว่าปิด updater อย่างเดียวทำให้แยกโปรแกรมสำเร็จ

## วิธีแตกงานโดยไม่วางแผนหนักเกินไป

เตรียมรายละเอียดเฉพาะ task ที่กำลังจะทำตาม [template](templates/task.md)
แบ่งเพิ่มเมื่อพบ ownership ต่างกันหรือไม่สามารถทดสอบจบในขอบเขตเดียว
บันทึก dependency และเหตุผลที่แบ่งใน WORKLOG ห้ามวนวิเคราะห์โดยไม่มีสิ่งที่ตรวจสอบได้
งาน blocked ให้บันทึกผลตรวจและเงื่อนไขปลดบล็อก; ไปงานอิสระได้เมื่อ ACTIVE ระบุชัด
ไม่เพิ่ม multi-agent, ticket engine หรือ refactor ใหญ่ระหว่างการแยก product identity
