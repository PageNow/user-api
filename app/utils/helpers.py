def convert_to_user_info_public(user_info):
    user_info = dict(user_info)
    if not user_info['dob_public']:
        user_info['dob'] = None
    if not user_info['gender_public']:
        user_info['gender'] = None
    if not user_info['school_public']:
        user_info['school'] = None
    if not user_info['work_public']:
        user_info['work'] = None
    if not user_info['location_public']:
        user_info['location'] = None
    return user_info
