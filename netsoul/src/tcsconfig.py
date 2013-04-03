####
####
#### Tcapsoul Configuration File
####
####

TCAPSOUL_CONFIG_FILE='/etc/tcapsoul/tcapsoul.conf'

def     openConfigFile(op, file = TCAPSOUL_CONFIG_FILE):
    fd = open(TCAPSOUL_CONFIG_FILE, op)
    return (fd)

def     getConfigFile(file = TCAPSOUL_CONFIG_FILE):
    fd = openConfigFile('r', file)
    lines = fd.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.replace('\n', '')
    fd.close()
    return (lines)
    
def     putConfigFile(tabs, file = TCAPSOUL_CONFIG_FILE):
    fd = openConfigFile('wc', file)
    fd.write('\n'.join(tabs))
    fd.close()

def     update(newConfigFile):
    return (0)

def     saveBuddyList(l, file = TCAPSOUL_CONFIG_FILE):
    lines = getConfigFile()
    for i, line in enumerate(lines):
        if (line.find('buddys') != -1):
            break
    old = line[8:].replace(']', '').replace(' ', '').replace('\n', '').split(',')
    for bud in l:
        bud = "'%s'" % bud
        try:
            if (old.index(bud) != -1):
                continue
        except ValueError:
            old.append(bud)
    lines[i] = "buddys=[" + ', '.join(old) + ']\n'
    putConfigFile(lines, file)
