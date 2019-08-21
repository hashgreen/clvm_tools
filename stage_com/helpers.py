from clvm import KEYWORD_TO_ATOM


CONS_KW = KEYWORD_TO_ATOM["c"]
QUOTE_KW = KEYWORD_TO_ATOM["q"]
EVAL_KW = KEYWORD_TO_ATOM["e"]
ARGS_KW = KEYWORD_TO_ATOM["a"]


def run(prog, macro_lookup):
    """
    PROG => (e (com (q PROG) (mac)) ARGS)

    The result can be evaluated with the stage_com eval_f
    function.
    """
    args = [ARGS_KW]
    mac = [QUOTE_KW, macro_lookup]
    return prog.to([
        EVAL_KW, [b"com", prog, mac], args])


def brun(prog, args):
    return prog.to([
        EVAL_KW, [QUOTE_KW, prog], [QUOTE_KW, args]])