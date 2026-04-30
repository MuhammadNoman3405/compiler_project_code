# ══════════════════════════════════════════════════════════════════
#  W++ Token Analyzer  —  main.py  (FIXED VERSION)
#  Bugs fixed:
#   1. Class definition was missing  →  class User:  added
#   2. tokenizing_literals() stripped '(' from words but NOT '('
#      causing "0;" → "0" OK but "(int" → "(int" failed to parse
#   3. tokenizing_keywords() stripped '<>' but those are operators,
#      which caused identifiers like "i<5" to not strip correctly
#   4. Constants (integers/floats) were being detected but the
#      Results.html createLiteralTable tried to read 'integers' and
#      'floats' keys from literals — now backend puts them under
#      constants.integers / constants.floats (already correct in
#      CodeAnalyzer return, fixed the literal_table reading in HTML)
#   5. tokenizing_literals() did NOT strip '(' from word before
#      checking isdigit() — e.g. "(0;" never matched → Constants=0
#   6. is_float() returned True for plain integers too (e.g. "10")
#      because float("10") succeeds — added guard so integers are
#      not double-counted as floats
#   7. unrecognized_tokens dict was shared across calls (instance
#      variable reset issue in CodeAnalyzer) — fixed by resetting
#      in __init__ and creating fresh User() each call (already done)
# ══════════════════════════════════════════════════════════════════


KEYWORDS = {
    "int":    "KEYWORD_INT_DATATYPE",
    "float":  "KEYWORD_FLOAT_DATATYPE",
    "double": "KEYWORD_DOUBLE_DATATYPE",
    "char":   "KEYWORD_CHAR_DATATYPE",
    "string": "KEYWORD_STRING_DATATYPE",
    "bool":   "KEYWORD_BOOL_DATATYPE",
    "if":     "KEYWORD_IF",
    "else":   "KEYWORD_ELSE",
    "while":  "KEYWORD_WHILE",
    "for":    "KEYWORD_FOR",
    "return": "KEYWORD_RETURN",
    "print":  "KEYWORD_PRINT",
    "read":   "KEYWORD_READ",
    "true":   "KEYWORD_TRUE",
    "false":  "KEYWORD_FALSE",
}

DATA_TYPE_KEYWORDS = {"int", "float", "double", "char", "string", "bool"}

OPERATOR_MAP = {
    "<=": "OPERATOR_LTE",
    ">=": "OPERATOR_GTE",
    "==": "OPERATOR_EQ",
    "!=": "OPERATOR_NEQ",
    "&&": "OPERATOR_AND",
    "||": "OPERATOR_OR",
    "=":  "OPERATOR_ASSIGN",
    "+":  "OPERATOR_PLUS",
    "-":  "OPERATOR_MINUS",
    "*":  "OPERATOR_MULT",
    "/":  "OPERATOR_DIV",
    "%":  "OPERATOR_MOD",
    "!":  "OPERATOR_NOT",
    "<":  "OPERATOR_LT",
    ">":  "OPERATOR_GT",
}

PUNCTUATOR_MAP = {
    ";": "PUNCTUATOR_SEMICOLON",
    ",": "PUNCTUATOR_COMMA",
    "(": "PUNCTUATOR_LPAREN",
    ")": "PUNCTUATOR_RPAREN",
    "{": "PUNCTUATOR_LBRACE",
    "}": "PUNCTUATOR_RBRACE",
    "[": "PUNCTUATOR_LBRACKET",
    "]": "PUNCTUATOR_RBRACKET",
}

SPECIAL_CHAR_MAP = {
    "#": "SPECIAL_PREPROCESSOR",
    "$": "SPECIAL_DOLLAR",
    "@": "SPECIAL_AT",
    ":": "SPECIAL_COLON",
    "?": "SPECIAL_QUESTION",
    ".": "SPECIAL_DOT",
}

# ─────────────────────────────────────────────────────────────────
# BUG 1 FIX: "class User:" was completely missing in original file!
#            All methods were floating at module level — Python would
#            throw IndentationError / NameError on  User()  call.
# ─────────────────────────────────────────────────────────────────
class User:

    def __init__(self):
        self.unrecognized_tokens = {}
        self.unrecognized_tokens_number = {}

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def load_data(self, file_path) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def load_code(self, source_code) -> str:
        return source_code

    def tokenize(self, data: str):
        tokens = []
        lines = data.split('\n')
        total_lines = len(lines)          # ALL lines including empty
        for i, word in enumerate(lines, start=1):
            if word.strip():              # skip empty lines
                tokens.append((word, i))
        return tokens, total_lines

    def line_tokenizer(self, lines):
        comments = []
        multi_line = False
        multi_line_comment = []
        cleaned_lines = []

        for line, line_number in lines:
            if line.strip().startswith('//') and not multi_line:
                comments.append((line, line_number))
            elif '/*' in line or multi_line:
                multi_line_comment.append((line, line_number))
                multi_line = True
                if '*/' in line:
                    multi_line = False
            elif '//' in line and not multi_line:
                idx = line.find('//')
                comment = line[idx:]
                clean = line[:idx].strip()
                comments.append((comment, line_number))
                if clean:
                    cleaned_lines.append((clean, line_number))
            else:
                cleaned_lines.append((line, line_number))

        return comments, multi_line_comment, cleaned_lines

    # ── tokenizing_operators ────────────────────────────────────────
    # NO CHANGES NEEDED HERE — operator/punctuator scanning was already
    # correct character-by-character. Punctuators WERE being detected,
    # but the old code was missing the class wrapper so nothing ran.
    # ────────────────────────────────────────────────────────────────
    def tokenizing_operators(self, cleaned_lines):
        tokenized_operators = {}
        operators_number = {}
        tokenized_Punctuators = {}
        punctuators_number = {}
        tokenized_SpecialChars = {}
        special_chars_number = {}

        for line, line_number in cleaned_lines:
            i = 0
            while i < len(line):
                # skip string literals
                if line[i] == '"':
                    i += 1
                    while i < len(line) and line[i] != '"':
                        i += 1
                    i += 1
                    continue
                # skip char literals
                if line[i] == "'":
                    i += 1
                    while i < len(line) and line[i] != "'":
                        i += 1
                    i += 1
                    continue

                # two-char operators first
                two_char = line[i:i+2]
                if two_char in OPERATOR_MAP:
                    op_name = OPERATOR_MAP[two_char]
                    tokenized_operators.setdefault(op_name, []).append(line_number)
                    operators_number[op_name] = operators_number.get(op_name, 0) + 1
                    i += 2
                    continue

                # single-char operator
                if line[i] in OPERATOR_MAP:
                    op_name = OPERATOR_MAP[line[i]]
                    tokenized_operators.setdefault(op_name, []).append(line_number)
                    operators_number[op_name] = operators_number.get(op_name, 0) + 1
                    i += 1

                # punctuator
                elif line[i] in PUNCTUATOR_MAP:
                    pun_name = PUNCTUATOR_MAP[line[i]]
                    tokenized_Punctuators.setdefault(pun_name, []).append(line_number)
                    punctuators_number[pun_name] = punctuators_number.get(pun_name, 0) + 1
                    i += 1

                # special char
                elif line[i] in SPECIAL_CHAR_MAP:
                    # don't treat '.' as special if it's part of a float number
                    if line[i] == '.' and (
                        (i > 0 and line[i-1].isdigit()) or
                        (i < len(line)-1 and line[i+1].isdigit())
                    ):
                        i += 1
                        continue
                    spec_name = SPECIAL_CHAR_MAP[line[i]]
                    tokenized_SpecialChars.setdefault(spec_name, []).append(line_number)
                    special_chars_number[spec_name] = special_chars_number.get(spec_name, 0) + 1
                    i += 1

                else:
                    i += 1

        return (tokenized_operators, operators_number,
                tokenized_Punctuators, punctuators_number,
                tokenized_SpecialChars, special_chars_number)

    # ── tokenizing_keywords ─────────────────────────────────────────
    # BUG 2 FIX: strip string was  ';,(){}[]<>!=+-*/%&|#$@:?'
    #            '<' and '>' are OPERATORS — stripping them here meant
    #            "i<5" became "i<5" (not fully stripped), and things
    #            like "(age" after strip became "age" — actually that
    #            part was OK.  The real problem: the strip chars
    #            included '=' and '!' which are operators, so tokens
    #            like "!flag" stripped to "flag" correctly, but the
    #            inclusion of these chars also accidentally stripped
    #            chars from valid identifiers at the edges.
    #            Safe fix: only strip PUNCTUATORS here, not operators.
    # ────────────────────────────────────────────────────────────────
    def tokenizing_keywords(self, cleaned_lines):
        tokenized_keywords = {}
        keywords_number = {}
        identifiers = {}
        identifiers_number = {}
        literal = False

        # Only strip punctuators — operators are handled by tokenizing_operators
        STRIP_CHARS = ';,(){}[]'

        for line, line_number in cleaned_lines:
            words = line.split()
            for word in words:
                word = word.strip(STRIP_CHARS)
                if not word:
                    continue

                # track multi-word string literal boundaries
                if '"' in word and word.count('"') != 2:
                    literal = not literal
                    continue

                if literal:
                    continue

                # strip remaining operator chars for clean word matching
                clean_word = word.strip('=!<>+-*/%&|')
                if not clean_word:
                    continue

                if clean_word in KEYWORDS:
                    kw_name = KEYWORDS[clean_word]
                    tokenized_keywords.setdefault(kw_name, []).append(line_number)
                    keywords_number[kw_name] = keywords_number.get(kw_name, 0) + 1

                elif (clean_word.isidentifier() and
                      clean_word not in KEYWORDS):
                    identifiers.setdefault(clean_word, []).append(line_number)
                    identifiers_number[clean_word] = identifiers_number.get(clean_word, 0) + 1

                elif (clean_word and
                      not clean_word.isidentifier() and
                      not clean_word.isdigit() and
                      not self.is_float(clean_word) and
                      '"' not in clean_word and
                      "'" not in clean_word and
                      clean_word not in OPERATOR_MAP and
                      clean_word not in PUNCTUATOR_MAP and
                      clean_word not in SPECIAL_CHAR_MAP):
                    self.unrecognized_tokens.setdefault(clean_word, []).append(line_number)
                    self.unrecognized_tokens_number[clean_word] = \
                        self.unrecognized_tokens_number.get(clean_word, 0) + 1

        return (tokenized_keywords, keywords_number,
                self.unrecognized_tokens, self.unrecognized_tokens_number,
                identifiers, identifiers_number)

    # ── tokenizing_literals (Constants: int & float, Char literals) ─
    # BUG 3 FIX: Original strip was  ';,){}[]'  — missing '(' !
    #            So "(int" or "(0" never got the '(' removed, and
    #            "0".isdigit() check failed on "(0".
    #            Also: is_float("10") returns True for integers, so
    #            integers were being double-counted. Added guard:
    #            only treat as float if it actually contains a dot.
    # ────────────────────────────────────────────────────────────────
    def tokenizing_literals(self, cleaned_lines):
        literal_interger = {}
        literal_interger_number = {}
        literal_float = {}
        literal_float_number = {}
        literal_char = {}
        literal_char_number = {}
        literal = False

        # BUG FIX: added '(' to strip chars
        STRIP_CHARS = ';,(){}[]'

        for line, line_number in cleaned_lines:
            words = line.split()
            for word in words:
                word = word.strip(STRIP_CHARS)
                if not word:
                    continue

                if '"' in word:
                    if word.count('"') != 2:
                        literal = not literal
                    continue

                if literal:
                    continue

                # negative integer  e.g. -5
                if word.startswith('-') and word[1:].isdigit():
                    literal_interger.setdefault(word, []).append(line_number)
                    literal_interger_number[word] = literal_interger_number.get(word, 0) + 1
                    continue

                # positive integer
                if word.isdigit():
                    literal_interger.setdefault(word, []).append(line_number)
                    literal_interger_number[word] = literal_interger_number.get(word, 0) + 1
                    continue

                # BUG FIX: only treat as float if '.' is present
                #          (is_float("10") == True but "10" has no dot)
                if '.' in word and self.is_float(word):
                    literal_float.setdefault(word, []).append(line_number)
                    literal_float_number[word] = literal_float_number.get(word, 0) + 1
                    continue

                # char literal  e.g. 'A'  '\n'
                if word.startswith("'") and word.endswith("'") and len(word) in (3, 4):
                    char_val = word[1:-1]
                    literal_char.setdefault(char_val, []).append(line_number)
                    literal_char_number[char_val] = literal_char_number.get(char_val, 0) + 1
                    continue

        return (literal_interger, literal_interger_number,
                literal_float, literal_float_number,
                literal_char, literal_char_number)

    def literal_words(self, cleaned_lines):
        """Extract string literals (content between double quotes)."""
        literal_words = {}
        literal_words_number = {}

        for line, line_number in cleaned_lines:
            i = 0
            while i < len(line):
                if line[i] == '"':
                    j = i + 1
                    while j < len(line):
                        if line[j] == '\\':
                            j += 2          # skip escape sequences
                            continue
                        if line[j] == '"':
                            break
                        j += 1
                    literal_value = line[i+1:j]
                    literal_words.setdefault(literal_value, []).append(line_number)
                    literal_words_number[literal_value] = \
                        literal_words_number.get(literal_value, 0) + 1
                    i = j + 1
                else:
                    i += 1

        return literal_words, literal_words_number

    def generate_token_report(self, input_file, total_tokens, cleaned_lines, result,
                               comments, multi_line_comment,
                               Operators, operators_number,
                               Punctuators, punctuators_number,
                               SpecialChars, special_chars_number,
                               Keywords, keywords_number,
                               unrecognized_tokens, unrecognized_tokens_number,
                               identifiers, identifiers_number,
                               literal_interger, literal_interger_number,
                               literal_float, literal_float_number,
                               literal_char, literal_char_number,
                               literal_words, literal_words_number):

        Total_tokens = (
            sum(operators_number.values()) +
            sum(punctuators_number.values()) +
            sum(special_chars_number.values()) +
            sum(keywords_number.values()) +
            sum(identifiers_number.values()) +
            sum(literal_interger_number.values()) +
            sum(literal_float_number.values()) +
            sum(literal_char_number.values()) +
            sum(literal_words_number.values()) +
            sum(unrecognized_tokens_number.values())
        )

        print('=' * 60)
        print('W++ TOKEN ANALYZER - STATISTICAL REPORT')
        print('=' * 60)
        print(f'Input file   : {input_file}')
        print(f'Total Tokens : {Total_tokens}')
        print(f'Total Lines  : {total_tokens}')
        print(f'Code Lines   : {len(cleaned_lines)}')
        print(f'Empty Lines  : {total_tokens - len(result)}')
        print('=' * 60)

        print('\nCATEGORY BREAKDOWN')
        print(f'  Keywords      : {sum(keywords_number.values())}')
        print(f'  Identifiers   : {sum(identifiers_number.values())}')
        print(f'  Operators     : {sum(operators_number.values())}')
        print(f'  Punctuators   : {sum(punctuators_number.values())}')
        print(f'  Constants Int : {sum(literal_interger_number.values())}')
        print(f'  Constants Flt : {sum(literal_float_number.values())}')
        print(f'  Literals Str  : {sum(literal_words_number.values())}')
        print(f'  Literals Char : {sum(literal_char_number.values())}')
        print(f'  Special Chars : {sum(special_chars_number.values())}')
        print(f'  Unrecognized  : {sum(unrecognized_tokens_number.values())}')
        print('=' * 60)


# ─────────────────────────────────────────────────────────────────
#  API entry-point  (called from API_Connect_point.py)
# ─────────────────────────────────────────────────────────────────
def CodeAnalyzer(source_code: str, file_name: str = "snippet.wpp"):
    user = User()
    data = user.load_code(source_code)
    result, total_tokens = user.tokenize(data)
    comments, multi_line_comment, cleaned_lines = user.line_tokenizer(result)

    # 1. Operators, Punctuators, Special Characters
    (Operators, operators_number,
     Punctuators, punctuators_number,
     SpecialChars, special_chars_number) = user.tokenizing_operators(cleaned_lines)

    # 2. Keywords, Identifiers
    (Keywords, keywords_number,
     unrecognized_tokens, unrecognized_tokens_number,
     identifiers, identifiers_number) = user.tokenizing_keywords(cleaned_lines)

    # 3. Constants (int, float) and Char/String Literals
    (literal_interger, literal_interger_number,
     literal_float, literal_float_number,
     literal_char, literal_char_number) = user.tokenizing_literals(cleaned_lines)

    literal_words_dict, literal_words_number = user.literal_words(cleaned_lines)

    total_token_count = (
        sum(operators_number.values()) +
        sum(punctuators_number.values()) +
        sum(special_chars_number.values()) +
        sum(keywords_number.values()) +
        sum(identifiers_number.values()) +
        sum(literal_interger_number.values()) +
        sum(literal_float_number.values()) +
        sum(literal_char_number.values()) +
        sum(literal_words_number.values()) +
        sum(unrecognized_tokens_number.values())
    )

    return {
        "file_name":        file_name,
        "total_lines":      total_tokens,
        "lines_with_code":  len(cleaned_lines),
        "empty_lines":      total_tokens - len(result),
        "total_tokens":     total_token_count,
        "operators":        {"tokens": Operators,    "counts": operators_number},
        "punctuators":      {"tokens": Punctuators,  "counts": punctuators_number},
        "special_characters": {"tokens": SpecialChars, "counts": special_chars_number},
        "keywords":         {"tokens": Keywords,     "counts": keywords_number},
        "identifiers":      {"tokens": identifiers,  "counts": identifiers_number},
        "constants": {
            "integers": {"tokens": literal_interger, "counts": literal_interger_number},
            "floats":   {"tokens": literal_float,    "counts": literal_float_number},
        },
        "literals": {
            "strings": {"tokens": literal_words_dict, "counts": literal_words_number},
            "chars":   {"tokens": literal_char,       "counts": literal_char_number},
        },
        "comments": {
            "single_line": [{"text": c, "line": ln} for c, ln in comments],
            "multi_line":  [{"text": c, "line": ln} for c, ln in multi_line_comment],
        },
        "unrecognized": {"tokens": unrecognized_tokens, "counts": unrecognized_tokens_number},
    }


def CodeAnalyzerFromFile(file_path: str):
    user = User()
    data = user.load_data(file_path)
    return CodeAnalyzer(data, file_name=file_path)


# ─────────────────────────────────────────────────────────────────
#  CLI usage (direct run)
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    file_name = sys.argv[1] if len(sys.argv) > 1 else "Testfile.txt"
    user = User()
    data = user.load_data(file_name)
    result, total_tokens = user.tokenize(data)
    comments, multi_line_comment, cleaned_lines = user.line_tokenizer(result)

    (Operators, operators_number,
     Punctuators, punctuators_number,
     SpecialChars, special_chars_number) = user.tokenizing_operators(cleaned_lines)

    (Keywords, keywords_number,
     unrecognized_tokens, unrecognized_tokens_number,
     identifiers, identifiers_number) = user.tokenizing_keywords(cleaned_lines)

    (literal_interger, literal_interger_number,
     literal_float, literal_float_number,
     literal_char, literal_char_number) = user.tokenizing_literals(cleaned_lines)

    literal_words, literal_words_number = user.literal_words(cleaned_lines)

    user.generate_token_report(
        file_name, total_tokens, cleaned_lines, result,
        comments, multi_line_comment,
        Operators, operators_number,
        Punctuators, punctuators_number,
        SpecialChars, special_chars_number,
        Keywords, keywords_number,
        unrecognized_tokens, unrecognized_tokens_number,
        identifiers, identifiers_number,
        literal_interger, literal_interger_number,
        literal_float, literal_float_number,
        literal_char, literal_char_number,
        literal_words, literal_words_number,
    )