async def get_file_type(ext : str) :
    custom_types = {
        'txt': 'text/plain',
        'pdf': 'application/pdf',
        'mp3': 'audio/mpeg',
        'mp4': 'video/mp4',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }
    
    if ext not in custom_types :
        return False
    
    return custom_types[ext]