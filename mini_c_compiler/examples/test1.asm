; -- Mini C Assembly --
JMP __init_globals
add:
; PARAM a
PARAM a
; PARAM b
PARAM b
; t1 = a + b
PUSH a
PUSH b
ADD
STORE t1
; RETURN t1
PUSH t1
RET
RET

main:
; ARG x
; ARG y
; t2 = CALL add
PUSH y
PUSH x
CALL add
STORE t2
; z = t2
PUSH t2
STORE z
; t3 = z > 10
PUSH z
PUSH 10
GT
STORE t3
; IF_FALSE t3 GOTO L1
PUSH t3
JZ L1
; PRINT z
PUSH z
PRINT
; GOTO L2
JMP L2
L1:
L2:
RET

__init_globals:
; x = 5
PUSH 5
STORE x
; y = 10
PUSH 10
STORE y
CALL main
HALT