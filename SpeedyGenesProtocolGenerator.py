import csv, itertools, string, sys



projectName = "MAusTest"


print("Writing Echo CSV_1")
#Read csv and generate list of first column
csv_file = "exampleCSV.csv"


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

#define oligo wells by position in 384 well plate
w = 0
oligo_wells = []
for oligo_list in l:
    oligo_wells.append([])
    for oligo in oligo_list:
        oligo_wells[-1].append(wells384[w])
        w+=1

#Define blocks (6 and 7 oligos per block)
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

ts = [[ "SrcWell"," DstWell", "Vol"]]
for p, w in zip(b1pools + b2pools, wells96):
    ts = ts + get_pool_transfers(p, w)


MM_ts = [[ "SrcWell"," DstWell", "Vol"]]
for i in range(len(b1pools + b2pools)):
    MM_ts = MM_ts + [["A1", wells96[i], 12500]]
for i in range(len(b1pools + b2pools)):
    MM_ts = MM_ts + [["A2", wells96[i], 9500]]


EchocsvFile = projectName + "_EchoTransfers"+".csv"

with open(EchocsvFile, "w", newline="") as outputCSV:
    echoWriter = csv.writer(outputCSV, delimiter=";")
    for t in ts:
        echoWriter.writerow(t)


echoMMcsvFile = projectName + "_MasterMix.csv"
with open(echoMMcsvFile, "w", newline="") as MMOutputCSV:
    echoMMWriter = csv.writer(MMOutputCSV, delimiter=";")
    for MM_T in MM_ts:
        echoMMWriter.writerow(MM_T)

print("Writing OT Protocol")

b1 = [i for i in range(len(b1pools))]

b2 = [i + len(b1pools) for i in range(len(b2pools))]

b_1_2 = [b1] + [b2]

block_combs = []
for i in itertools.product(*b_1_2):
    block_combs.append(list(i))


prot = open("OEPCR_Template.txt", "r")

new_prot_name = projectName + "_OEPCR_OT.py"

new_prot = open(new_prot_name, "w")

new_prot.write("blocks =" + str(b_1_2))
new_prot.write("\n")

for line in prot:
    new_prot.write(line)
new_prot.close()



