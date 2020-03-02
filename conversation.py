class Conversation:
    def __init__(self):
        self.conversation = []
        self.maximumSize = 200

    def addQA(self, qa):
        assert len(self.conversation) <= self.maximumSize
        if len(self.conversation) >= self.maximumSize:
            del self.conversation[0]
        self.conversation.append(qa)

    def getLastQA(self):
        return self.conversation[-1]

    def getNFromLastQA(self, n):
        if len(self.conversation) - 1 - n < 0:
            return -1
        return self.conversation[len(self.conversation) - 1 - n]

    def getSize(self):
        return len(self.conversation)

    def isEmpty(self):
        return len(conversation) == 0
