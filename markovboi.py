import sys
import random
import redis

class MarkovBoi():

    chain_length = 2
    end_word = '\x02'
    separator = '\x01'
    prefix = b'cozy'
    avg_length = 50
    all_user = '000000000000000000'

    def __init__(self):
        super(MarkovBoi, self).__init__()
        self.r = redis.Redis()

    def make_key(self, user, k):
        return b'-'.join((user, k))

    def parse_key(self, user, k):
        return k[len(user)+1:]

    def split_message(self, message):
        words = message.split()

        if len(words) > self.chain_length:
            words.append(self.end_word)
            for i in range(len(words) - self.chain_length):
                yield words[i:i + self.chain_length + 1]

    def gen_message(self, user, seed=None):
        if seed:
            try:
                key = self.parse_key(
                    user, 
                    random.sample(list(self.r.scan_iter(match=f'*0000-{seed}*')), 1)[0]
                )
            except:
                return '**error:** no messages for that seed :(('
        else:
            key = self.parse_key(user, self.r.srandmember(user + '-keys'))

        message = []
        
        for i in range(self.avg_length):
            # get the words from the key
            words = key.split(self.separator.encode())
            
            # add the word to final message
            message.append(words[0])

            # get next word based on last key
            next_word = self.r.srandmember(self.make_key(user.encode(), key))
            
            # these words are fresh :O
            if not next_word:
           	    break
            
            # create new key
            key = words[-1] + self.separator.encode() + next_word

        return b' '.join(message).decode()
        
    def parse_message(self, user, message):
        for words in self.split_message(message.lower()):
            key = self.separator.join(words[:-1])
            
            # add the message keys
            self.r.sadd(self.make_key(user.encode(), key.encode()), words[-1])
            self.r.sadd(self.make_key(self.all_user.encode(), key.encode()), words[-1])

            # add the keys to the collections of keys
            self.r.sadd(user + '-keys', self.make_key(user.encode(), key.encode()))
            self.r.sadd(self.all_user + '-keys', self.make_key(self.all_user.encode(), key.encode()))

if __name__ == '__main__':
    m = MarkovBoi()

    while True:
        m.parse_message("000000000000000000", input('> '))
        print(m.gen_message("000000000000000000"))
