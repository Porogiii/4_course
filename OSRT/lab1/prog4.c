#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>

void suicide(int sig)
{
    printf("\033[?25h\033[=0G\033[=7F\n");
    exit(0);
}

void error_suicide()
{
    printf("\033[?25h\033[=0G\033[=7F\n");
    exit(-1);
}

int main(int argc, char *argv[])
{
    signal(SIGINT, suicide);
    if(argc != 4){
        printf("Too few arguments");
        error_suicide();
    }
    int speed = atoi(argv[1]);
    int direction = atoi(argv[2]);
    int color = atoi(argv[3]);

    if(direction < 1 || direction > 4) {
        printf("Invalid direction");
        error_suicide();
    }
    if(color < 0 || color > 7) {
        printf("Invalid color");
        error_suicide();
    }
    if(speed < 1) {
        printf("Invalid speed");
        error_suicide();
    }

    int dx = 0, dy = 0;
    if(direction == 1)
        dy = -1;
    if(direction == 2)
        dx = -1;
    if(direction == 3)
        dy = 1;
    if(direction == 4)
        dx = 1;
    
    printf("\033[=%df\033[?25l", color);
    int x, y;
    for(x = 40, y = 15; ; x += dx, y += dy)
    {
        printf("\033[2J");
        printf("\033[%d;%dH", y, x);
        printf("(*^^*)^");
        fflush(stdout);
        usleep(speed);
        if(y+dy < 0 || y+dy > 42)
            y = y - 42 * dy;
        if(x+dx < 0 || x+dx > 80)
            x = x - 80 * dx;
    }
    return 0;
}
