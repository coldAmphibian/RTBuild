[section .text]

; extern int __fastcall asmadd(int a, int b)

[global asmadd]
asmadd:
	mov eax, edx
	add eax, ecx
	ret
