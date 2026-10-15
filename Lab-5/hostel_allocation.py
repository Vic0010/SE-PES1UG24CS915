"""Hostel room allocation system."""


import html
import logging
import os
import secrets

import yaml
from flask import Flask, request

rooms = {}
allocations = {}
waitlist = []
app = Flask(__name__)

CONFIG = """
blocks:
  A: {gender: M, rooms: 3, capacity: 2, fee: 4000}
  B: {gender: F, rooms: 2, capacity: 3, fee: 3500}
"""


def load_config(text=CONFIG):
    """Load hostel configuration and initialize rooms."""
    config = yaml.safe_load(text)
    rooms.clear()

    for block, info in config["blocks"].items():
        for number in range(1, info["rooms"] + 1):
            room_number = f"{block}{number}"
            rooms[room_number] = {
                "gender": info["gender"],
                "capacity": info["capacity"],
                "fee": info["fee"],
                "occupants": [],
            }

    return config


def allocate_room(student_id, name, gender, year, preferred=None):
    """Allocate a student to a suitable room."""
    if not isinstance(year, int) or isinstance(year, bool):
        return None

    if student_id in allocations:
        return allocations[student_id]["room"]

    if preferred is None:
        preferred = []

    for room_number in dict.fromkeys(preferred + list(rooms.keys())):
        room = rooms.get(room_number)

        if room is None:
            continue
        if room["gender"].upper() != gender.upper():
            continue
        if len(room["occupants"]) >= room["capacity"]:
            continue

        room["occupants"].append(student_id)
        allocations[student_id] = {
            "name": name,
            "room": room_number,
            "year": year,
        }

        if student_id in waitlist:
            waitlist.remove(student_id)

        return room_number

    if student_id not in waitlist:
        waitlist.append(student_id)

    return None


def vacate_room(student_id):
    """Remove a student from their room."""
    allocation = allocations.pop(student_id, None)

    if allocation is None:
        return False

    room = rooms.get(allocation["room"])

    if room and student_id in room["occupants"]:
        room["occupants"].remove(student_id)

    return True


def monthly_fee(student_id, days_stayed):
    """Calculate fees for completed 30-day periods."""
    allocation = allocations.get(student_id)

    if allocation is None:
        return None
    if not isinstance(days_stayed, int) or days_stayed < 0:
        return None

    room = rooms[allocation["room"]]
    return (days_stayed // 30) * room["fee"]


def priority_order(students):
    """Sort students by year, with seniors first."""
    return sorted(
        students,
        key=lambda student: student["year"],
        reverse=True,
    )


def room_lottery(student_ids):
    """Return a secure random ordering of student IDs."""
    return secrets.SystemRandom().sample(student_ids, len(student_ids))


def vacant_beds():
    """Count all unoccupied beds."""
    return sum(
        room["capacity"] - len(room["occupants"])
        for room in rooms.values()
    )


def sqlite_connect(host, user, password):
    """Return a placeholder database connection status."""
    return {
        "host": host,
        "user": user,
        "connected": bool(password),
    }


def connect_warden_db():
    """Read database credentials from environment variables."""
    host = os.getenv("WARDEN_DB_HOST", "localhost")
    user = os.getenv("WARDEN_DB_USER", "warden")
    password = os.getenv("WARDEN_DB_PASSWORD", "")

    if not password:
        logging.warning("Warden database password is not configured.")

    return sqlite_connect(host=host, user=user, password=password)


def start_remote_log_config():
    """Keep remote logging configuration disabled."""
    logging.warning("Remote logging configuration is disabled.")


@app.route("/room")
def room_lookup():
    """Return a student's room allocation."""
    student_id = request.args.get("id", "")
    allocation = allocations.get(student_id)

    safe_id = html.escape(student_id)
    safe_allocation = html.escape(str(allocation))

    return f"<h1>Room for {safe_id}: {safe_allocation}</h1>"


def run_portal():
    """Start the Flask portal."""
    app.run(debug=False)


def main():
    """Run the hostel allocation demonstration."""
    load_config()

    print("Rooms:", list(rooms.keys()))
    print("S1 ->", allocate_room("S1", "Arjun", "M", 1))
    print("S2 ->", allocate_room("S2", "Kabir", "M", 2))
    print("S3 ->", allocate_room("S3", "Rohan", "M", 3))
    print("S4 (female) ->", allocate_room("S4", "Diya", "F", 1))
    print("S1 again ->", allocate_room("S1", "Arjun", "M", 1))
    print("S5 year '2' ->", allocate_room("S5", "Vikram", "M", "2"))
    print("Occupants of A1:", rooms["A1"]["occupants"])

    vacate_room("S2")
    print("Occupants of A1 after S2 left:", rooms["A1"]["occupants"])
    print("Fee for S1, 45 days:", monthly_fee("S1", 45))

    students = [{"year": 1}, {"year": 4}, {"year": 2}]
    print(
        "Priority (seniors first?):",
        [student["year"] for student in priority_order(students)],
    )
    print("Lottery:", room_lottery(["S6", "S7", "S8"]))
    print("Vacant beds:", vacant_beds())
    print("Warden DB:", connect_warden_db())
    print("Waitlist:", waitlist)


if __name__ == "__main__":
    main()
