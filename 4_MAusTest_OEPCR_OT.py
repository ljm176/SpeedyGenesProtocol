blocks = [[0, 2],
 [0, 3],
 [0, 4],
 [0, 5],
 [0, 6],
 [0, 7],
 [0, 8],
 [0, 9],
 [0, 10],
 [0, 11],
 [0, 12],
 [0, 13],
 [0, 14],
 [0, 15],
 [0, 16],
 [0, 17],
 [1, 2],
 [1, 3],
 [1, 4],
 [1, 5],
 [1, 6],
 [1, 7],
 [1, 8],
 [1, 9],
 [1, 10],
 [1, 11],
 [1, 12],
 [1, 13],
 [1, 14],
 [1, 15],
 [1, 16],
 [1, 17]]

metadata = {
    'protocolName': 'SpeedyGenes Combinatorial OEPCR',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.8'
    }

nReactions = len(blocks)

#Set PCR Parameters
#Set initial denaturing
init_temp = 98
init_time = 30 

#set Denaturing
d_temp = 98
d_time = 10

#Set annealing
a_temp = 72
a_time = 20

#Set Extension
e_temp = 72
e_time = 300

def run(protocol):
    #Load Tips
    #tips20= [protocol.load_labware('opentrons_96_tiprack_20ul', x), for x in [6, 10]]
    tips300 = [protocol.load_labware('opentrons_96_tiprack_300ul', '3')]

    #Load Pipettes
    p20Single = protocol.load_instrument('p20_single_gen2', 'right',
                                         tip_racks=[protocol.load_labware('opentrons_96_tiprack_20ul', x)
                                                    for x in [6, 10]])
    p300Single = protocol.load_instrument('p300_single', 'left', tip_racks=tips300)

    #Load Thermocylcer Module
    tc_mod = protocol.load_module('thermocycler')
    OEpcr_rack = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', label="Thermocylcer")

    #Load temp_block
    temp_block = protocol.load_module("tempdeck", 1)
    temp_block.set_temperature(4)

    #Load Reagents
    reagents = temp_block.load_labware("opentrons_24_aluminumblock_nest_1.5ml_snapcap", label="Reagents")
    #Load 2x Mastermix
    mastermix = reagents["A1"]
    template = reagents["A2"]
    water = reagents["A3"]

    #Load fragment plates
    dil_plate = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", 5, label="Dilution Plate")
    

    if tc_mod.lid_position != open:
        tc_mod.open_lid()

    #add master mix to wells
    p300Single.distribute(10, mastermix, OEpcr_rack.wells()[0:nReactions])
    #add vector to wells
    p20Single.distribute(4, mastermix, OEpcr_rack.wells()[0:nReactions])

    #Function to return a list of positions that take each block
    #This is weirdly complicated for what it is. I don't know why i wrote it like this.
    def list_positions(ind):
        positions = []
        for i in blocks:
            positions.append(i[ind])
        positions = list(set(positions))
        return(positions)

    #Generate positions for each block (as well number)
    b1_positions = list_positions(0)
    b2_positions = list_positions(1)



    def transfer_blocks(pos, b, dis=True):
        dests = []
        for i in range(len(blocks)):
            if blocks[i][b] == pos:
                dests.append(i)
        if dis:
            p20Single.pick_up_tip()
            p20Single.distribute(1, dil_plate.wells()[pos], [OEpcr_rack.wells()[x] for x in dests], new_tip="never")
            p20Single.drop_tip()
        else:
            for x in dests:
                p20Single.transfer(1, dil_plate.wells()[pos], OEpcr_rack.wells()[x], mix_after=(2, 20))

    for i in b1_positions:
        transfer_blocks(i, 0)
    for i in b2_positions:
        transfer_blocks(i, 1, dis=False)



    protocol.pause("Add PCR seal")

    tc_mod.close_lid()
    tc_mod.set_lid_temperature(110)

    
    # Initial denaturing
    tc_mod.set_block_temperature(init_temp, hold_time_seconds=init_time, block_max_volume=25)
                                 
    #Set Profile
    profile = [
        {'temperature': d_temp, 'hold_time_seconds': d_time},
        {'temperature': a_temp, 'hold_time_seconds': a_time},
        {'temperature': e_temp, 'hold_time_seconds': e_time}
    ]

    tc_mod.execute_profile(steps=profile, repetitions=35, block_max_volume=25)

    #Final extension
    tc_mod.set_block_temperature(72, hold_time_seconds = 600, block_max_volume=25)
    tc_mod.set_block_temperature(10)

    tc_mod.open_lid()
    protocol.pause("Load Deepwell and A. Baylyi")

    falconRack = protocol.load_labware("opentrons_6_tuberack_falcon_50ml_conical", location=9, label="Baylyi Rack")
    baylyi = falconRack["A1"]
    deepWell = protocol.load_labware("usascientific_96_wellplate_2.4ml_deep", location= 4, label="DeepWell")
    protocol.comment("Transforming")

    p300Single.pick_up_tip()
    for i in range(len(blocks)):
        p300Single.transfer(500, baylyi,deepWell.wells()[i], new_tip="never")
    p300Single.drop_tip()


    
    for i in range(len(blocks)):
        p20Single.transfer(5, OEpcr_rack.wells()[i], deepWell.wells()[i])

    protocol.comment("Congratulations! \nRun complete. Place deep well plate in 30 degree incubator")