from itertools import count


EPSILON = 'ε'


class Automaton:
    _id_counter = count()

    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.transitions = {}
        self.start = None
        self.accept = set()

    @classmethod
    def new_state(cls):
        return next(cls._id_counter)

    def add_state(self, state, accept=False):
        self.states.add(state)
        if accept:
            self.accept.add(state)

    def add_transition(self, src, symbol, dst):
        if symbol != EPSILON:
            self.alphabet.add(symbol)
        self.states.add(src)
        self.states.add(dst)
        self.transitions.setdefault((src, symbol), set()).add(dst)

    def move(self, state, symbol):
        return self.transitions.get((state, symbol), set())

    def epsilon_closure(self, states):
        stack = list(states)
        closure = set(states)
        while stack:
            s = stack.pop()
            for t in self.move(s, EPSILON):
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
        return closure

    def __repr__(self):
        return (
            f'Automaton(states={len(self.states)}, '
            f'alphabet={sorted(self.alphabet)}, start={self.start}, '
            f'accept={self.accept})'
        )


OPERATORS = {'|', '.', '*', '+', '?'}
UNARY_POSTFIX = {'*', '+', '?'}
PRECEDENCE = {'|': 1, '.': 2, '*': 3, '+': 3, '?': 3}
LEFT_ASSOC = {'|': True, '.': True, '*': True, '+': True, '?': True}

def tokenize(regex):
    tokens = []
    i = 0
    n = len(regex)
    while i < n:
        c = regex[i]
        if c == '\\':
            if i + 1 >= n:
                raise ValueError("Carácter de escape '\\' al final de la expresión regular")
            tokens.append(('LITERAL', regex[i + 1]))
            i += 2
            continue
        if c == '(':
            tokens.append(('LPAREN', c))
        elif c == ')':
            tokens.append(('RPAREN', c))
        elif c in OPERATORS:
            tokens.append(('OP', c))
        elif c == ' ':
            i += 1
            continue
        else:
            tokens.append(('LITERAL', c))
        i += 1
    return tokens

def _is_operand_end(token):
    kind, val = token
    return kind == 'LITERAL' or kind == 'RPAREN' or (kind == 'OP' and val in UNARY_POSTFIX)

def _is_operand_start(token):
    kind, val = token
    return kind == 'LITERAL' or kind == 'LPAREN'

def insert_concat_operators(tokens):
    result = []
    for idx, tok in enumerate(tokens):
        if result and _is_operand_end(result[-1]) and _is_operand_start(tok):
            result.append(('OP', '.'))
        result.append(tok)
    return result

def to_postfix(regex):
    tokens = tokenize(regex)
    tokens = insert_concat_operators(tokens)
    output = []
    op_stack = []
    for kind, val in tokens:
        if kind == 'LITERAL':
            output.append(('LITERAL', val))
        elif kind == 'LPAREN':
            op_stack.append((kind, val))
        elif kind == 'RPAREN':
            while op_stack and op_stack[-1][0] != 'LPAREN':
                output.append(op_stack.pop())
            if not op_stack:
                raise ValueError("Paréntesis desbalanceados: falta un '(' ")
            op_stack.pop()
        elif kind == 'OP':
            while (
                op_stack
                and op_stack[-1][0] == 'OP'
                and (
                    PRECEDENCE[op_stack[-1][1]] > PRECEDENCE[val]
                    or (
                        PRECEDENCE[op_stack[-1][1]] == PRECEDENCE[val]
                        and LEFT_ASSOC[val]
                    )
                )
            ):
                output.append(op_stack.pop())
            op_stack.append((kind, val))
    while op_stack:
        top = op_stack.pop()
        if top[0] in ('LPAREN', 'RPAREN'):
            raise ValueError("Paréntesis desbalanceados: falta un ')' ")
        output.append(top)
    return output

def _literal_fragment(symbol):
    nfa = Automaton()
    s0 = Automaton.new_state()
    s1 = Automaton.new_state()
    nfa.add_state(s0)
    nfa.add_state(s1, accept=True)
    nfa.add_transition(s0, symbol, s1)
    nfa.start = s0
    nfa.accept = {s1}
    return nfa

def _union(a, b):
    nfa = Automaton()
    s0 = Automaton.new_state()
    s1 = Automaton.new_state()
    nfa.states = a.states | b.states | {s0, s1}
    nfa.alphabet = a.alphabet | b.alphabet
    nfa.transitions = _merge_transitions(a.transitions, b.transitions)
    nfa.add_transition(s0, EPSILON, a.start)
    nfa.add_transition(s0, EPSILON, b.start)
    for acc in a.accept:
        nfa.add_transition(acc, EPSILON, s1)
    for acc in b.accept:
        nfa.add_transition(acc, EPSILON, s1)
    nfa.add_state(s1, accept=True)
    nfa.start = s0
    nfa.accept = {s1}
    return nfa

def _concat(a, b):
    nfa = Automaton()
    nfa.states = a.states | b.states
    nfa.alphabet = a.alphabet | b.alphabet
    nfa.transitions = _merge_transitions(a.transitions, b.transitions)
    for acc in a.accept:
        nfa.add_transition(acc, EPSILON, b.start)
    nfa.start = a.start
    nfa.accept = set(b.accept)
    return nfa

def _star(a):
    nfa = Automaton()
    s0 = Automaton.new_state()
    s1 = Automaton.new_state()
    nfa.states = a.states | {s0, s1}
    nfa.alphabet = set(a.alphabet)
    nfa.transitions = dict(a.transitions)
    nfa.add_transition(s0, EPSILON, a.start)
    nfa.add_transition(s0, EPSILON, s1)
    for acc in a.accept:
        nfa.add_transition(acc, EPSILON, a.start)
        nfa.add_transition(acc, EPSILON, s1)
    nfa.add_state(s1, accept=True)
    nfa.start = s0
    nfa.accept = {s1}
    return nfa

def _plus(a):
    return _concat(a, _star(_clone(a)))

def _optional(a):
    return _union(a, _literal_fragment(EPSILON))

def _clone(a):
    mapping = {s: Automaton.new_state() for s in a.states}
    nfa = Automaton()
    nfa.alphabet = set(a.alphabet)
    for (src, sym), dsts in a.transitions.items():
        for dst in dsts:
            nfa.add_transition(mapping[src], sym, mapping[dst])
    nfa.states = set(mapping.values())
    nfa.start = mapping[a.start]
    nfa.accept = {mapping[s] for s in a.accept}
    return nfa

def _merge_transitions(t1, t2):
    merged = {}
    for d in (t1, t2):
        for key, dsts in d.items():
            merged.setdefault(key, set()).update(dsts)
    return merged

def build_nfa_from_postfix(postfix_tokens):
    stack = []
    for kind, val in postfix_tokens:
        if kind == 'LITERAL':
            stack.append(_literal_fragment(val))
        elif kind == 'OP':
            if val == '|':
                b = stack.pop()
                a = stack.pop()
                stack.append(_union(a, b))
            elif val == '.':
                b = stack.pop()
                a = stack.pop()
                stack.append(_concat(a, b))
            elif val == '*':
                a = stack.pop()
                stack.append(_star(a))
            elif val == '+':
                a = stack.pop()
                stack.append(_plus(a))
            elif val == '?':
                a = stack.pop()
                stack.append(_optional(a))
            else:
                raise ValueError(f'Operador desconocido: {val}')
        else:
            raise ValueError(f'Token desconocido: {kind}')
    if len(stack) != 1:
        raise ValueError('Expresión regular mal formada (verifique operandos/operadores)')
    return stack.pop()

def regex_to_nfa(regex):
    postfix = to_postfix(regex)
    return build_nfa_from_postfix(postfix)

def simulate_nfa(nfa, w):
    current = nfa.epsilon_closure({nfa.start})
    steps = [current]
    for symbol in w:
        next_states = set()
        for s in current:
            next_states |= nfa.move(s, symbol)
        current = nfa.epsilon_closure(next_states)
        steps.append(current)
        if not current:
            break
    accepted = bool(current & nfa.accept)
    return (accepted, steps)
