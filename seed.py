"""
Master seed script for Swahilipot Hub Admin Platform.
Creates: 6 departments + superadmin + 22 sample assets.

Usage:
    python manage.py shell < seed.py
"""

from django.contrib.auth.models import User
from datetime import date
from assets_app.models import Asset, Department, StaffProfile, AssetType


# ── STEP 1 — DEPARTMENTS ──────────────────────────────────

print("=" * 50)
print("STEP 1 — Creating departments...")
print("=" * 50)

departments = [
    ("Administration",           "Handles assets, records, facilities, and general operations of the hub."),
    ("Finance",                  "Manages budgets, expenditure, grants, and financial reporting."),
    ("Technology",               "Runs tech programs: Data & Research, Digital Literacy, Industrial Attachment, Campus Ambassador, Pitching Thursday."),
    ("Community Service",        "Leads mentorship, GOYN initiative, Youth Hub Networks, and entrepreneurship training."),
    ("Communication & Media",    "Manages SwahiliPot FM, social media, Sanaa Show, Saanart Shop, and PR."),
    ("Creative Arts & Heritage", "Oversees acting, voice arts, exhibitions, and heritage site technology integration."),
]

for name, desc in departments:
    dept, created = Department.objects.get_or_create(name=name, defaults={"description": desc})
    print(f"  {'Created' if created else 'Already exists'}: {name}")

print()


# ── STEP 2 — ASSET TYPES ──────────────────────────────────

print("=" * 50)
print("STEP 2 — Creating asset types...")
print("=" * 50)

asset_types = [
    ("Electronics", "Computers, printers, monitors, keyboards, mice, cables, and other IT equipment."),
    ("Furniture", "Desks, chairs, tables, shelves, cabinets, and office furniture."),
    ("Equipment", "Machinery, tools, cameras, projectors, and specialized equipment."),
    ("Vehicles", "Cars, motorcycles, bicycles, and transportation assets."),
    ("Stationery & Supplies", "Paper, pens, notebooks, ink cartridges, and office supplies."),
    ("Facility", "Building infrastructure, HVAC systems, electrical panels, and facility infrastructure."),
    ("Software & Licenses", "Software licenses, subscriptions, and digital tools."),
    ("Audio/Visual", "Speakers, microphones, projectors, screens, and recording equipment."),
    ("Networking", "Routers, switches, cables, WiFi equipment, and network infrastructure."),
    ("Office Equipment", "Photocopiers, scanners, shredders, and office machines."),
    ("Security", "Cameras, alarms, locks, and security systems."),
    ("Appliances", "Refrigerators, microwaves, water dispensers, and kitchen appliances."),
    ("Books & Media", "Books, manuals, DVDs, and physical media."),
    ("Other", "Miscellaneous items that don't fit other categories."),
]

for name, desc in asset_types:
    asset_type, created = AssetType.objects.get_or_create(name=name, defaults={"description": desc})
    print(f"  {'Created' if created else 'Already exists'}: {name}")

print()


# ── STEP 3 — SUPERADMIN ───────────────────────────────────

print("=" * 50)
print("STEP 3 — Creating superadmin account...")
print("=" * 50)

if not User.objects.filter(username="admin").exists():
    admin_user = User.objects.create_superuser(
        username="admin",
        password="SwahilipotAdmin2024!",
        first_name="System",
        last_name="Admin",
        email="admin@swahilipothub.co.ke",
    )
    StaffProfile.objects.create(
        user=admin_user,
        role="superadmin",
        department=Department.objects.get(name="Administration"),
    )
    print("  Superadmin created.")
    print("  Username : admin")
    print("  Password : SwahilipotAdmin2024!")
    print("  >>> Change this password immediately after first login!")
else:
    print("  Superadmin 'admin' already exists — skipped.")
    admin_user = User.objects.get(username="admin")

print()


# ── STEP 4 — SAMPLE ASSETS ────────────────────────────────

print("=" * 50)
print("STEP 4 — Adding sample assets...")
print("=" * 50)

def dept(name):
    return Department.objects.get(name=name)

assets_data = [

    # ADMINISTRATION
    {
        "asset_name": "HP LaserJet Printer", "asset_label": "SPH-ELEC-0001",
        "description": "Black and white laser printer. Good condition. Located at reception. Used for printing official documents and reports.",
        "asset_type": "electronics", "department": "Administration",
        "acquired_by_name": "Ali Mahmoud", "acquisition_date": date(2023, 3, 10),
        "status": "available", "serial_number": "HPLJ-2023-00142",
        "next_maintenance": date(2026, 6, 1), "notes": "Toner replaced March 2024.",
    },
    {
        "asset_name": "Reception Desk", "asset_label": "SPH-FURN-0001",
        "description": "Large wooden L-shaped reception desk. Brown finish. Main entrance. Has 3 drawers on right side.",
        "asset_type": "furniture", "department": "Administration",
        "acquired_by_name": "Ali Mahmoud", "acquisition_date": date(2022, 1, 15),
        "status": "available", "serial_number": "",
        "next_maintenance": None, "notes": "One drawer hinge needs tightening.",
    },
    {
        "asset_name": "Office Chair Set (x6)", "asset_label": "SPH-FURN-0002",
        "description": "Set of 6 black padded office chairs with adjustable height. Used in the main admin office.",
        "asset_type": "furniture", "department": "Administration",
        "acquired_by_name": "Ali Mahmoud", "acquisition_date": date(2022, 1, 15),
        "status": "available", "serial_number": "",
        "next_maintenance": None, "notes": "",
    },
    {
        "asset_name": "Canon Photocopier", "asset_label": "SPH-EQUIP-0001",
        "description": "Canon IR2625 multifunction photocopier. Prints, scans and copies. Admin office. Paper tray 500 sheets.",
        "asset_type": "equipment", "department": "Administration",
        "acquired_by_name": "Ali Mahmoud", "acquisition_date": date(2023, 6, 20),
        "status": "maintenance", "serial_number": "CNIR-2023-88421",
        "next_maintenance": date(2026, 4, 20), "notes": "Paper jam sensor faulty. Technician scheduled.",
    },
    {
        "asset_name": "Filing Cabinet (4-drawer)", "asset_label": "SPH-FURN-0003",
        "description": "Grey steel 4-drawer filing cabinet with lock and key. Stores admin documents and contracts.",
        "asset_type": "furniture", "department": "Administration",
        "acquired_by_name": "Ali Mahmoud", "acquisition_date": date(2021, 8, 5),
        "status": "available", "serial_number": "",
        "next_maintenance": None, "notes": "Key kept with admin manager.",
    },

    # TECHNOLOGY
    {
        "asset_name": "Dell Laptop 15 inch", "asset_label": "SPH-ELEC-0002",
        "description": "Dell Inspiron 15 3000. Intel Core i5, 8GB RAM, 256GB SSD. Black. Used for tech training sessions.",
        "asset_type": "electronics", "department": "Technology",
        "acquired_by_name": "Fatuma Hassan", "acquisition_date": date(2023, 9, 1),
        "status": "in_use", "serial_number": "DELL-INS-2023-00451",
        "next_maintenance": date(2026, 9, 1), "notes": "Currently in use by Pitching Thursday team.",
    },
    {
        "asset_name": "Lenovo ThinkPad X1", "asset_label": "SPH-ELEC-0003",
        "description": "Lenovo ThinkPad X1 Carbon. Intel Core i7, 16GB RAM, 512GB SSD. Silver. Data and research program.",
        "asset_type": "electronics", "department": "Technology",
        "acquired_by_name": "Fatuma Hassan", "acquisition_date": date(2023, 9, 1),
        "status": "available", "serial_number": "LEN-X1-2023-00214",
        "next_maintenance": date(2026, 9, 1), "notes": "",
    },
    {
        "asset_name": "Projector — Epson EB-X51", "asset_label": "SPH-ELEC-0004",
        "description": "Epson EB-X51 projector. 3600 lumens. For training and pitching events. Includes HDMI and VGA cables.",
        "asset_type": "electronics", "department": "Technology",
        "acquired_by_name": "Fatuma Hassan", "acquisition_date": date(2022, 11, 3),
        "status": "available", "serial_number": "EPS-EB-2022-00089",
        "next_maintenance": date(2026, 5, 15), "notes": "Lamp hours at 60%. Replace at 80%.",
    },
    {
        "asset_name": "Projector Screen (120 inch)", "asset_label": "SPH-EQUIP-0002",
        "description": "Manual pull-down projector screen. 120 inch diagonal. White matte. Main training hall.",
        "asset_type": "equipment", "department": "Technology",
        "acquired_by_name": "Fatuma Hassan", "acquisition_date": date(2022, 11, 3),
        "status": "available", "serial_number": "",
        "next_maintenance": None, "notes": "",
    },
    {
        "asset_name": "Raspberry Pi 4 Kit (x5)", "asset_label": "SPH-ELEC-0005",
        "description": "5 units Raspberry Pi 4 Model B (4GB RAM each). For digital literacy and coding bootcamps.",
        "asset_type": "electronics", "department": "Technology",
        "acquired_by_name": "Fatuma Hassan", "acquisition_date": date(2024, 2, 14),
        "status": "available", "serial_number": "",
        "next_maintenance": None, "notes": "SD cards pre-loaded with Raspberry Pi OS and Python 3.",
    },

    # FINANCE
    {
        "asset_name": "HP EliteBook 840", "asset_label": "SPH-ELEC-0006",
        "description": "HP EliteBook 840 G8. Intel Core i5, 8GB RAM, 256GB SSD. Finance use only. Password protected.",
        "asset_type": "electronics", "department": "Finance",
        "acquired_by_name": "Omar Sharif", "acquisition_date": date(2023, 4, 5),
        "status": "in_use", "serial_number": "HP-840-2023-00334",
        "next_maintenance": date(2026, 4, 5), "notes": "Do not share. Contains financial data.",
    },
    {
        "asset_name": "Safe Box (Small)", "asset_label": "SPH-EQUIP-0003",
        "description": "Electronic safe box for petty cash, cheques and sensitive documents. Finance office. Code with Finance Manager.",
        "asset_type": "equipment", "department": "Finance",
        "acquired_by_name": "Omar Sharif", "acquisition_date": date(2021, 5, 20),
        "status": "available", "serial_number": "SAFE-2021-00011",
        "next_maintenance": None, "notes": "Battery replaced January 2025.",
    },
    {
        "asset_name": "Office Desk — Finance", "asset_label": "SPH-FURN-0004",
        "description": "Rectangular wooden desk. Light oak finish. Finance Manager's desk. Lockable side drawer.",
        "asset_type": "furniture", "department": "Finance",
        "acquired_by_name": "Omar Sharif", "acquisition_date": date(2021, 5, 20),
        "status": "available", "serial_number": "",
        "next_maintenance": None, "notes": "",
    },

    # COMMUNICATION & MEDIA
    {
        "asset_name": "Canon EOS 200D Camera", "asset_label": "SPH-EQUIP-0004",
        "description": "Canon EOS 200D DSLR. 24.1MP. 18-55mm lens, 2 batteries, charger, 64GB card. Events and Sanaa Show.",
        "asset_type": "equipment", "department": "Communication & Media",
        "acquired_by_name": "Salma Juma", "acquisition_date": date(2023, 7, 18),
        "status": "available", "serial_number": "CNEOS-2023-00772",
        "next_maintenance": date(2026, 7, 18), "notes": "Sensor cleaned Oct 2024. Store in padded bag.",
    },
    {
        "asset_name": "Rode Wireless Microphone Set", "asset_label": "SPH-EQUIP-0005",
        "description": "Rode Wireless GO II. Dual-channel wireless mic. For FM broadcasts and events. 2 transmitters, 1 receiver.",
        "asset_type": "equipment", "department": "Communication & Media",
        "acquired_by_name": "Salma Juma", "acquisition_date": date(2023, 7, 18),
        "status": "in_use", "serial_number": "RODE-WG2-2023-00091",
        "next_maintenance": None, "notes": "Currently in use for FM broadcast recording.",
    },
    {
        "asset_name": "iMac 24 inch — Media Workstation", "asset_label": "SPH-ELEC-0007",
        "description": "Apple iMac 24 inch (2023). M3 chip, 16GB RAM, 512GB SSD. Blue. Adobe Premiere, Photoshop, Audacity installed.",
        "asset_type": "electronics", "department": "Communication & Media",
        "acquired_by_name": "Salma Juma", "acquisition_date": date(2024, 1, 8),
        "status": "available", "serial_number": "APIMAC-2024-00003",
        "next_maintenance": date(2027, 1, 8), "notes": "Adobe CC license renewal: Jan 2026.",
    },
    {
        "asset_name": "Audio Mixer — Yamaha MG10", "asset_label": "SPH-EQUIP-0006",
        "description": "Yamaha MG10 10-channel mixing console. SwahiliPot FM studio for live broadcasts and podcast recordings.",
        "asset_type": "equipment", "department": "Communication & Media",
        "acquired_by_name": "Salma Juma", "acquisition_date": date(2022, 8, 30),
        "status": "available", "serial_number": "YAM-MG10-2022-00044",
        "next_maintenance": date(2026, 8, 30), "notes": "",
    },

    # COMMUNITY SERVICE
    {
        "asset_name": "Asus VivoBook Laptop", "asset_label": "SPH-ELEC-0008",
        "description": "Asus VivoBook 15. AMD Ryzen 5, 8GB RAM, 512GB SSD. Community Service for case management and GOYN data entry.",
        "asset_type": "electronics", "department": "Community Service",
        "acquired_by_name": "Hillary Mutuma", "acquisition_date": date(2023, 10, 10),
        "status": "available", "serial_number": "ASUS-VB-2023-00561",
        "next_maintenance": date(2026, 10, 10), "notes": "",
    },
    {
        "asset_name": "Portable Whiteboard", "asset_label": "SPH-EQUIP-0007",
        "description": "Double-sided portable whiteboard on wheels. 120cm x 90cm. Mentorship sessions and workshops.",
        "asset_type": "equipment", "department": "Community Service",
        "acquired_by_name": "Hillary Mutuma", "acquisition_date": date(2022, 3, 14),
        "status": "available", "serial_number": "",
        "next_maintenance": None, "notes": "Markers in supply drawer. Replenish when low.",
    },
    {
        "asset_name": "Plastic Chairs (x20)", "asset_label": "SPH-FURN-0005",
        "description": "20 white plastic stackable chairs. Community events, training and outdoor gatherings. Storage room.",
        "asset_type": "furniture", "department": "Community Service",
        "acquired_by_name": "Hillary Mutuma", "acquisition_date": date(2021, 11, 1),
        "status": "available", "serial_number": "",
        "next_maintenance": None, "notes": "2 chairs cracked — set aside. Effectively 18 usable.",
    },

    # CREATIVE ARTS & HERITAGE
    {
        "asset_name": "DJI Drone — Mavic Air 2", "asset_label": "SPH-EQUIP-0008",
        "description": "DJI Mavic Air 2. 4K camera. Aerial photography at heritage sites and events. 3 batteries and carrying case.",
        "asset_type": "equipment", "department": "Creative Arts & Heritage",
        "acquired_by_name": "Amina Suleiman", "acquisition_date": date(2024, 3, 22),
        "status": "available", "serial_number": "DJI-MA2-2024-00017",
        "next_maintenance": date(2026, 3, 22), "notes": "Requires CAA Kenya flight clearance at heritage sites.",
    },
    {
        "asset_name": "Portable PA System", "asset_label": "SPH-EQUIP-0009",
        "description": "Mackie Thump15A 1300W PA speaker with stand. Outdoor performances, Sanaa Show and community events.",
        "asset_type": "equipment", "department": "Creative Arts & Heritage",
        "acquired_by_name": "Amina Suleiman", "acquisition_date": date(2023, 2, 5),
        "status": "available", "serial_number": "MAC-T15A-2023-00033",
        "next_maintenance": date(2026, 2, 5), "notes": "",
    },
    {
        "asset_name": "Costume Storage Rack", "asset_label": "SPH-FURN-0006",
        "description": "Heavy duty metal clothing rack on wheels. Performance costumes for acting and cultural events. Backstage.",
        "asset_type": "furniture", "department": "Creative Arts & Heritage",
        "acquired_by_name": "Amina Suleiman", "acquisition_date": date(2022, 6, 10),
        "status": "available", "serial_number": "",
        "next_maintenance": None, "notes": "Label each costume bag with production name and size.",
    },
    {
        "asset_name": "Digital Drawing Tablet — Wacom", "asset_label": "SPH-ELEC-0009",
        "description": "Wacom Intuos Pro Medium. Digital artists in Saanart Shop for illustration and graphic design.",
        "asset_type": "electronics", "department": "Creative Arts & Heritage",
        "acquired_by_name": "Amina Suleiman", "acquisition_date": date(2024, 5, 3),
        "status": "lost", "serial_number": "WAC-ITP-2024-00009",
        "next_maintenance": None, "notes": "Reported lost April 2025. Investigation ongoing.",
    },
]

created_count = 0
skipped_count = 0

for data in assets_data:
    label = data["asset_label"]
    if Asset.objects.filter(asset_label=label).exists():
        print(f"  Skipped (exists): {label}")
        skipped_count += 1
        continue
    asset = Asset.objects.create(
        asset_name       = data["asset_name"],
        asset_label      = label,
        description      = data["description"],
        asset_type       = data["asset_type"],
        department       = dept(data["department"]),
        acquired_by_name = data["acquired_by_name"],
        acquisition_date = data["acquisition_date"],
        status           = data["status"],
        serial_number    = data.get("serial_number", ""),
        next_maintenance = data.get("next_maintenance"),
        notes            = data.get("notes", ""),
        registered_by    = admin_user,
    )
    print(f"  Created: {asset.asset_label} — {asset.asset_name} [{asset.department}]")
    created_count += 1

print()
print("=" * 50)
print("Seeding complete!")
print(f"  Departments : {Department.objects.count()}")
print(f"  Assets added: {created_count} ({skipped_count} skipped)")
print(f"  Admin login : admin / SwahilipotAdmin2024!")
print("=" * 50)
print("Next  -> python manage.py runserver")
print("Then  -> http://127.0.0.1:8000")