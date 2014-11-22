[section .text]

; extern int __fastcall asmadd(int a, int b)

[global $@asmadd@8]
$@asmadd@8:
	mov eax, edx
	add eax, ecx
	ret
