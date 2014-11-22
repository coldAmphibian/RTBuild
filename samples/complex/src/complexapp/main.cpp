#include <stdio.h>
#include "complexlib/complexlib.h"

int main(int argc, char **argv)
{
	printf("RTBuild Sample Application: Complex (" COMPLEX_PLATSTRING ")\n");

	printf("complex_add(1, 2) = %d\n", complex_add(1, 2));
	return 0;
}
