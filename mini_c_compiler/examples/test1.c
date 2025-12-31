int x = 5;
int y = 10;

int add(int a, int b) {
    return a + b;
}

int main() {
    int z = add(x, y);
    if (z > 10) {
        print(z);
    }
}
