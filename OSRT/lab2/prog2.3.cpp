#include <stdlib.h>
#include <unistd.h>
#include <vingraph.h>
#include <stdio.h>
#include <sys/types.h>
#include <process.h>
#include <time.h>

int main()
{
    ConnectGraph();
    Text(2, 2, "Абстрактная картинка с анимацией");

    // фигуры
    int rect = Rect(50, 50, 500, 350);
    int elip1 = Ellipse(150, 150, 80, 60);
    int elip2 = Ellipse(350, 150, 70, 70);
    int pix1 = Pixel(200, 250);
    int pix2 = Pixel(220, 260);
    int pix3 = Pixel(240, 250);

    tPoint triangle_points[] = {{300, 250}, {250, 200}, {350, 200}};
    int polyg = Polygon(triangle_points, 3);

    int *im_buf = (int*)malloc(60*60*4);
    for (int i = 0; i < 60; i++) {
        for(int j = 0; j < 60; j++) {
            int color = 0x0000FF + (i * 0x020000) - (j * 0x000100);
            im_buf[60*i + j] = color;
        }
    }
    int img = Image32(400, 250, 60, 60, im_buf);

    tPoint line_points[] = {{250, 300}, {280, 320}, {310, 300}, {340, 320}, {370, 300}};
    int poly1 = Polyline(line_points, 5);

    pid_t proc1, proc2, proc3, proc4;

    int a = getpid();
    printf("\ncurrent process = %d", a);

    if((proc1 = fork()) != 0)
    {
        int b = getpid();
        printf("\ncurrent process 1 = %d", b);
        if((proc2 = fork()) != 0)
        {
            int c = getpid();
            printf("\ncurrent process 2 = %d", c);
            if((proc3 = fork()) != 0)
            {
                int d = getpid();
                printf("\ncurrent process 3 = %d", d);
                if((proc4 = fork()) != 0)
                {
                    int e = getpid();
                    printf("\ncurrent process 4 = %d\n", e);
                    InputChar();
                    CloseGraph();
                }
                else
                {
                    // Процесс 4: двигает изображение и ломаную линию
                    srand(time(0));
                    while(1)
                    {
                        int x = (rand() % 3) - 1;
                        int y = (rand() % 3) - 1;
                        Move(img, x, y);
                        
                        x = (rand() % 3) - 1;
                        y = (rand() % 3) - 1;
                        Move(poly1, x, y);
                        delay(400);
                    }
                }
            }
            else
            {
                // Процесс 3: двигает прямоугольник и полигон
                srand(time(0));
                while(1)
                {
                    int c = RGB(rand() % 255, rand() % 255, rand() % 255);
                    int lr = (rand() % 60) - 30;
                    int x = (rand() % 3) - 1;
                    int y = (rand() % 3) - 1;
                    Move(rect, x, y);
                    SetColor(rect, c);
                    Enlarge(rect, lr, lr);
                    
                    x = (rand() % 3) - 1;
                    y = (rand() % 3) - 1;
                    Move(polyg, x, y);
                    SetColor(polyg, c);
                    delay(300);
                }
            }
        }
        else
        {
            // Процесс 2: двигает эллипсы
            srand(time(0));
            while(1)
            {
                int c = RGB(rand() % 255, rand() % 255, rand() % 255);
                int x = (rand() % 3) - 1;
                int y = (rand() % 3) - 1;
                Move(elip1, x, y);
                SetColor(elip1, c);
                
                x = (rand() % 3) - 1;
                y = (rand() % 3) - 1;
                Move(elip2, x, y);
                SetColor(elip2, c);
                delay(200);
            }
        }
    }
    else
    {
        // Процесс 1: двигает пиксели
        srand(time(0));
        while(1)
        {
            int c = RGB(rand() % 255, rand() % 255, rand() % 255);
            int x = (rand() % 3) - 1;
            int y = (rand() % 3) - 1;
            Move(pix1, x, y);
            SetColor(pix1, c);
            
            x = (rand() % 3) - 1;
            y = (rand() % 3) - 1;
            Move(pix2, x, y);
            SetColor(pix2, c);
            
            x = (rand() % 3) - 1;
            y = (rand() % 3) - 1;
            Move(pix3, x, y);
            SetColor(pix3, c);
            delay(100);
        }
    }

    free(im_buf);
    return 0;
}