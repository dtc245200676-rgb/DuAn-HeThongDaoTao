def program_dict(p):
    return {"id": p.id, "code": p.code, "name": p.name, "description": p.description, "total_duration_hours": p.total_duration_hours, "standard_tuition": float(p.standard_tuition or 0), "status": p.status}

def subject_dict(s):
    return {"id": s.id, "code": s.code, "name": s.name, "session_count": s.session_count, "weight": s.weight, "description": s.description, "learning_outcomes": s.learning_outcomes}

def session_dict(x):
    return {"id": x.id, "subject_id": x.subject_id, "sequence": x.sequence, "topic": x.topic, "objective": x.objective}
