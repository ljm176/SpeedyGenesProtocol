import csv, itertools, string

#Read csv and generate list of first column
csv_file = "exampleCSV.csv"
with open(csv_file, "r") as f:
    csv_read = csv.reader(f, delimiter=";")
    t = [row[0] for row in csv_read]
print(len(t))
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

w = 0
oligo_wells = []
for oligo_list in l:
    oligo_wells.append([])
    for oligo in oligo_list:
        oligo_wells[-1].append(wells384[w])
        w+=1

block1 = oligo_wells[0:6]
block2 = oligo_wells[6:15]

def get_pools(block):
    pools = list(itertools.product(*block))
    return(pools)

b1pools = get_pools(block1)
b2pools = get_pools(block2)

print(len(b2pools))

src_plate = "Source Plate"
dest_plate = "Dest Plate"

def make_transfer_list(src_w, dst_w, vol=75):
    return([src_w, dst_w, vol])


def get_pool_transfers(pool, d):
    transfers = []
    #primer transfer
    for ol in [pool[0], pool[-1]]:
        transfers.append(make_transfer_list(ol, d, vol=1500))
    for ol in pool[1:-1]:
        transfers.append(make_transfer_list(ol, d))
    return(transfers)

ts = [[ "SrcWell"," DstWell", "Vol"]]
for p, w in zip(b1pools + b2pools, wells96):
    ts = ts + get_pool_transfers(p, w)


with open("mAusFPPools.csv", "w", newline="") as outputCSV:
    echoWriter = csv.writer(outputCSV, delimiter=";")
    for t in ts:
        echoWriter.writerow(t)





