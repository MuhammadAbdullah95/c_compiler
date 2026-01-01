; -- Mini C Assembly --
JMP __init_globals
factorial:
; PARAM n
PARAM n
; result = 1
PUSH 1
STORE result
L1:
; t1 = n > 1
PUSH n
PUSH 1
GT
STORE t1
; IF_FALSE t1 GOTO L2
PUSH t1
JZ L2
; t2 = result * n
PUSH result
PUSH n
MUL
STORE t2
; result = t2
PUSH t2
STORE result
; t3 = n - 1
PUSH n
PUSH 1
SUB
STORE t3
; n = t3
PUSH t3
STORE n
; GOTO L1
JMP L1
L2:
; RETURN result
PUSH result
RET
RET

main:
; num = 5
PUSH 5
STORE num
; ARG num
; t4 = CALL factorial
PUSH num
CALL factorial
STORE t4
; fact = t4
PUSH t4
STORE fact
; PRINT fact
PUSH fact
PRINT
RET

__init_globals:

CALL main
HALT