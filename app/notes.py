from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.db import get_db
from app.auth import login_required

notes_bp = Blueprint("notes", __name__, url_prefix="/api/notes")

def calculate_reminder_status(deadline_str, is_completed):
    if is_completed:
        return "completed"
    if not deadline_str:
        return "none"
    try:
        # Normalize ISO formats
        clean_deadline = deadline_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_deadline)
        if dt.tzinfo is not None:
            now = datetime.now(dt.tzinfo)
        else:
            now = datetime.now()

        if dt < now:
            return "overdue"
        elif dt.date() == now.date():
            return "due_today"
        else:
            return "upcoming"
    except (ValueError, TypeError):
        return "none"

def row_to_dict(row):
    deadline = row["deadline"]
    is_completed = bool(row["is_completed"])
    status = calculate_reminder_status(deadline, is_completed)
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "title": row["title"],
        "content": row["content"],
        "deadline": deadline,
        "is_completed": is_completed,
        "status": status,
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }

@notes_bp.route("", methods=["GET"])
@login_required
def list_notes():
    user_id = session["user_id"]
    filter_type = request.args.get("filter", "all").lower()
    db = get_db()

    if filter_type == "reminders":
        query = """
            SELECT * FROM notes 
            WHERE user_id = ? AND deadline IS NOT NULL AND deadline != '' AND is_completed = 0
            ORDER BY deadline ASC
        """
        rows = db.execute(query, (user_id,)).fetchall()
    elif filter_type == "completed":
        query = """
            SELECT * FROM notes 
            WHERE user_id = ? AND is_completed = 1
            ORDER BY updated_at DESC
        """
        rows = db.execute(query, (user_id,)).fetchall()
    else:
        # Default all: incomplete first, then ordered by deadline if present, then newest
        query = """
            SELECT * FROM notes 
            WHERE user_id = ?
            ORDER BY is_completed ASC, 
                     CASE WHEN deadline IS NOT NULL AND deadline != '' THEN 0 ELSE 1 END,
                     deadline ASC, 
                     updated_at DESC
        """
        rows = db.execute(query, (user_id,)).fetchall()

    return jsonify([row_to_dict(r) for r in rows]), 200

@notes_bp.route("", methods=["POST"])
@login_required
def create_note():
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = data.get("content", "")
    deadline = data.get("deadline")

    if not title:
        return jsonify({"error": "Title is required."}), 400

    # Validate deadline format if provided
    if deadline:
        deadline = str(deadline).strip()
        try:
            datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid deadline format. Use ISO format (e.g. YYYY-MM-DDTHH:MM)."}), 400
    else:
        deadline = None

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO notes (user_id, title, content, deadline, is_completed)
        VALUES (?, ?, ?, ?, 0)
        """,
        (user_id, title, content, deadline)
    )
    db.commit()
    note_id = cursor.lastrowid

    row = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return jsonify(row_to_dict(row)), 201

@notes_bp.route("/<int:note_id>", methods=["GET"])
@login_required
def get_note(note_id):
    user_id = session["user_id"]
    db = get_db()
    row = db.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, user_id)
    ).fetchone()

    if row is None:
        return jsonify({"error": "Note not found."}), 404

    return jsonify(row_to_dict(row)), 200

@notes_bp.route("/<int:note_id>", methods=["PUT"])
@login_required
def update_note(note_id):
    user_id = session["user_id"]
    db = get_db()
    existing = db.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, user_id)
    ).fetchone()

    if existing is None:
        return jsonify({"error": "Note not found."}), 404

    data = request.get_json(silent=True) or {}
    
    title = data.get("title", existing["title"])
    if isinstance(title, str):
        title = title.strip()
    if not title:
        return jsonify({"error": "Title cannot be empty."}), 400

    content = data.get("content", existing["content"])
    
    if "deadline" in data:
        raw_deadline = data.get("deadline")
        if raw_deadline:
            raw_deadline = str(raw_deadline).strip()
            try:
                datetime.fromisoformat(raw_deadline.replace("Z", "+00:00"))
                deadline = raw_deadline
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid deadline format. Use ISO format."}), 400
        else:
            deadline = None
    else:
        deadline = existing["deadline"]

    if "is_completed" in data:
        is_completed = 1 if data["is_completed"] else 0
    else:
        is_completed = existing["is_completed"]

    db.execute(
        """
        UPDATE notes 
        SET title = ?, content = ?, deadline = ?, is_completed = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """,
        (title, content, deadline, is_completed, note_id, user_id)
    )
    db.commit()

    updated = db.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, user_id)
    ).fetchone()

    return jsonify(row_to_dict(updated)), 200

@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    user_id = session["user_id"]
    db = get_db()
    row = db.execute(
        "SELECT id FROM notes WHERE id = ? AND user_id = ?",
        (note_id, user_id)
    ).fetchone()

    if row is None:
        return jsonify({"error": "Note not found."}), 404

    db.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
    db.commit()
    return jsonify({"message": "Note deleted successfully."}), 200
