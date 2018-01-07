game = input('Which game is it on? Please send an int.')
outcomes = input('Write a list of "A"s and "D"s to indicate who won each game.')

for char in outcomes:
    if char not in 'AD':
        print('Please send a valid string.')

if len(outcomes) != game:
    print('That is an invalid string or game.')

a = 0
d = 0
for char in outcomes:
    if char == 'D':
        d += 1
    elif char == 'A':
        a += 1

print(f'Adon won {a} games and Kyle won {d} games.')
