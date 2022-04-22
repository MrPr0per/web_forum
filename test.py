import random

letters = 'qwertyuiopasdfghjklzxcvbnm1234567890'
n_block = 4
len_block = 4
key = '-'.join(''.join(random.choice(letters) for i in range(len_block)) for j in range(n_block))
print(key)
