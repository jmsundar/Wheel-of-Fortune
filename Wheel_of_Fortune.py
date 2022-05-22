import sys
import json
import random
import time

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
VOWELS  = 'AEIOU'
VOWEL_COST  = 250

class WOFTeam:
    def __init__(self , name):
        self.name = name
        self.prizeMoney = 0
        self.prizes = []

    def addMoney( self, amt):
        self.prizeMoney += amt

    def goBankrupt(self):
        self.prizeMoney = 0

    def addPrize(self,prize):
        self.prizes.append(prize)

    def __str__(self):
        return "{} (${})".format(self.name,self.prizeMoney)

    def getMove(self,category, obscuredPhrase, guessed):
        print("{} has (${})".format(self.name,self.prizeMoney))

        print("Category:",category)
        print("Phrase:",obscuredPhrase)
        print("Guessed:",guessed)

        choice = str(input("Guess a letter, phrase, or type 'exit' or 'pass': "))
        return choice

# Repeatedly asks the user for a number between min & max (inclusive)
def getNumberBetween(prompt, min, max):
    userinp = input(prompt) # ask the first time

    while True:
        try:
            n = int(userinp) # try casting to an integer
            if n < min:
                errmessage = 'Must be at least {}'.format(min)
            elif n > max:
                errmessage = 'Must be at most {}'.format(max)
            else:
                return n
        except ValueError: # The user didn't enter a number
            errmessage = '{} is not a number.'.format(userinp)

        # If we haven't gotten a number yet, add the error message
        # and ask again
        userinp = input('{}\n{}'.format(errmessage, prompt))

# Spins the wheel of fortune wheel to give a random prize
# wheel.json format:
#   [
#       { "type": "cash", "text": "$950", "value": 950},
#       { "type": "cash", "text": "$500", "value": 500, "prize": "small prize"},
#       { "type": "cash", "text": "$5000", "value": 5000}
#   ]
def spinWheel():
    with open("wheel.json", 'r') as f:
        wheel = json.loads(f.read())
        return random.choice(wheel)

# Returns a category & phrase (as a tuple) to guess
# phrases.json format:
#   {
#       "Shlokas": ["Shloka1", "Shloka2"],
#       "Gods and Goddesses": ["Krishna", "Rama"]
#   }
def getRandomCategoryAndPhrase():
    with open("phrases.json", 'r') as f:
        phrases = json.loads(f.read())

        category = random.choice(list(phrases.keys()))
        phrase   = random.choice(phrases[category])
        return (category, phrase.upper())

# Given a phrase and a list of guessed letters, returns an obscured version
# Example:
#     guessed: ['L', 'B', 'E', 'R', 'N', 'P', 'K', 'X', 'Z']
#     phrase:  "GLACIER NATIONAL PARK"
#     returns> "_L___ER N____N_L P_RK"
def obscurePhrase(phrase, guessed):
    rv = ''
    for s in phrase:
        if (s in LETTERS) and (s not in guessed):
            rv = rv+'_'
        else:
            rv = rv+s
    return rv

# Returns a string representing the current state of the game
def showBoard(category, obscuredPhrase, guessed):
    return """
Category: {}
Phrase:   {}
Guessed:  {}""".format(category, obscuredPhrase, ', '.join(sorted(guessed)))

# GAME LOGIC CODE
print('='*15)
print('WHEEL OF FORTUNE - TEJOMAYAM')
print('='*15)
print('')

num_teams = getNumberBetween('How many teams?', 0, 10)

# Create the team instances
teams = WOFTeam(input('Enter the name for team #{}: '.format(i+1))) for i in range(num_teams)]

# No teams, no game :(
if len(teams) == 0:
    print('We need teams to play!')
    raise Exception('Not enough teams')

# category and phrase are strings.
category, phrase = getRandomCategoryAndPhrase()

# guessed is a list of the letters that have been guessed
guessed = []

# teamIndex keeps track of the index (0 to len(players)-1) of the player whose turn it is
teamIndex = 0

# will be set to the team instance when/if someone wins
winner = False

def requestTeamMove(team, category, guessed):
    while True: # we're going to keep asking the team for a move until they give a valid one
        time.sleep(0.1) # added so that any feedback is printed out before the next prompt

        move = team.getMove(category, obscurePhrase(phrase, guessed), guessed)
        move = move.upper() # convert whatever the player entered to UPPERCASE
        if move == 'EXIT' or move == 'PASS':
            return move
        elif len(move) == 1: # they guessed a character
            if move not in LETTERS: # the team entered an invalid letter (such as @, #, or $)
                print('Guesses should be letters. Try again.')
                continue
            elif move in guessed: # this letter has already been guessed
                print('{} has already been guessed. Try again.'.format(move))
                continue
            elif move in VOWELS and player.prizeMoney < VOWEL_COST: # if it's a vowel, we need to be sure the team has enough money for it
                    print('Need ${} to guess a vowel. Try again.'.format(VOWEL_COST))
                    continue
            else:
                return move
        else: # they guessed the phrase
            return move


while True:
    team = teams[teamIndex]
    wheelPrize = spinWheel()

    print('')
    print('-'*15)
    print(showBoard(category, obscurePhrase(phrase, guessed), guessed))
    print('')
    print('{} spins...'.format(team.name))
    time.sleep(2) # pause for dramatic effect!
    print('{}!'.format(wheelPrize['text']))
    time.sleep(1) # pause again for more dramatic effect!

    if wheelPrize['type'] == 'bankrupt':
        team.goBankrupt()
    elif wheelPrize['type'] == 'loseturn':
        pass # do nothing; just move on to the next team
    elif wheelPrize['type'] == 'cash':
        move = requestTeamMove(team, category, guessed)
        if move == 'EXIT': # leave the game
            print('Until next time!')
            break
        elif move == 'PASS': # will just move on to next team
            print('{} passes'.format(team.name))
        elif len(move) == 1: # they guessed a letter
            guessed.append(move)

            print('{} guesses "{}"'.format(team.name, move))

            if move in VOWELS:
                team.prizeMoney -= VOWEL_COST

            count = phrase.count(move) # returns an integer with how many times this letter appears
            if count > 0:
                if count == 1:
                    print("There is one {}".format(move))
                else:
                    print("There are {} {}'s".format(count, move))

                # Give them the money and the prizes
                team.addMoney(count * wheelPrize['value'])
                if 'prize' in wheelPrize:
                    team.addPrize(wheelPrize['prize'])

                # all of the letters have been guessed
                if obscurePhrase(phrase, guessed) == phrase:
                    winner = team
                    break

                continue # this team gets to go again

            elif count == 0:
                print("There is no {}".format(move))
        else: # they guessed the whole phrase
            if move == phrase: # they guessed the full phrase correctly
                winner = team

                # Give them the money and the prizes
                team.addMoney(wheelPrize['value'])
                if wheelPrize['prize']:
                    team.addPrize(wheelPrize['prize'])

                break
            else:
                print('{} was not the phrase'.format(move))

    # Move on to the next player (or go back to player[0] if we reached the end)
    teamIndex = (teamIndex + 1) % len(teams)

if winner:
    # In your head, you should hear this as being announced by a game show host
    print('{} wins! The phrase was {}'.format(winner.name, phrase))
    print('{} won ${}'.format(winner.name, winner.prizeMoney))
    if len(winner.prizes) > 0:
        print('{} also won:'.format(winner.name))
        for prize in winner.prizes:
            print('    - {}'.format(prize))
else:
    print('Nobody won. The phrase was {}'.format(phrase))
