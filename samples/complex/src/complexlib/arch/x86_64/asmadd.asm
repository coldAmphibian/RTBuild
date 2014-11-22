[section .text]

; extern int asmadd_win32(int a, int b)
; extern int asmadd_sysv(int a, int b)

[global asmadd_win32]
[global asmadd_sysv]

; You just HAD to be different, didn't you M$
asmadd_win32:
	mov rdi, rcx
	mov rsi, rdx
asmadd_sysv:
	mov rax, rdi
	add rax, rsi
	ret
