from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

def add_history_model(messages_list: list, chat_history: object, key: str) -> None:
    messages = []
    for message in messages_list:
        match message["role"]:
            case "user":
                messages.append(HumanMessage(content=message["message"]))
            case "model":
                messages.append(AIMessage(content=message["message"]))
    chat_history(key=key).add_messages(messages)
    

def format_messages_to_db(history: object) -> list:
    messages_list = []
    for msg in history.messages:
        match msg.type:
            case "human":
                messages_list.append({
                    "role": "user",
                    "message": msg.content
                })
            case "ai":
                messages_list.append({
                    "role": "model",
                    "message": msg.content
                })
    return messages_list


def send_messages_to_db(supabase: object, chat_name: str, chat_messages:object) -> None:
    if supabase.table("chat_history").select("chat_name").eq("chat_name", chat_name).execute().data:
        supabase.table("chat_history").update({"chat_messages": format_messages_to_db(chat_messages)}).eq("chat_name", chat_name).execute()
    else:
        supabase.table("chat_history").insert({"chat_name": chat_name, "chat_messages": format_messages_to_db(chat_messages)}).execute()