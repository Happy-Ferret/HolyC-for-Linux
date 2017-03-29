class TokenStream(object):
    def __init__(self, input_):
        self.input = input_
        self.current = None
        self.keywords = 'if then else true false'.split(' ')

    def croak(self, message):
        return self.input.croak(message)

    def is_keyword(self, word):
        return word in self.keywords

    def is_digit(self, ch):
        try:
            int(ch)
            return True
        except (ValueError, TypeError):
            return False

    def is_id_start(self, ch):
        try:
            return ch.isalpha()
        except AttributeError:
            return False

    def is_id(self, ch):
        return self.is_id_start(ch) or ch in '?!-<>=0123456789'

    def is_op_char(self, ch):
        return ch in '+-*/%=&|<>!'

    def is_punc(self, ch):
        return ch in ',;(){}[]'

    def is_whitespace(self, ch):
        return ch in ' _\t_\n'.split('_')

    def read_while(self, predicate):
        string = str()
        while not self.input.eof() and predicate(self.input.peek()):
            string += self.input.next()
        return string

    def read_number(self):
        def anon(ch):
            if ch == '.':
                if (has_dot):
                    return False
                has_dot = True
                return True
            return self.is_digit(ch)
        has_dot = False
        number = self.read_while(anon)
        return {
            'type': 'num',
            'value': int(number)
        }

    def read_ident(self):
        id_ = self.read_while(self.is_id)
        return {
            'type': 'kw' if self.is_keyword(id_) else 'var',
            'value': id_
        }

    def read_escaped(self, end):
        escaped = False
        string = str()
        self.input.next()
        while not self.input.eof():
            ch = self.input.next()
            if escaped:
                string += ch
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == end:
                break
            else:
                string += ch
        return string

    def read_string(self):
        return {
            'type': 'str',
            'value': self.read_escaped('"')
        }

    def skip_comment(self):
        self.read_while(lambda ch: ch != "\n")
        self.input.next()

    def read_next(self):
        self.read_while(self.is_whitespace)
        if self.input.eof():
            return None
        ch = self.input.peek()
        if ch == "#":
            self.skip_comment()
            return self.read_next()
        if ch == '"':
            return self.read_string()
        if self.is_digit(ch):
            return self.read_number()
        if self.is_id_start(ch):
            return self.read_ident()
        if self.is_punc(ch):
            return {
                'type': 'punc',
                'value': self.input.next()
            }
        if self.is_op_char(ch):
            return {
                'type': 'op',
                'value': self.read_while(self.is_op_char)
            }
        self.input.croak(f'Can\'t handle character: {ch}')

    def peek(self):
        if self.current:
            return self.current
        self.current = self.read_next()
        return self.current

    def next(self):
        tok = self.current
        self.current = None
        return tok or self.read_next()

    def eof(self):
        return self.peek() is None