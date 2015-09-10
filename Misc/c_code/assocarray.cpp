#include <string>
#include <map>
#include <iostream>
using namespace std;
    
int main()
{
  map<string,int,less<string> >  age;   // age is a map from string to int
    
  age["Fred"] = 42;                     // Fred is 42 years old
  age["Barney"] = 37;                   // Barney is 37
  
  bool FredsBirthday = true;
    
  if ( FredsBirthday )           // On Fred's birthday,
    ++ age["Fred"];                     // increment Fred's age
  
  cout << "Barney is " << age["Barney"] << " years old\n";
  cout << "Fred is " << age["Fred"] << " years old\n";
  cout << "The combined age is " << age["Barney"] + age["Fred"] << " years old\n";
} 
