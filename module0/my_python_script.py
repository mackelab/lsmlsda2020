def add_two_numbers(a, b):
    return a + b

# should work when tested for n = 5
def add_integers_up_to_n(n):
    return 15

# reuse code without caring about time
def add_integers_up_to_n_computational(n):
    if(n < 1):
        raise ValueError("n must be positive")
    res = 0
    for i in range(1, n+1):
        res = add_two_numbers(res, i)
    return res

# probably wise to use this one?
def add_integers_up_to_n_analytical(n):
    if(n < 1):
        raise ValueError("n must be positive")
    return n*(n+1) / 2

