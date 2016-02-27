def open_file_to_bytearray(filehandle,endianness,encoding,supported_version):
    values = bytearray()
    with open(filehandle, "rb") as f:
        for line in f:
            for b in line:
                values.append(b)
    return convert_bytes(values,endianness,encoding,supported_version)


def convert_bytes(the_bytearray,endianness,encoding,supported_version):
    results = []
    for index in xrange(len(the_bytearray)):
        byte_start = (index) #This will be where I will want to start the next readout from
        if index < 2:
            value = s.unpack_from("<B",the_bytearray,index)
            if (index == 0) and (value[0] != supported_version):
                raise Exception("Unsupported file version")
        else:
            break
    chunk = value[0]
    #print chunk
    #b_arr = the_bytearray[byte_start:chunk+byte_start]
    ##RECURSION HERE?
    for array_segment in xrange(byte_start,len(the_bytearray),chunk):
        b_arr = (the_bytearray[array_segment:(array_segment+chunk)])
        #print len(b_arr)
        start = 0
        for i in xrange(len(encoding)):
            enc = encoding[i]
            size = ENCODING_DICTIONARY.get(enc,None) #If want to be able to use e.g. 50I, could replace None here with a fucntion.
            enc_bytes = b_arr[start:(start+size)]
            #print enc_bytes
            start=(start+size)
            value = s.unpack(endianness+enc,enc_bytes)
            results.append(value) #This could be a 2D array with each record len(chunk)
    return results
    
#Store file sizes in a dictionary
ENCODING_DICTIONARY={"x":1,"c":1,"b":1,"B":1,"?":1,"h":2,"H":2,"i":4,"I":4,"l":4,"L":4,"q":8,"Q":8,"f":4,"d":8,"s":1,"p":1,"P":1}

import struct as s

filen='C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\OLAT rotations\Years Two-Three\SAVWork\PhiXRuns\\150818_M00766_0125_000000000-AE8BP\\InterOp\\QMetricsOut.bin'
enda= "<"
enca="HHHIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
print open_file_to_bytearray(filen,enda,enca,4)