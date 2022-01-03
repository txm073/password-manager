#include <iostream>
#include <vector>
#include <utility>
#include <cmath>

using namespace std;

vector<int> sieve(int n)
{
    vector<int> nums = {}, marker = {}, primes = {};
    for(int i = 2; i < n; ++i){
        nums.push_back(i);
        marker.push_back(0);
    }
    for(int index = 0; index < nums.size(); ++index){
        int number = nums[index];
        if(marker[index] == 0){
            primes.push_back(number);            
            for(int j = index + number; j < nums.size(); j += number){
                marker[j] = 1;
            }
        }
    }
    return primes;
}

bool contains(vector<int> vec, int i)
{
    for(int j : vec){
        if(j == i){
            return true;
        }
    }
    return false;
}

pair<int, int> getLargePrimes(int lower, int upper)
{
    int prime1, prime2;
    vector<int> sqrtPrimes = sieve((int)sqrt(upper)), numsTried = {};
    while(true){
        
    }
    return pair<int, int>(prime1, prime2);
}

int main(int argc, char* argv[])
{
    vector<int> primes = sieve(100);
    for(int i : primes) cout << i << endl;
}