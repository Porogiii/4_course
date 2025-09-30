#include <stdlib.h>
#include <unistd.h>
#include <vingraph.h>

int main()
{
    ConnectGraph();
    Text(2, 2, "Абстрактная картинка");
    Rect(50, 50, 500, 350);
    
    Ellipse(150, 150, 80, 60);
    Ellipse(350, 150, 70, 70);

    Pixel(200, 250);
    Pixel(220, 260);
    Pixel(240, 250);

    tPoint triangle[] = {{300, 250}, {250, 200}, {350, 200}};
    Polygon(triangle, 3);

    int *im_buf = (int*)malloc(60*60*4);
    for (int i = 0; i < 60; i++) {
        for(int j = 0; j < 60; j++) {
            int color = 0x0000FF + (i * 0x020000) - (j * 0x000100);
            im_buf[60*i + j] = color;
        }
    }
    Image32(400, 250, 60, 60, im_buf);

    tPoint line[] = {{250, 300}, {280, 320}, {310, 300}, {340, 320}, {370, 300}};
    Polyline(line, 5);

    sleep(100);
    CloseGraph();
    return 0;
}