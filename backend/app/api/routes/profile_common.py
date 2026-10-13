def serialize_profile(user):
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "date_of_birth": user.date_of_birth,
        "address": user.address,
        "avatar_url": f"/{user.avatar_path}" if user.avatar_path else None,
        "avatar_thumbnail_url": f"/{user.avatar_thumbnail_path}" if user.avatar_thumbnail_path else None,
        "roles": [r.slug for r in user.roles],
    }
