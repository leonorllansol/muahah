class ReferenceTA:

    def __init__(self, dialogId, trigger, answer):
        self.dialogId = dialogId
        self.trigger = trigger
        self.answer = answer

    def __repr__(self):
        return "ReferenceTA{" + "dialogId=" + dialogId + ", trigger='" + trigger + '\'' + ", answer='" + answer + '\'' + '}'