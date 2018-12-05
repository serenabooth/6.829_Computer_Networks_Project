with open('bgp_12_3.csv') as fp:
    ct = 0 
    line = fp.readline()

    while ct < 10:
        ct += 1 

        delimiter_positions = ( [pos for pos, char in enumerate(line) if char == "|"])
        try: 
            as_identifier = "AS" + str(line[delimiter_positions[4]+1:delimiter_positions[5]])
            print as_identifier
            bgp_address = str(line[delimiter_positions[5]+1:delimiter_positions[6]])
            print bgp_address
        except:
            pass
        print delimiter_positions
        print line

        line = fp.readline()
