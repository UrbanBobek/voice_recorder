# Returns current settings in seting file
def read_settings_file():
    f = open("temp/settings.txt", "r")
    lines = f.readlines()
    res = []
    for line in lines:
        idx = line.find(":")
        res.append(line[idx+2:-1])
    f.close()
    
    return res