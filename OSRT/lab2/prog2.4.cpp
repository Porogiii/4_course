#include <stdlib.h>
#include <unistd.h>
#include <vingraph.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <process.h>
#include <time.h>
#include <sys/mman.h>
#include <signal.h>

// Структура для разделяемой памяти
typedef struct {
    float a;      // радиус
    float b;      // форма
    float speed;  // скорость движения
    int trajectory_type; // тип траектории (0-круг, 1-эллипс, 2-розетка, 3-сердце)
} SharedData;

// тригонометрические функции
float my_cos(float x) {
    while (x < 0) x += 6.283185307f;
    while (x >= 6.283185307f) x -= 6.283185307f;
    
    float x2 = x * x;
    float x4 = x2 * x2;
    float x6 = x4 * x2;
    return 1.0f - x2/2.0f + x4/24.0f - x6/720.0f;
}

float my_sin(float x) {
    while (x < 0) x += 6.283185307f;
    while (x >= 6.283185307f) x -= 6.283185307f;
    
    float x2 = x * x;
    float x3 = x2 * x;
    float x5 = x3 * x2;
    float x7 = x5 * x2;
    return x - x3/6.0f + x5/120.0f - x7/5040.0f;
}

int main()
{
    ConnectGraph();
    int key = 0;
    pid_t proc1, proc2, proc3, proc4;
    float phi = 0.0f;

    // Разделяемая память для параметров траектории
    SharedData *shared = (SharedData*)mmap(0, sizeof(SharedData), 
                                         PROT_READ | PROT_WRITE, 
                                         MAP_SHARED | MAP_ANON, -1, 0);

    // Инициализация разделяемой памяти
    shared->a = 60.0f;
    shared->b = 40.0f;
    shared->speed = 0.02f;
    shared->trajectory_type = 0;

    // Фон
    Text(2, 2, "Движение по траектории - Управление: W,A,S,D,1,2,3,4,+,-");
    
    // отдельные процессы
    if((proc1 = fork()) == 0) {
        // Процесс 1: Анимированные эллипсы
        int el1 = Ellipse(150, 150, 80, 60);
        int el2 = Ellipse(350, 150, 70, 70);
        srand(time(0));
        while(1) {
            int c = RGB(rand() % 255, rand() % 255, rand() % 255);
            SetColor(el1, c);
            SetColor(el2, c);
            delay(200);
        }
    }

    if((proc2 = fork()) == 0) {
        // Процесс 2: Анимированные пиксели
        int pix1 = Pixel(200, 250);
        int pix2 = Pixel(220, 260);
        int pix3 = Pixel(240, 250);
        srand(time(0) + 1);
        while(1) {
            int c = RGB(rand() % 255, rand() % 255, rand() % 255);
            SetColor(pix1, c);
            SetColor(pix2, c);
            SetColor(pix3, c);
            delay(100);
        }
    }

    if((proc3 = fork()) == 0) {
        // Процесс 3: Анимированный треугольник
        tPoint tri_points[] = {{300, 250}, {250, 200}, {350, 200}};
        int tri = Polygon(tri_points, 3);
        srand(time(0) + 2);
        while(1) {
            int c = RGB(rand() % 255, rand() % 255, rand() % 255);
            SetColor(tri, c);
            delay(300);
        }
    }

    Rect(50, 50, 500, 350, 0, RGB(200, 200, 200));
    
    int *im_buf = (int*)malloc(60*60*4);
    for (int i = 0; i < 60; i++) {
        for(int j = 0; j < 60; j++) {
            int color_val = 0x0000FF + (i * 0x020000) - (j * 0x000100);
            im_buf[60*i + j] = color_val;
        }
    }
    Image32(400, 250, 60, 60, im_buf);

    tPoint line_points[] = {{250, 300}, {280, 320}, {310, 300}, {340, 320}, {370, 300}};
    Polyline(line_points, 5, RGB(255, 255, 255));

    // движущийся объект
    int moving_obj = Ellipse(0, 0, 15, 15, RGB(255, 0, 0)); // красный круг
    
    if((proc4 = fork()) == 0) {
        // Процесс 4: Движение по траектории
        while(1) {
            float x, y, rho;
            
            // координаты в зависимости от типа траектории
            switch(shared->trajectory_type) {
                case 0: // Круг
                    x = shared->a * my_cos(phi) + 300.0f;
                    y = shared->a * my_sin(phi) + 200.0f;
                    break;
                case 1: // Эллипс
                    x = shared->a * my_cos(phi) + 300.0f;
                    y = shared->b * my_sin(phi) + 200.0f;
                    break;
                case 2: // Розетка
                    rho = shared->a * my_cos(3.0f * phi) + shared->b;
                    x = rho * my_cos(phi) + 300.0f;
                    y = rho * my_sin(phi) + 200.0f;
                    break;
                case 3: // Сердце
                    x = 16.0f * my_sin(phi) * my_sin(phi) * my_sin(phi);
                    y = 13.0f * my_cos(phi) - 5.0f * my_cos(2.0f * phi) - 
                        2.0f * my_cos(3.0f * phi) - my_cos(4.0f * phi);
                    x = x * (shared->a / 16.0f) + 300.0f;
                    y = -y * (shared->b / 13.0f) + 200.0f; // инвертируем Y
                    break;
                default:
                    x = shared->a * my_cos(phi) + 300.0f;
                    y = shared->a * my_sin(phi) + 200.0f;
            }
            
            MoveTo((int)x, (int)y, moving_obj);
            phi += shared->speed;
            
            if (phi > 6.283185307f) {
                phi = 0.0f;
            }
            
            delay(15);
        }
    }

    while(key != 27) { // 27 - ESC
        key = InputChar();
        printf("Клавиша: %d\n", key);
        
        switch(key) {
            case 'w': case 'W':
                shared->a += 5.0f;
                if (shared->a > 100.0f) shared->a = 100.0f;
                break;
            case 's': case 'S':
                shared->a -= 5.0f;
                if (shared->a < 20.0f) shared->a = 20.0f;
                break;
            case 'a': case 'A':
                shared->b += 5.0f;
                if (shared->b > 80.0f) shared->b = 80.0f;
                break;
            case 'd': case 'D':
                shared->b -= 5.0f;
                if (shared->b < 10.0f) shared->b = 10.0f;
                break;
            case '+':
                shared->speed += 0.005f;
                if (shared->speed > 0.1f) shared->speed = 0.1f;
                break;
            case '-':
                shared->speed -= 0.005f;
                if (shared->speed < 0.005f) shared->speed = 0.005f;
                break;
            case '1':
                shared->trajectory_type = 0; // Круг
                break;
            case '2':
                shared->trajectory_type = 1; // Эллипс
                break;
            case '3':
                shared->trajectory_type = 2; // Розетка
                break;
            case '4':
                shared->trajectory_type = 3; // Сердце
                break;
        }
    }

    // Завершение всех процессов
    kill(proc1, SIGTERM);
    kill(proc2, SIGTERM);
    kill(proc3, SIGTERM);
    kill(proc4, SIGTERM);
    waitpid(proc1, NULL, 0);
    waitpid(proc2, NULL, 0);
    waitpid(proc3, NULL, 0);
    waitpid(proc4, NULL, 0);

    free(im_buf);
    munmap(shared, sizeof(SharedData));
    CloseGraph();
    return 0;
}