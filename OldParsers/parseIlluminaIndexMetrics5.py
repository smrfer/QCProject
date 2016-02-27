def open_file_to_bytearray(filehandle,supported_version_number):
    values = bytearray()
    with open(filehandle, "rb") as f:
        for line in f:
            for b in line:
                values.append(b)
    return convert_bytes_index(values,supported_version_number)
    #return values


def convert_bytes_index(the_bytearray,supported_version_number):
    for index in xrange(len(the_bytearray)):
        byte_start = (index) #This will be where I will want to start the next readout from
        if index < 1:
            value = s.unpack_from(ENDIANNESS + "B",the_bytearray,index)
            if value[0] != supported_version_number:
                raise Exception("Unsupported file version")
        else:
            return get_chunk_len(byte_start,the_bytearray)


def get_varstr_info(readout_start,the_bytearray,offset=0):
    #Need readout_start because the first two bytes are the file version number
    #-set this to 0 for later iterations maybe depending on how implement
    ind_Y = 6
    ind_YV = 4
    #Define the length of the bytes storing the length information
    #Could maybe look at pulling it from the dictionary later?
    index_bytes_length = 2
    
    Y = s.unpack_from(ENDIANNESS + "H",the_bytearray[(offset+readout_start+ind_Y):(offset+readout_start+ind_Y+index_bytes_length)],0)
    ind_V = ind_Y + index_bytes_length + Y[0] + ind_YV
    V = s.unpack_from(ENDIANNESS + "H",the_bytearray[(offset+readout_start+ind_V):(offset+readout_start+ind_V+index_bytes_length)],0)
    ind_W = ind_V + index_bytes_length + V[0]
    W = s.unpack_from(ENDIANNESS + "H",the_bytearray[(offset+readout_start+ind_W):(offset+readout_start+ind_W+index_bytes_length)],0)
    #print (ind_W + index_bytes_length + W[0])
    return (Y[0],V[0],W[0],(ind_W + index_bytes_length + W[0])) #THIS IS KIND OF SHITTY BUT IT WORKS


def get_entry_len(readout_start,the_bytearray,offset=0):
    b_arr_len = get_varstr_info(readout_start,the_bytearray,offset) #NOTE THAT YOU MUSTN'T PUT offset=0 here
    return b_arr_len[3]

def get_Y(readout_start,the_bytearray,offset=0):
    Y = get_varstr_info(readout_start,the_bytearray,offset)
    #print Y[0]
    return Y[0]

def get_V(readout_start,the_bytearray,offset=0):
    V = get_varstr_info(readout_start,the_bytearray,offset)
    #print V[1]
    return V[1]

def get_W(readout_start,the_bytearray,offset=0):
    W = get_varstr_info(readout_start,the_bytearray,offset)
    #print W[2]
    return W[2] 
           

#This function also controls the program execution and could probably do with abstracting this out
def get_chunk_len(readout_start,the_bytearray):
    cumulative_chunks = 0
    values = []
    #First index starts at offset 0, so this has been pre-placed
    chunks = [0,]
    while cumulative_chunks < (len(the_bytearray)-1): #Run through the bytearray
        offset_for_summation = chunks[0:(len(chunks))]
        offset = sum(offset_for_summation)
        entry_length = get_entry_len(readout_start,the_bytearray,offset)
        chunks.append(entry_length)
        #Note actual length of record is 672 entries
        #Offset is the sum, bytearray is bytearray, chunk size is the most recent entry in the chunk array
        #(len(chunks)) is the number of chunks been through
        values.append(get_values((readout_start + offset),the_bytearray,chunks[(len(chunks))-1]))
        cumulative_chunks += entry_length
    #return readout_to_file(values) #Removed file readout part
    return values

#Probably need some work on abstracting this one out too
def get_values(byte_start,the_bytearray,chunk):
    array_segment = the_bytearray[byte_start:(byte_start+chunk)]
    Y = get_Y(byte_start,the_bytearray)
    V = get_V(byte_start,the_bytearray)
    W = get_W(byte_start,the_bytearray)
    encoding_constants = (Y,V,W)
    let = []
    count = 0
    arr_start = 0
    result = []
    for letter in ENCODING:
        if letter != 's':
            let.append(letter)
        elif letter == 's':
            print "arr_start is " + str(arr_start)
            #del let[len(let)-1] #Python is 0-indexed- remove the constant which has no meaning to unpack_from
            let.pop() #Pop from the stack (pop always pops from the end of a stack)
            encoding_string = "".join(let)
            enc_len = get_encoded_length(encoding_string)
            value = s.unpack_from(ENDIANNESS + encoding_string,array_segment[arr_start:(arr_start + enc_len)])
            for tup_ind in xrange(len(value)-1): #default will create a tuple with the entries in it. The -1 removes the entry that gives the length of the string from being appended.
                result.append(value[tup_ind])
            let = [] #Reinitialise the list
            let.append(letter*(encoding_constants[count]))
            encoding_string = "".join(let)
            value = s.unpack_from(ENDIANNESS + encoding_string,array_segment[(arr_start + enc_len):((encoding_constants[count]) + (arr_start + enc_len))])
            result.append("".join(value))
            arr_start = ((encoding_constants[count]) + (arr_start + enc_len))
            let = [] #Reinitialise the list
            count += 1 #Keeps track of which varstr was the last
    return result
    
def get_encoded_length(encoding_string):
    enc = []
    for encoder in encoding_string:
        enc.append(ENCODING_DICTIONARY.get(encoder,None))
    enc_len = sum(enc)
    return enc_len

#Removed file readout part
'''
def readout_to_file(list_of_data):
    fout = open("C:\Users\Sara\Desktop\Crap.txt", "w")
    for lst in list_of_data:
        #print lst
        for element in lst:
            fout.write(str(element) + "\t")
        fout.write("\n")
    #fout.write(list_of_data)
    fout.close()
    return "File write completed"
'''    

  
#Store file sizes in a dictionary
ENCODING_DICTIONARY={"x":1,"c":1,"b":1,"B":1,"?":1,"h":2,"H":2,"i":4,"I":4,"l":4,"L":4,"q":8,"Q":8,"f":4,"d":8,"s":1,"p":1,"P":1}

import struct as s
filename='C:\Users\Sara\Dropbox\Bioinformatics Clinical Science\OLAT rotations\Years Two-Three\SAVWork\PhiXRuns\\150818_M00766_0125_000000000-AE8BP\\InterOp\\IndexMetricsOut.bin'
#print parseIlluminaMetrics(fh,"<HHHf",'Lane\tTile\tCode\tValue\n',2)
ENDIANNESS = "<"
ENCODING = "HHHHYsIHVsHWs"
print open_file_to_bytearray(filename,1)