#include <stdio.h>
#include <fstream>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <termios.h>

int set_interface_attribs (int fd, int speed, int parity)
{
        struct termios tty;
        if (tcgetattr (fd, &tty) != 0)
        {
                printf("error %d from tcgetattr", errno);
                return -1;
        }

        cfsetospeed (&tty, speed);
        cfsetispeed (&tty, speed);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;     // 8-bit chars
        // disable IGNBRK for mismatched speed tests; otherwise receive break
        // as \000 chars
        tty.c_iflag &= ~IGNBRK;         // disable break processing
        tty.c_lflag = 0;                // no signaling chars, no echo,
                                        // no canonical processing
        tty.c_oflag = 0;                // no remapping, no delays
        tty.c_cc[VMIN]  = 0;            // read doesn't block
        tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

        tty.c_iflag &= ~(IXON | IXOFF | IXANY); // shut off xon/xoff ctrl

        tty.c_cflag |= (CLOCAL | CREAD);// ignore modem controls,
                                        // enable reading
        tty.c_cflag &= ~(PARENB | PARODD);      // shut off parity
        tty.c_cflag |= parity;
        tty.c_cflag &= ~CSTOPB;
        tty.c_cflag &= ~CRTSCTS;

        if (tcsetattr (fd, TCSANOW, &tty) != 0)
        {
                printf("error %d from tcsetattr", errno);
                return -1;
        }
        return 0;
}

void set_blocking (int fd, int should_block)
{
        struct termios tty;
        memset (&tty, 0, sizeof tty);
        if (tcgetattr (fd, &tty) != 0)
        {
                printf ("error %d from tggetattr", errno);
                return;
        }

        tty.c_cc[VMIN]  = should_block ? 1 : 0;
        tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

        if (tcsetattr (fd, TCSANOW, &tty) != 0)
                printf ("error %d setting term attributes", errno);
}




int main(int argc, char** argv)
{
    if(argc < 2)
        exit(1);

    std::string devStr = argv[1];
int fd = open (devStr.c_str(), O_RDWR | O_NOCTTY | O_SYNC);
if (fd < 0)
{
        printf ("error %d opening %s: %s", errno, devStr.c_str(), strerror (errno));
        return 1;
}

set_interface_attribs (fd, B9600, 0);  // set speed to 115,200 bps, 8n1 (no parity)
set_blocking (fd, 0);                // set no blocking

//write (fd, "hello!\n", 7);           // send 7 character greeting

usleep ((7 + 25) * 100);             // sleep enough to transmit the 7 plus
                                     // receive 25:  approx 100 uS per char transmit
//char buf [100];
//int n = read (fd, buf, sizeof buf);  // read up to 100 characters if ready to read

   // FILE* f = fopen(devStr.c_str(), "r");
   // if(!f) {
   //     printf("no file\n");
   //     exit(1);
   // }
    while(true) {
        printf(".");
        fflush(stdout);

        int next = 200;

        char* buf = new char[next + 1];
        memset(buf, 0, next +1);
        size_t n_read = read(fd, buf, next);

        if(n_read > 0) {
            //for(int i = 0; i < n_read; i++) {
            //    printf("%d ", buf[i]);
            //}
            //printf("\n");
            printf("N %d\n%s", n_read, buf);
        }

        delete[] buf;
        usleep(100*1000);
    }
    //fclose(f);
    printf("EXIT\n");
    exit(0);

    std::ifstream dev(devStr.c_str());
    if(!dev) {
        printf("Device not good!\n");
        exit(1);
    }
    std::string line;
    printf("Device open. Starting read.\n");
    while(dev.good()) {
        std::streamsize next = dev.rdbuf()->in_avail();
        printf(".");
        fflush(stdout);

        if(next <= 0)
            continue;

        char c;
        dev >> c;
        printf("C %c\n", c);

//         printf("N %ld\n", next);
//         char buf[2];
//         buf[1] = '\0';
//         dev.readsome(buf, 1);
// 
// //
// //
// //        char* buf = new char[next + 1];
// //        dev.read(buf, next);
// //        buf[next] = '\0';
// //
//         printf("C '%s'\n", buf);
// //        delete[] buf;
        usleep(100*1000);
    }
    //while(std::getline(dev, line)) {
    //    printf("%s\n", line.c_str());
    //}

    dev.close();

    return 0;
}
