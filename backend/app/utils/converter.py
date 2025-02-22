def convert_object_id_to_string(obj):
    """
    Convert MongoDB ObjectId to string.

    Args:
        obj (dict): Object containing ObjectId

    Returns:
        dict: Object with ObjectId converted to string
    """
    if "_id" in obj:
        obj["_id"] = str(obj["_id"])
    return obj
