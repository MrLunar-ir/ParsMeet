class State:
    def __init__(self, name, handler, next_state=None):
        self.name = name
        self.handler = handler
        self.next_state = next_state

class Conversation:
    def __init__(self, name):
        self.name = name
        self.states = {}
        self.entry = None

    def add_state(self, name, handler, next_state=None):
        state = State(name, handler, next_state)
        self.states[name] = state
        if self.entry is None:
            self.entry = name
        return self

    def set_entry(self, name):
        self.entry = name
        return self

class ConversationManager:
    def __init__(self):
        self.conversations = {}
        self.user_states = {}

    def register(self, conversation):
        self.conversations[conversation.name] = conversation

    def start(self, user_id, name, data=None):
        if name not in self.conversations:
            return False
        conv = self.conversations[name]
        self.user_states[user_id] = {"conv": name, "state": conv.entry, "data": data or {}}
        return True

    def is_active(self, user_id):
        return user_id in self.user_states

    def get_state(self, user_id):
        if user_id not in self.user_states:
            return None
        return self.user_states[user_id]["state"]

    def get_data(self, user_id):
        if user_id not in self.user_states:
            return {}
        return self.user_states[user_id]["data"]

    def stop(self, user_id):
        self.user_states.pop(user_id, None)

    def handle(self, user_id, data):
        if user_id not in self.user_states:
            return False
        info = self.user_states[user_id]
        conv = self.conversations[info["conv"]]
        current = conv.states[info["state"]]
        try:
            result = current.handler(data, info["data"])
        except Exception as e:
            print(f"FSM error: {e}")
            self.stop(user_id)
            return True
        if result is None or result is False:
            self.stop(user_id)
        elif result is True:
            pass
        elif isinstance(result, str):
            if result in conv.states:
                info["state"] = result
            else:
                self.stop(user_id)
        return True

def conversation(name):
    def decorator(func):
        func._is_conversation = True
        func._conversation_name = name
        return func
    return decorator

def state(name, next_state=None):
    def decorator(func):
        func._is_state = True
        func._state_name = name
        func._state_next = next_state
        return func
    return decorator