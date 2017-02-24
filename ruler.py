
'''Rule over formal systems using lisp syntax
'''

import traceback

COMMENT_PREFIX     = ';'
PLACEHOLDER_PREFIX = ':'
DEFRULE_FORM       = 'defrule'

def padParens(s):
    return s.replace('(' , ' ( ').replace(')', ' ) ')

# TODO: Should I make s-expressions tuples so they're immutable?
def pyifyToken(token):
    if token == '(':
        return '['
    elif token == ')':
        return '],'
    else:
        return '"' + token.replace('"', r'\"') + '",'

class EmptyForm(Exception):
    pass

def read(s):
    """This is not quite a full parser, since it returns only compositions of
    str and list, but it's close to a parser. It doesn't know, for example,
    the difference between foo and :foo. It treats them as "foo" and ":foo",
    respectively. Identification of placeholders (like :foo) is done when
    a form is converted into a rule.
    """
    tokens = padParens(s).split()

    # Omit any comment, e.g. (this is (a form)) ; but not this part
    try:
        commentBegin = tokens.index(COMMENT_PREFIX)
        tokens = tokens[:commentBegin]
    except ValueError:
        pass

    if len(tokens) == 0:
        raise EmptyForm('There are no forms in this string: ' + s)

    pyExpression = ''.join(pyifyToken(token) for token in tokens)

    # Often there will be a tailing comma. Remove it.
    if pyExpression.endswith(','):
        pyExpression = pyExpression[:-1]

    form = eval(pyExpression)
    if type(form) not in (str, list):
        raise Exception('This string is not a form: ' + repr(s))

    return form

def form2str(form):
    t = type(form)

    if t is list:
        return '(' + ' '.join(form2str(f) for f in form) + ')'
    else:
        assert t is str, \
                str(form) + " is neither a list nor a str, but a " + str(t)
        return form

def regurgitate(s):
    return form2str(read(form))

class Placeholder:
    """Represents a placeholder in a rule pattern. Will compare equal to
    anything at first, but then will compare equal to other things only
    if they're equal to the first thing, until this `Placeholder` is
    `reset()`.
    """

    def __init__(self):
        self.reset()

    def __eq__(self, other):
        if self.mostRecentlyCompared is None:
            self.mostRecentlyCompared = other
            return True
        else:
            return self.mostRecentlyCompared == other

    def reset(self):
        # This will be trouble if we compare with `None`, but meh.
        self.mostRecentlyCompared = None

class Rule:
    """A form transformation rule: pattern -> replacement. The constructor
    takes a form (already pythonized) like:

        (defrule (... pattern ...) (... replacement ...)

    The constructor will parse `pattern` and `replacement`, creating instances
    of `Placeholder` where necessary. Then you can call the `apply()` method
    to see whether a given form matches this `Rule`, and if so what the form
    looks like after the substitution.
    """
    def __init__(self, form):
        if type(form) != list:
            raise Exception('Scalar form cannot define a rule: ' + str(form))
        if len(form) != 3:
            raise Exception('Rule must have 3 elements, not ' + str(len(form)))
       
        _, pattern, replacement = form
        
        self._shorthand = form2str(pattern) + ' -> ' + form2str(replacement)

        def buildPatternForm(fm):
            t = type(fm)
            if t is list:
                return [buildPatternForm(f) for f in fm]
            
            assert t is str
            if fm.startswith(PLACEHOLDER_PREFIX):
                name = fm[1:]
                if name not in self._placeholders:
                    placeholder = Placeholder()
                    self._placeholders[name] = placeholder
                else:
                    placeholder = self._placeholders[name]

                return placeholder
            else:
                return fm

        self._placeholders = dict()
        self._patternForm  = buildPatternForm(pattern)

        def buildReplacement(fm):
            t = type(fm)
            if t is list:
                return [buildReplacement(f) for f in fm]

            assert t is str
            if fm.startswith(PLACEHOLDER_PREFIX):
                name = fm[1:]
                return self._placeholders[name]
            else:
                return fm

        self._replacement = buildReplacement(replacement)

    def apply(self, form):
        """If the specified `form` matches this `Rule`, then return a
        transformed copy of `form`. Otherwise return `None`.
        """
        # Reset our placeholders (if we have any) so that in the comparison
        # that follows, a placeholder can enforce that multiple occurrences
        # of it must be the same to be considered a match.
        for placeholder in self._placeholders.values():
            placeholder.reset()

        # See if the form matches the pattern. If not, we're done.
        if form != self._patternForm:
            return None

        # The form matches, so now apply the transformation it describes.

        if type(self._replacement) is Placeholder:
            return self._replacement.mostRecentlyCompared
        elif type(self._replacement) is not list:
            return self._replacement
       
        # The replacement is a list. Make a copy of it, but replace the
        # placeholder(s) with whatever they matched on.
        # TODO Do I need to deep copy the stuff that the placeholders matched?
        def replace(fm):
            t = type(fm)
            if t is Placeholder:
                return fm.mostRecentlyCompared
            elif t is list:
                return [replace(f) for f in fm]
            else:
                assert t is str
                return fm

        return replace(self._replacement)

    def __repr__(self):
        return self._shorthand

class Matches:
    count = 0

def applyRules(form, rules):
    for rule in rules:
        applied = rule.apply(form)
        if applied is not None: # It matched
            Matches.count += 1
            return applyRules(applied, rules)

    # Now that we no longer match any rules, check the children
    # (if we have any).
    if type(form) is list:
        appliedChildren = [applyRules(f, rules) for f in form]
        if appliedChildren != form:
            return applyRules(appliedChildren, rules)
   
    return form

def evaluate(form, env):
    """Interpret the specified `form` in the specified `env` (environment).
    Return the resulting form. `env` might be modified.
    """
    if type(form) is list and form[0] == DEFRULE_FORM:
        rule = Rule(form)
        env['rules'].append(rule)
        print('There are', len(env['rules']), 'rules after adding', rule)
        return form

    return applyRules(form, env['rules'])

def repl():
    env = dict()
    env['rules'] = []
    while True:
        try:
            print(form2str(evaluate(read(input('ruler> ')), env)))
            print('That took', Matches.count, 'matches.')
            Matches.count = 0
        except EOFError:
            break
        except EmptyForm:
            pass
        except Exception:
            traceback.print_exc()
    
    print() # Leave the shell on a new line when we're done.

if __name__ == '__main__':
    repl()

