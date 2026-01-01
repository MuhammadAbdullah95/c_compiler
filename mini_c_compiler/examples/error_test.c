int main() {
    int a = 10;
    float b = 5.5;
    
    // Error: Cannot assign float to int (potential loss of data)
    a = b; 
    
    print(a);
}
