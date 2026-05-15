# helpers/vc_manager.py
from pyrogram.enums import ChatType
from pytgcalls.exceptions import NoActiveGroupCall

active_calls = {}  # {chat_id: file_path}
current_volume = {}  # {chat_id: volume}

async def join_voice_chat(call, app, chat_input):
    """Voice chat join karega (ID ya username se)"""
    try:
        # Convert username to ID if needed
        if isinstance(chat_input, str) and not chat_input.startswith("-"):
            chat = await app.get_chat(chat_input)
            chat_id = chat.id
        else:
            chat_id = int(chat_input)
        
        # Join
        await call.join_group_call(chat_id, stream_type=0)
        active_calls[chat_id] = None
        current_volume[chat_id] = 500
        
        return chat_id, True, None
    except NoActiveGroupCall:
        return None, False, "Voice chat active nahi hai!"
    except Exception as e:
        return None, False, str(e)

async def leave_voice_chat(call, chat_id: int):
    """Voice chat leave karega"""
    if chat_id in active_calls:
        await call.leave_group_call(chat_id)
        del active_calls[chat_id]
        if chat_id in current_volume:
            del current_volume[chat_id]
        return True
    return False
