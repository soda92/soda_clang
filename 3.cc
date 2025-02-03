#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main()
{
    vector<string> s = {"Hello", "world"};
    for (auto i : s)
    {
        cout << i << ' ';
    }
    cout << endl;
}