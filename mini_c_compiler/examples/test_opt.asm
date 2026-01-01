; -- Mini C Assembly --
JMP __init_globals
main:
; res = 35
PUSH 35
STORE res
; PRINT res
PUSH res
PRINT
RET

__init_globals:

CALL main
HALT