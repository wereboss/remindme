from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.db import get_db
from app.auth import login_required

notes_bp = Blueprint("notes", __name__, url_prefix="/api/notes")

def normalize_tags(raw_tags):
    if raw_tags is None:
        return ""
    if isinstance(raw_tags, list):
        tag_list = raw_tags
    else:
        # Split by comma
        tag_list = str(raw_tags).split(",")
    
    cleaned = []
    for t in tag_list:
        clean = str(t).strip().lower().lstrip("#")
        if clean and clean not in cleaned:
            cleaned.append(clean)
    return ",".join(cleaned)

def calculate_reminder_status(deadline_str, is_completed):
    if is_completed:
        return "completed"
    if not deadline_str:
        return "none"
    try:
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
    is_archived = bool(row["is_archived"])
    status = calculate_reminder_status(deadline, is_completed)
    tags_str = row["tags"] if "tags" in row.keys() and row["tags"] else ""
    tag_list = [t for t in tags_str.split(",") if t]

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "title": row["title"],
        "content": row["content"],
        "deadline": deadline,
        "tags": tag_list,
        "tags_str": tags_str,
        "is_completed": is_completed,
        "is_archived": is_archived,
        "status": status,
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }

@notes_bp.route("", methods=["GET"])
@login_required
def list_notes():
    user_id = session["user_id"]
    filter_type = request.args.get("filter", "all").lower()
    q = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip().lower().lstrip("#")
    db = get_db()

    conditions = ["user_id = ?"]
    params = [user_id]

    if filter_type == "archived":
        conditions.append("is_archived = 1")
    else:
        conditions.append("is_archived = 0")
        if filter_type == "reminders":
            conditions.append("deadline IS NOT NULL AND deadline != '' AND is_completed = 0")
        elif filter_type == "completed":
            conditions.append("is_completed = 1")

    if q:
        conditions.append("(LOWER(title) LIKE ? OR LOWER(content) LIKE ?)")
        search_term = f"%{q.lower()}%"
        params.extend([search_term, search_term])

    if tag:
        conditions.append("(',' || tags || ',') LIKE ?")
        params.append(f"%,{tag},%")

    where_clause = " AND ".join(conditions)

    if filter_type == "reminders":
        order_clause = "ORDER BY deadline ASC"
    elif filter_type in ("completed", "archived"):
        order_clause = "ORDER BY updated_at DESC"
    else:
        order_clause = """
            ORDER BY is_completed ASC, 
                     CASE WHEN deadline IS NOT NULL AND deadline != '' THEN 0 ELSE 1 END,
                     deadline ASC, 
                     updated_at DESC
        """

    query = f"SELECT * FROM notes WHERE {where_clause} {order_clause}"
    rows = db.execute(query, params).fetchall()

    return jsonify([row_to_dict(r) for r in rows]), 200

@notes_bp.route("", methods=["POST"])
@login_required
def create_note():
    user_id = session["user_id"]
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    content = data.get("content", "")
    deadline = data.get("deadline")
    tags = normalize_tags(data.get("tags", ""))

    if not title:
        return jsonify({"error": "Title is required."}), 400

    if deadline:
        deadline = str(deadline).strip()
        try:
            datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid deadline format. Use ISO format."}), 400
    else:
        deadline = None

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO notes (user_id, title, content, deadline, tags, is_completed, is_archived)
        VALUES (?, ?, ?, ?, ?, 0, 0)
        """,
        (user_id, title, content, deadline, tags)
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

    if "tags" in data:
        tags = normalize_tags(data.get("tags"))
    else:
        tags = existing["tags"] if "tags" in existing.keys() else ""

    if "is_completed" in data:
        is_completed = 1 if data["is_completed"] else 0
    else:
        is_completed = existing["is_completed"]

    if "is_archived" in data:
        is_archived = 1 if data["is_archived"] else 0
    else:
        is_archived = existing["is_archived"] if "is_archived" in existing.keys() else 0

    db.execute(
        """
        UPDATE notes 
        SET title = ?, content = ?, deadline = ?, tags = ?, is_completed = ?, is_archived = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
        """,
        (title, content, deadline, tags, is_completed, is_archived, note_id, user_id)
    )
    db.commit()

    updated = db.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?",
        (note_id, user_id)
    ).fetchone()

    return jsonify(row_to_dict(updated)), 200

@notes_bp.route("/<int:note_id>/archive", methods=["POST", "PUT"])
@login_required
def archive_note(note_id):
    user_id = session["user_id"]
    db = get_db()
    existing = db.execute("SELECT id FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id)).fetchone()
    if existing is None:
        return jsonify({"error": "Note not found."}), 404

    db.execute("UPDATE notes SET is_archived = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?", (note_id, user_id))
    db.commit()
    updated = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return jsonify(row_to_dict(updated)), 200

@notes_bp.route("/<int:note_id>/unarchive", methods=["POST", "PUT"])
@login_required
def unarchive_note(note_id):
    user_id = session["user_id"]
    db = get_db()
    existing = db.execute("SELECT id FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id)).fetchone()
    if existing is None:
        return jsonify({"error": "Note not found."}), 404

    db.execute("UPDATE notes SET is_archived = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?", (note_id, user_id))
    db.commit()
    updated = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
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
