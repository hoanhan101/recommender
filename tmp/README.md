# tmp

## Observation

### Problem: Find the top 10 recommendations for userID 10.

I run the program 3 times.

Because I only test for user 10, the top 10 movies are fixed:
```
- Usual Suspects, The (1995)
- There's Something About Mary (1998)
- Hairspray (1988)
- 13th Warrior, The (1999)
- Runaway Train (1985)
- Sweet Hereafter, The (1997)
- My Own Private Idaho (1991)
- Matrix, The (1999)
- Sling Blade (1996)
- Hearts and Minds (1996)
```

For the nearest neighbours technique, all of them have the same output, which
is what I expected.
```
- Seven (a.k.a. Se7en) (1995)
- Apollo 13 (1995)
- Pulp Fiction (1994)
- Forrest Gump (1994)
- Trainspotting (1996)
- Clockwork Orange, A (1971)
- Saving Private Ryan (1998)
- American History X (1998)
- American Beauty (1999)
- Amores Perros (Love's a Bitch) (2000)
```

However, the results from latent factor technique's are different. They
share some similarities but not all.

Output 1:
```
- Toy Story (1995)
- Jumanji (1995)
- American President, The (1995)
- Casino (1995)
- Get Shorty (1995)
- Twelve Monkeys (a.k.a. 12 Monkeys) (1995)
- Seven (a.k.a. Se7en) (1995)
- Usual Suspects, The (1995)
- Mr. Holland's Opus (1995)
- Friday (1995)
```

Output 2:
```
Using latent factor technique, we found:
- Toy Story (1995)
- Father of the Bride Part II (1995)
- Heat (1995)
- GoldenEye (1995)
- Casino (1995)
- Twelve Monkeys (a.k.a. 12 Monkeys) (1995)
- Clueless (1995)
- Seven (a.k.a. Se7en) (1995)
- Usual Suspects, The (1995)
- Mr. Holland's Opus (1995)
```

Output 3:
```
Using latent factor technique, we found:
- Toy Story (1995)
- Heat (1995)
- Casino (1995)
- Get Shorty (1995)
- Twelve Monkeys (a.k.a. 12 Monkeys) (1995)
- Clueless (1995)
- To Die For (1995)
- Seven (a.k.a. Se7en) (1995)
- Usual Suspects, The (1995)
- Mr. Holland's Opus (1995)
```

I am not sure why *Toy Story (1995)* is occurred 3 times in the beginning of the
list. Is it because of the list is unsorted/sorted? What about the logic of the
algorithm? Is it supposed to do so?

> *Assumption:* Because I run it 3 times separately, it calculates the matrix
> factorization 3 times and produces different result for each time. If I run
> it once and reuse the result, then I should have the same set of
> recommendations for the same user.

*Mr. Holland's Opus (1995)* appears 2 time near the end. Is it a coincidence?
I don't know yet.

*Seven (1995)* is the only collision (comparing 2 techniques) in 3 outputs.
```
Here are the same items that occured in both techniques:
- Seven (a.k.a. Se7en) (1995)
```

## Done
- Change top_recommendations to top_favotires
- Refactor steps in matrix factorization
- Use threading to execute tasks in parallel to serve resutls quicker
- Timestamp for each step

## TODO
- Figure out the reason numpy blocks
  > Maybe it doesn't block. Maybe the locking causes the problem.
- Calculate matrix factorization once and save the return values to reuse
  during a session, since it's super expensive.
- Does the difficulty increase after x number of steps?
- Does the computer slow down after some number of computations and how to
  tell?
- What is the processing of training data? Is it always true that the more
  training the better?
