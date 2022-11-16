from parsing import Parser
from enum import IntEnum


def parse_typing_log1(log:str):
    parser = Parser(log)
    

    pred_and_ret = lambda pred,ret: lambda s,i,j:ret(s,i,j) if pred(s,i,j) else None
    make_slice = lambda s,i,j:s[i:j]

    chr_eq = lambda ch: (lambda s,i,j:ch==s[j])
    not_num = lambda str,i,j: not str[j].isdigit() or (j== len(str)-1) 
    until_num = lambda str,i,j: str[j].isdigit() or (j == len(str)-1)

    slice_on_comma = pred_and_ret(chr_eq(','),make_slice)
    single = pred_and_ret(lambda s,i,j: True,lambda s,i,j: s[j])

    parser(slice_on_comma)
    lang = parser(slice_on_comma)
    if lang!= 'en': 
        return None
    
    init_latency = int(parser(slice_on_comma))
    letter = parser(single)
    

    letters = [letter]
    latencies = [init_latency]
    
    while parser.offset<len(log)-1:
        next_letter_next_freq = pred_and_ret(not_num,lambda s,i,j:(s[i:j],s[j]))
        latency,letter = parser(next_letter_next_freq)
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

class press_type(IntEnum):
    Add_correct = 0
    Add_mistake = 1
    Remove_correct = 2
    Remove_mistake = 3


def parse_typing_log2(log:str,letters1):
    parser = Parser(log)
    letters1_i = 0
    letters = []
    latencies = []
    operations = []
    durations = []
    all_multi_comps = []
    op_chars = []
    mistakes = []
    all_keypresses = 0
    mistakes_to_delete = 0
    has_been_mistake = False

    def parse_composite(s,i,j):
        if s[j] == ',' and ((s[j-1] != '+' and s[j-1] != '-')or((s[j-2] == '+' or (s[j-2] == '-')) and ((s[j-1] == '+' or (s[j-1] == '-'))))):
            rets = []
            slic = s[i:j]
            if '\"' in slic:
                print()
            slc_s = 0
            slc_e = 0
            while slc_e<len(slic)-1:
                while slc_e < len(slic) and slic[slc_s:slc_e+1].isdecimal():
                    slc_e+=1
                dur = slic[slc_s:slc_e]
                op = slic[slc_e]
                if op != '+' and op != '-':
                    print('unk op', op,slic)
                    return [(42,op,'q')]
                slc_e+=1
                chr = slic[slc_e]
                if chr == '\\':
                    slc_e+=1
                    chr = slic[slc_e]
                slc_e+=1
                rets.append((dur,op,chr))
                if len(chr)>1:
                    print()
                slc_s = slc_e
            if len(rets) > 1:
                print()
            return rets
            # if len(slic.split('+'))>2:
            #     slic.find('+')
            #     print()
            # if len(slic.split('+-'))>2:
            #     print()
            # if slic.find('+')>0 and slic.find('-')>0:
            #     print()
            # op_i = slic.find('+')
            # if op_i == -1 or op_i == len(slic)-1: # not found or the '+' is at the end as the letter 
            #     op_i = slic.find('-')
            # dur,op,chr = int(slic[:op_i]),slic[op_i],slic[-1]
            # if len(chr)>1:
            #     print()
            #return (dur,op,chr)
            
    def parse_num(s,i,j):
        if s[j] == ',':
            return int(s[i:j])

    while parser.offset<len(log)-1:
        #if mistakes_to_delete > 0: #seems like typeracer can sometimes have reversed letters(even tho they are correct order in log1)
            #return None
        word_start_i = parser(parse_num)
        letters1_i = word_start_i
        keystrokes = parser(parse_num)
        all_keypresses += keystrokes
        for letter_i in range(keystrokes):
            latency = parser(parse_num)
            latencies.append(latency)
            comps =  parser(parse_composite)
            first_comp = True
            if len(comps)>1 and all([comp[1]=='-' for comp in comps]):  #typeracer replay bug: ctrl+bsp has inverse deletion order
                comps.reverse()
            if len(comps)>1:
                all_multi_comps.append(comps)
            for comp in comps:
                if not first_comp:
                    latencies.append(0)
                first_comp = False

                duration,op,chr =  comp
                if op != '+' and op != '-':
                    return None

                if letters1_i == len(letters1):
                    return None #extra letter after text ?!?
                l_i = letters1_i
                if op == '+':
                    if chr == letters1[letters1_i] and mistakes_to_delete == 0:
                        letters1_i +=1
                        operations.append(press_type.Add_correct)
                        mistakes.append(has_been_mistake)
                        has_been_mistake = False
                    else:
                        operations.append(press_type.Add_mistake)
                        mistakes_to_delete += 1
                        has_been_mistake = True
                else:
                    if mistakes_to_delete > 0:
                        operations.append(press_type.Remove_mistake)
                        mistakes_to_delete-=1
                    else:
                        operations.append(press_type.Remove_correct)
                        letters1_i -=1
                        mistakes.pop(len(mistakes)-1)
                op_chars.append((op+chr,operations[-1],chr,letters1[l_i],chr == letters1[l_i]))

                
                durations.append(duration)
                letters.append(chr)
            

    if len(operations) != len(latencies) or len(operations) != len(letters):
        print('dif op and kp len', len(operations),all_keypresses)
    if mistakes_to_delete > 0: #throw away this result as not to poison the data
        return None
        
    return letters,latencies,durations,operations,mistakes
