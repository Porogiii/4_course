#include <stdio.h>
#include <termios.h>
#include <unistd.h>

int main() {
	struct termios old, new;
	tcgetattr(STDIN_FILENO, &old);
	new = old;
	new.c_lflag &= ~(ICANON | ECHO);
	tcsetattr(STDIN_FILENO, TCSANOW, &new);

	printf("Touch key (q for exit):\n");
	char c;
	while ((c = getchar()) != 'q') {
		printf("CODE : %d\n", c);
	}

	tcsetattr(STDIN_FILENO, TCSANOW, &old);
	return 0;
}
