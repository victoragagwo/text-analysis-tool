from random_username.generate import generate_username

#Welcome User
def welcomeUser():
    print("Welcome to the text analysis tool, I will mine and analyze a body of text from a file you give me.")

#Get Username
def getUsername():
    #Print message prompting user to input their name
    usernameFromInput = input("\nTo begin, please enter your username:\n")

    #Check if username is valid
    if len(usernameFromInput) < 5 or not usernameFromInput.isidentifier() :
        print("Your username must be atleast 5 characters long, alphanumeric only (a-z/A-Z/0-9), have no spaces, and cannot start with a number.")
        print("Assigning username instead...")
        return generate_username()[0]
    
    return usernameFromInput

#Greet User
def greetUser(name):
    print("\nHello " + name)

def runProgram():
    welcomeUser()
    username = getUsername()
    greetUser(username)

runProgram()
