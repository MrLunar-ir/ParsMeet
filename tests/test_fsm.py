from ParsMeet.fsm import Conversation, ConversationManager

def test_conversation_registration():
    mgr = ConversationManager()
    conv = Conversation("signup")
    conv.add_state("ask_name", lambda d, c: "ask_age", "ask_age")
    conv.add_state("ask_age", lambda d, c: None)
    mgr.register(conv)
    assert "signup" in mgr.conversations

def test_start_conversation():
    mgr = ConversationManager()
    conv = Conversation("test")
    conv.add_state("step1", lambda d, c: None)
    mgr.register(conv)
    assert mgr.start("user1", "test") is True
    assert mgr.is_active("user1") is True

def test_stop_conversation():
    mgr = ConversationManager()
    conv = Conversation("test")
    conv.add_state("step1", lambda d, c: None)
    mgr.register(conv)
    mgr.start("user1", "test")
    mgr.stop("user1")
    assert mgr.is_active("user1") is False