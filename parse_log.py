from parsing import Parser
from enum import Enum
def parse_typing_log1(log:str):
    parser = Parser()
    

    char_eq = lambda c1:(lambda str,i,j: c1==str[j])
    is_comma = char_eq(',')
    make_slice = lambda s,i,j:s[i:j]

    parser(log,is_comma,lambda s,i,j:None)
    lang = parser(log,is_comma,make_slice)
    if lang!= 'en': 
        return None
    
    some_num = parser(log,is_comma,make_slice)
    letter = log[parser.offset]
    parser.offset+=1
    

    letters = [letter]
    latencies = []
    not_num = lambda str,i,j: not str[j].isdigit() or (j== len(str)-1)
    until_num = lambda str,i,j: str[j].isdigit() or (j == len(str)-1)
    
    while parser.offset<len(log)-1:
        l = lambda s,i,j:(s[i:j],s[j])
        latency,letter = parser(log,not_num,l)
        if letter == '`' or letter == '~': 
            return None
        if letter == '\\':
            if log[parser.offset] == "b":
                letter = log[parser.offset+1]
                parser.offset+=2
            elif log[parser.offset] == "\"":
                letter = '\"'
                parser.offset+=1
            else:
                #invalid escape (idk if its possible)
                escaped = parser(log,until_num,make_slice) #get rid of it
                print('invalid escape')
                letter = ' ' #substitute with ' ' and ignore it

        if parser.offset<len(log)-1: # edge case: last number in the last latency is returned in letter
            letters.append(letter)
        else:
            latency = latency + letter
        
        try:
            latencies.append(int(latency))
        except Exception :
            print('latency parsing err ', latency )
            print(letter)
            print(log)
            print(letters)
            print(latencies)
            return None
    
    return letters,latencies

class press_type(Enum):
    Add_correct = 0
    Add_incorrect = 1
    Remove_correct = 2
    Remove_incorrect = 3


def parse_typing_log2(log:str,letters1):
    parser = Parser()
    make_slice = lambda s,i,j:s[i:j]
    letter1_position = 0
    letter2_position = 0
    was_last_number = False
    letters = []
    latencies = []
    operations = []
    mistakes = []
    keypresses = 0
    not_num = lambda str,i,j: not str[j].isdigit() or (j== len(str)-1)
    until_num = lambda str,i,j: str[j].isdigit() or (j == len(str)-1)
    is_separating_comma = lambda str,i,j:(j == len(str)-1) or (str[j] == ',' and str[j+1] != ',')
    
    while parser.offset<len(log)-1:

        latency = parser(log,not_num,make_slice)
        if log[parser.offset-1] ==',':
            if was_last_number:
                was_last_number = False  
                next_word_start_index = latencies.pop(len(latencies)-1)
                try:
                    keystrokes_to_type = int(latency)
                except Exception :
                    print('keystrokes_to_type parsing err ', latency )
                    print(letter)
                    print(log)
                    print(letters)
                    print(latencies)
                    return None
            else:
                was_last_number = True
                try:
                    latencies.append(int(latency))
                except Exception :
                    print('latency parsing err ', latency )
                    print(letter)
                    print(log)
                    print(letters)
                    print(latencies)
                    return None
        else:
            was_last_number = False
            keypresses +=1
            op = log[parser.offset-1]
            letter = parser(log,is_separating_comma,make_slice)
            if letter[0]== '\\':
                if letter[1] == "b":
                    letter = letter[2]
                else:
                    letter = letter[1]
            letters.append(letter)
            if op == '+':
                if letter1_position == letter2_position:
                    if letters1[letter1_position] == letter:
                        letter1_position+=1
                        letter2_position+=1
                    else:
                        mistakes.append(letter)
                        letter2_position+=1
        try:
            durations.append(int(latency))
        except Exception :
            print('latency parsing err ', latency )
            print(letter)
            print(log)
            print(letters)
            print(latencies)
            return None
        if op and op != '+' and op != '-':
            print('unk op', op)
       

        

        
    return letters,latencies,durations,mistakes
