"""
Created on fri Nov 1 2024

@author: Samuel McCarthy-Potter
"""

'''
This code function is to find variable regions in a fasta file. 
This function will take in a single dna sequence in fasta format and return the begging site and end site in a variable region. 

input - .txt .fasta 
a single sequnce fasta file 

output - list of list of sites 
the begning and end site of each varable region 

'''

from argparse import ArgumentParser
from re import findall
from sys import argv,stderr

class FastaSequenceError(Exception):
    pass

class VariableSites(Exception):
    pass

class InstallError(Exception):
    pass

def init_argparse():
    #Sets up the command line arguments

    parser = ArgumentParser(description ='This program creates a list of the amino acid groups found from specified variability sites')
    
    parser.add_argument('fasta', type=str, help='Path to the fasta file:\n', default='input.fasta')
    parser.add_argument('fastq', type=str, help='Path to the fastq file:\n', default='fastq.fastq')

    parser.add_argument('-o', '--output', type=str, help='Path to the output file: \tdefault="output"\n', default='output')
    parser.add_argument('-p', '--phread', type=int, help='threshold value to filliter phread score: \tdefault=20\n', default=20)
    parser.add_argument('-5', '--five_prime', type=int, help='distance from variability sites to the 5 prime end of the required match: \tdefault=8\n', default=8)
    parser.add_argument('-3', '--three_prime', type=int, help='distance from variability sites to the 3 prime end of the required match: \tdefault=8\n', default=8)
    parser.add_argument('-v', '--variable', type=int, help='number of variable sites: \tdefault=2\n', default=2)
    if len(argv)==1:
        parser.print_help(stderr)
        
    return parser


def fasta_to_single_line_string(input_fasta,is_file = True):
    #Converts fasta file to a single line string

    if is_file:
        with open(input_fasta,"r") as open_fasta_file:

            line_list = list(open_fasta_file)

            open_fasta_file.close()
    else:
        line_list = input_fasta.split("\n")

    fasta_sequence = ''

    for line in line_list:
        strip_line = line.strip()
        if strip_line [0] == ">":
            if len(fasta_sequence) > 0:
                raise FastaSequenceError('There are more then one Sequences in this file')
        elif strip_line .isalpha():
            fasta_sequence += strip_line.upper() 
        else:
            raise FastaSequenceError(f"Unknown character in input fasta {line}")

    return fasta_sequence

def translate_codon(codon):
    #Takes in a string and maps it to a amino acid in the dictionary 

    genetic_code = {
        'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
        'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
        'TAT': 'Y', 'TAC': 'Y', 'TAA': '.', 'TAG': '.',
        'TGT': 'C', 'TGC': 'C', 'TGA': '.', 'TGG': 'W',
        'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
        'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
        'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
        'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
        'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
        'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
        'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
        'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
        'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
        'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
        'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
        'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
    }
    return genetic_code.get(codon.upper(), '-')

def reverse_complement(nucleotide):
    #Reverses nucleotides to their complements

    reverse_complement = []
    y = '-'
    for x in nucleotide:
        if str(x).upper() == "A":
            y = "T"
        if str(x).upper() == "T":
            y = "A"
        if str(x).upper() == "C":
            y = "G"
        if str(x).upper() == "G":
            y = "C"

        reverse_complement.append(y)

    reverse_complement.reverse()
    return(reverse_complement)

def reverse_complement_nucleotide(nucleotide_list):
    #Reverses the nucleotide sequences 

    reverse_nucleotide_list = []

    for item in nucleotide_list:
        if len(item) > 1:
            nucleotide_list = (''.join(reverse_complement(item[1])),''.join(reverse_complement(item[0])))
            reverse_nucleotide_list.append(nucleotide_list)
    
    return reverse_nucleotide_list



def reverse_complement_region_marker(region_marker_list):
    #Reverses the region marker sequences 

    reverse_complement_region_marker_list = []

    for item in region_marker_list:
        reverse_region_marker = (''.join(reverse_complement(item[1])),''.join(reverse_complement(item[0])),item[-1])
        reverse_complement_region_marker_list.append(reverse_region_marker)

    reverse_complement_region_marker_list.reverse()

    return reverse_complement_region_marker_list

def find_variable_sites(fasta_sequence,variable_sites_number = 2):
    """
    input - .txt .fasta 
    a single sequnce fasta file 

    output - list of list of sites 
    all sites of each varable region 
    """

    #returns a list of all continuous regions with nonstandard nucleotides

    list_non_standard_nucleotide_region = []

    non_standard_nucleotide_site = False

    for index,site in enumerate(fasta_sequence):
        if site in ["A","T","C","G"]:
            non_standard_nucleotide_site = False
        else:
            if non_standard_nucleotide_site:
                list_non_standard_nucleotide_region[-1].append(index)
            else:
                list_non_standard_nucleotide_region.append([index])
                non_standard_nucleotide_site = True

    if len(list_non_standard_nucleotide_region) != variable_sites_number:
        raise VariableSites(f'Variable Sites requested {variable_sites_number} not equal to Variable Sites found {len(list_non_standard_nucleotide_region)}')
 
    return list_non_standard_nucleotide_region

Default_distance_from_region = 8

def find_guide_sequences(fasta_sequence,list_non_standard_nucleotide_region,distance_5_prime = Default_distance_from_region,distance_3_prime = Default_distance_from_region):
    #Find guide sequences

    region_marker_list = []

    for region in list_non_standard_nucleotide_region:
        five_prime = fasta_sequence[(region[0] - (distance_5_prime )):region[0]]
        three_prime = fasta_sequence[(region[-1] +1 ):(region[-1] + distance_3_prime+1)]
        length_region = len(region)
        region_marker = (five_prime,three_prime,length_region)
        region_marker_list.append(region_marker)

    return region_marker_list

def find_codon_list(region_marker_list,fasta_line_list):
    #Find guide sequences

    codon_list = []
    for fasta_line in fasta_line_list:
        sub_codon_list = []
        for region_marker in region_marker_list:
            variable_region = "." * region_marker[-1]
            search_template = f"{region_marker[0] + variable_region + region_marker[1]}"

            look_for = findall(search_template ,fasta_line)
            if len(look_for) > 0:
                sub_codon_list.append(look_for[0][len(region_marker[0]):-len(region_marker[1])])
        codon_list.append(sub_codon_list)

    return codon_list

def get_fastq_sequence_list(in_put_fastq,is_file = True):
    #Preprocess fastq file into individual list of sequences

    sequence_list  = []
    if is_file:
        with open(in_put_fastq, 'r') as file:
            file_list = list(file)
            file.close()
    else:
        file_list = list(in_put_fastq.split("\n"))

    for site,line in enumerate(file_list):
        line = line.strip()
        if site % 4 == 0:
            sequence_list.append([])
            sequence_list[-1].append(line)
        else:
            sequence_list[-1].append(line)

    if sequence_list[-1] == ['']:
        sequence_list.pop()

    return sequence_list

def fastq_to_fasta_sequence(sequence_list,phread_score = 10):
    #Converts the each fastq sequence into a fasta sequence based on phread score 

    list_fasta_sequence = []

    for sequence in sequence_list:
        fasta_string = list(sequence[1])
        for site,char in enumerate(sequence[-1]):
            if ord(char) < 21 + phread_score:
                fasta_string[site] = "-"
        list_fasta_sequence.append([">" + str(sequence[0][1:]),''.join(fasta_string)])

    return list_fasta_sequence 

def convert_codons_to_amino_acid_list(codon_list,variable_sites_number):
    #This transforms the codon list to a list of amino acids

    amino_acid_list = []

    for codons in codon_list:
        if len(codons) == variable_sites_number:
            amino_pair = []

            for codon in codons:
                amino_pair.append(translate_codon(codon))

            if len(amino_pair) == variable_sites_number and "-" not in amino_pair:
                amino_acid_list.append(amino_pair)

    return amino_acid_list

def load_amino_dic(variable_sites_number=2):
    #Adds the amino acids counts to the dictionary  

    amino_acids = [".",1],["A",2],["C",1],["D",1],["E",1],["F",1],["G",2],["H",1],["I",1],["K",1],["L",3],["M",1],["N",1],["P",2],["Q",1],["R",3],["S",3],["T",2],["V",2],["W",1],["Y",1]

    amino_dic = {}

    loop = range(len(amino_acids) ** variable_sites_number)

    for i in loop:
        key = ""
        count = i

        for j in range(variable_sites_number):

            amino_len = len(amino_acids)
            m = ((count) % (amino_len ** (j+1))) / (amino_len ** (j))
            key += f"{amino_acids[int(m)][0]}\t"
            count -= m
            
        amino_dic[key] = 0

    return amino_dic

def populate_amino_dic(amino_acid_list,amino_dic):
    #Initializes the amino acid dictionary with empty values 

    for amino_pair in amino_acid_list:
        key = ""
        for amino in amino_pair:
            key += amino + "\t"
        amino_dic [key] += 1

def write_out_file(out_file,amino_dic,region_marker_list):
    #Print out file as a excel or CSV

    try:
        import pandas as pd
        print('module pandas run')

        out_file = f'{out_file}.xlsx'
        
        columns=[]
        for index,item in enumerate(region_marker_list):
            columns.append(f"Site_{index+1}:" + str(item[0]))

        columns.append("amino_acid_counter")
        amino = []

        for key in amino_dic.keys():
            key_list = key.split("\t")
            key_list[-1] = amino_dic[key]
            amino.append(key_list)

        df = pd.DataFrame(list(amino), columns=columns)
        df.to_excel(out_file)

        return out_file

    except:
        print('module pandas not found. changing output to CSV instead of excel')

        out_file = out_file + ".csv"

        print(out_file)

        with open(out_file,"w") as f:
            for index,item in enumerate(region_marker_list):
                f.write(f"Site_{index+1}:" + str(item[0]))
                f.write(",")

            f.write("amino_acid_counter")
            f.write("\n")

            for key in amino_dic .keys():
                f.write(",".join(key.split("\t")) +str(amino_dic[key]) +"\n")

        f.close

        return out_file


def main(input_fasta_file,in_put_fastq,out_file = "",is_file_fasta = True,is_file_fastq = True,phread_score = 20,distance_5_prime = 8,distance_3_prime = 8,variable_sites_number = 2):

    #main driver code 

    ref_fasta_sequence = fasta_to_single_line_string(input_fasta_file,is_file_fasta) #Converts fasta file into single line

    list_non_standard_nucleotide_region = find_variable_sites(ref_fasta_sequence,variable_sites_number) #returns a list of all continuous regions with nonstandard nucleotides

    region_marker_list = find_guide_sequences(ref_fasta_sequence,list_non_standard_nucleotide_region,distance_5_prime,distance_3_prime) #Find guide sequences

    sequence_list = get_fastq_sequence_list(in_put_fastq,is_file_fastq) #Preprocess fastq file into individual list of sequences

    fasta_line_list = [n[1] for n in fastq_to_fasta_sequence(sequence_list,phread_score)] #Converts the each fastq sequence into a fasta sequence based on phread score 

    codon_list = find_codon_list(region_marker_list,fasta_line_list) #Find guide sequences

    amino_acid_list = convert_codons_to_amino_acid_list(codon_list,variable_sites_number) #This transforms the codon list to a list of amino acids

    amino_dic = load_amino_dic(variable_sites_number) #Adds the amino acids counts to the dictionary 

    populate_amino_dic(amino_acid_list,amino_dic) #Initializes the amino acid dictionary with empty values 

    reverse_complement_region_marker_list = reverse_complement_region_marker(region_marker_list) #Reverses the region marker sequences

    reverse_codon_list = find_codon_list(reverse_complement_region_marker_list,fasta_line_list) #Find guide sequences
    
    reverse_codon_list = reverse_complement_nucleotide(reverse_codon_list) #Reverses the nucleotide sequences

    reverse_amino_acid_list = convert_codons_to_amino_acid_list(reverse_codon_list,variable_sites_number) #This transforms the codon list to a list of amino acids

    populate_amino_dic(reverse_amino_acid_list,amino_dic) #Initializes the amino acid dictionary with empty values 

    if len(out_file) > 0:
        print("run")
        return write_out_file(out_file,amino_dic,list_non_standard_nucleotide_region)
    else:
        return amino_dic


if __name__ == '__main__':

    parser = init_argparse()
    args = parser.parse_args()

    # Inputs ================================================================================================
    input_fasta_file = args.fasta
    in_put_fastq = args.fastq
    out_file = args.output
    phread_score = args.phread
    five_prime = args.five_prime
    three_prime = args.three_prime
    variable_sites = args.variable
    # ========================================================================================================




    # Check Inputs are valid =================================================================================
    
    assert type(input_fasta_file) == str
    assert type(in_put_fastq) == str
    assert type(out_file) == str
    assert type(phread_score) == int
    assert type(five_prime) == int
    assert type(three_prime) == int
    assert type(variable_sites) == int
    

    # ========================================================================================================
    

    print(f"Settings selected \nInput fasta file:\t{input_fasta_file}")
    print(f"Input fastq file:\t{in_put_fastq}")
    print(f"Output file name:\t{out_file}")
    print(f"Phread score:\t{phread_score}")
    print(f"Five prime base pair match:\t{five_prime}")
    print(f"Three prime base pair match:\t{three_prime}")
    print(f"Variable sites:\t{variable_sites}")
    print(main(input_fasta_file,in_put_fastq,out_file,True,True,phread_score,five_prime,three_prime,variable_sites))
    