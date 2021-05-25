from collections import defaultdict

class Feed:
    '''
    This is the parent class for individual exchanges
    '''
    def __init__(self):
        self.subscriptions = defaultdict(set) 