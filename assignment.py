
# que : 2

#TYPE DETECTIVE
    #Without running code, identify the type AND value:
#a = type(42) == int           # type = int , value = True
#b = 7 // 2                    # type = int , value = 3
#c = 7 / 2                     # type = float , value = 3.5
#d = bool(0) or bool(1)        # type = bool , value = True
#e = int(True) + int(False)    # type = int , value = 1
#f = "3" * 3                   # type = str , value = "333"
#g = not not not True          # type = bool , value = False
#h = 0 or "" or [] or "found"  # type = str , value = "found" or 1 or True
#i = 10 < 20 < 30 < 40         # type = bool , value = True


#Q3. VIBECHECK PROFILE
    #Create a complete player profile for yourself as a VibeCheck user.
    #Your profile must include:
    #- At least 2 variables of each type: int, float, str, bool
    #- At least one constant (SCREAMING_SNAKE_CASE)
    #- At least one type hint
    #- At least one f-string that combines 3+ variables with formatting
    #- Print the profile in a formatted table



#Q4. OPERATOR SURPRISE
    #Predict the output of each line, then verify your understanding:

print(0.1 + 0.2 == 0.3)                    # False
print(round(0.1 + 0.2, 10) == 0.3)         # True
print(True + True + False + True)           # 3
print(2 ** 3 ** 2)                          # 512 (careful!)
print(10 % 3 + 10 // 3)                     # 4
print("5" + str(5))                         # 55
print(int("10") + float("10"))              # 20.0
print(bool("False"))                        # True (careful!)
print(1_000 + 2_000_000)                    # 2001000
print(not (True and False) == (not True) or (not False))  # True

    #For any answer that surprised you: write one sentence explaining WHY.

#Q5. TYPE CONVERSION SAFETY
    #Write a function safe_to_int(value) that:
    #- Takes ANY value (str, float, bool, None, etc.)
    #- Attempts to convert it to int
    #- Returns the int if successful
    #- Returns None if conversion fails (don't let it crash!)
    #- Returns 0 for None input specifically
    #Test with: "42", "3.7", "hello", True, None, [], "  15  ", "0xFF"
#a = input("Enter a value: ")
print()
def safe_to_int(val):
    if val==None:
        return 0
    elif type(val)==int:
        return val
    elif type(val)==bool:
        return int(val)
    elif type(val)==float:
        return int(val)
    else:
        return None

value = safe_to_int("0xFF")
print(value)



#Q6. SCORE BREAKDOWN
    #A player's TOTAL score is 4783. Using only arithmetic operators
   # (no if/while/functions), compute and print:
    #- Their LEVEL (every 500 points = 1 level)
    #- Their XP toward next level
    #- Their score as a percentage of 5000 (max score), rounded to 1dp
    #- Whether their score is a perfect multiple of 100 (True/False)
    #- Their score formatted as a 6-digit zero-padded number ("004783")
    #- The hex representation of their score

score = 4783          
level = score // 500
xp_toward_next_level = score % 500
percentage_of_max = round((score / 5000) * 100, 1)
is_perfect_multiple_of_100 = (score % 100 == 0)
formatted_score = f"{score:06d}"
hex_representation = hex(score)
print(f"Level: {level}")
print(f"XP toward next level: {xp_toward_next_level}")
print(f"Score as percentage of max: {percentage_of_max}%")
print(f"Is perfect multiple of 100: {is_perfect_multiple_of_100}")
print(f"Formatted score: {formatted_score}")
print(f"Hex representation: {hex_representation}")