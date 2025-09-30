#include <stdio.h>
#include <unistd.h>
#include <termios.h>

int main() {
	struct termios old, new;
	tcgetattr(STDIN_FILENO, &old);
	new = old;
	new.c_lflag &= ~(ICANON | ECHO);
	tcsetattr(STDIN_FILENO, TCSANOW, &new);

	printf("\033[?25l");

	int x = 1, y = 1;
	int dx = 1, dy = 1;

	while (1) {
		printf("\033[%d;%dH*", y, x);
		fflush(stdout);
		usleep(100000);
		printf("\033[%d;%dH ", y, x);

		x += dx;
		y += dy;

		if (x <= 1 || x >= 80) dx = -dx;
		if (y <= 1 || y >= 24) dy = -dy;
	}
	
	printf("\033[?25h");
	tcsetattr(STDIN_FILENO, TCSANOW, &old);
	return 0;
}
