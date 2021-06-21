import csv, itertools, string

projectName = input("Enter name for project")
csv_file = input("Enter CSV file name (without extension)") + ".csv"

print("Writing Echo CSV_1")
#Read csv and generate list of first column

with open(csv_file, "r") as f:
    csv_read = csv.reader(f, delimiter=";")
    t = [row[0] for row in csv_read]


def is_variant(s):
    if "v" in s:
        return (True)
    else:
        return (False)

#Generate list of lists with variants together in nested list.
l = []
for i in t:
    if is_variant(i):
        l[-1].append(i)
    else:
        l.append([i])

#make list of wells in 384 well plate
rows = list(string.ascii_uppercase)[0:16]
cols = list(range(1,25))
wells384 = []
for col in cols:
    for letter in rows:
        wells384.append(letter + str(col))

#make list of wells in 96 well plate
rows = list(string.ascii_uppercase)[0:8]
cols = list(range(1, 13))
wells96 = []
for col in cols:
    for letter in rows:
        wells96.append(letter + str(col))

lowEvapWells= [x + i for x in range(18, 75, 8) for i in (range(4))]
lowEvap96 = [wells96[w] for w in lowEvapWells]



#define oligo wells by position in 384 well plate
w = 0
oligo_wells = []
for oligo_list in l:
    oligo_wells.append([])
    for oligo in oligo_list:
        oligo_wells[-1].append(wells384[w])
        w+=1

#Define blocks (6 and 7 oligos per block) This might need to be modified.
block1 = oligo_wells[0:6]
block2 = oligo_wells[6:15]

def get_pools(block):
    pools = list(itertools.product(*block))
    return(pools)

b1pools = get_pools(block1)
b2pools = get_pools(block2)


src_plate = "Source Plate"
dest_plate = "Dest Plate"

def make_transfer_list(src_w, dst_w, vol=75):
    return([src_w, dst_w, vol])


def get_pool_transfers(pool, d):
    transfers = []
    #primer transfer
    for ol in [pool[0], pool[-1]]:
        transfers.append(make_transfer_list(ol, d, vol=1500))

    #Protein Transfer
    for ol in pool[1:-1]:
        transfers.append(make_transfer_list(ol, d))
    return(transfers)

ts = [[ "Source Well"," Destination Well", "Transfer Volume"]]
for p, w in zip(b1pools + b2pools, lowEvap96):
    ts = ts + get_pool_transfers(p, w)

n_blocks = len(b1pools + b2pools)

MM_ts = [[ "Source Well"," Destination Well", "Transfer Volume"]]
for i in range(n_blocks):
    MM_ts = MM_ts + [["A1", lowEvap96[i], 12500]]
for i in range(n_blocks):
    MM_ts = MM_ts + [["A2", lowEvap96[i], 9200]]


EchocsvFile = "1_" + projectName + "_EchoOligoTransfers"+".csv"

with open(EchocsvFile, "w", newline="") as outputCSV:
    echoWriter = csv.writer(outputCSV, delimiter=",")
    for t in ts:
        echoWriter.writerow(t)


echoMMcsvFile = "2_" + projectName + "_MasterMix.csv"

with open(echoMMcsvFile, "w", newline="") as MMOutputCSV:
    echoMMWriter = csv.writer(MMOutputCSV, delimiter=",")
    for MM_T in MM_ts:
        echoMMWriter.writerow(MM_T)

print("Writing OT Block PCR and Digestion Protocol")

pcrProt = open("BlockPCR_ExoDigestion_Template.txt", "r")
new_pcrProt_name = "3_" + projectName + "_BlockPCRDig.py"
new_pcrProt = open(new_pcrProt_name, "w")

new_pcrProt.write("n_reactions = " + str(n_blocks))
new_pcrProt.write("\n")

for line in pcrProt:
    new_pcrProt.write(line)
new_pcrProt.close()


print("Writing OT Full Gene Protocol")
b1 = [i for i in range(len(b1pools))]
b2 = [i + len(b1pools) for i in range(len(b2pools))]

#Convert to low evap positions
b1_lowEvap = [lowEvapWells[x] for x in b1]
b2_lowEvap = [lowEvapWells[x] for x in b2]

b_1_2 = [b1_lowEvap] + [b2_lowEvap]

block_combs = []
for i in itertools.product(*b_1_2):
    block_combs.append(list(i))


oe_pcr_prot = open("FullBlockSynthesis_Template.txt", "r")

new_oe_pcr_prot_name = "4_" + projectName + "_OEPCR_OT.py"

new_oe_pcr_prot = open(new_oe_pcr_prot_name, "w")

new_oe_pcr_prot.write("blocks =" + str(block_combs))
new_oe_pcr_prot.write("\n")

for line in oe_pcr_prot:
    new_oe_pcr_prot.write(line)
new_oe_pcr_prot.close()

print("Writing Plating Protocol")


print("Setup Complete - Proceed to Wet Lab")

