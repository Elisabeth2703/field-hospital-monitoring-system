from mongodb_utils import MongoDBManager


mongo = MongoDBManager()


broken_qr_codes = [
    "da7538cd-164e-415b-b873-b9f5a361af44",
   
]

for qr in broken_qr_codes:
    eq = mongo.get_equipment(qr)
    if eq:
        deleted = mongo.delete_equipment(qr)
        print(f"✅ Видалено: {qr} (кількість видалених: {deleted})")
    else:
        print(f"⚠️ Запис не знайдено у базі: {qr}")


all_eq = mongo.get_all_equipment()
print(f"\nЗалишилося записів: {len(all_eq)}")
for e in all_eq:
    print(f"- {e['name']} ({e['qr_code']})")


mongo.close()
