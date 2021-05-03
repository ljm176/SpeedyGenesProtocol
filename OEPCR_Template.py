metadata = {
    'protocolName': 'SpeedyGenes Block Pooling',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.8'
    }

from math import ceil

nCols = ceil(len(blocks)/8)

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
    tips20= [protocol.load_labware('opentrons_96_tiprack_20ul', '6')]
    tips300 = [protocol.load_labware('opentrons_96_tiprack_300ul', '3')]

    #Load Pipettes
    p20Single = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=tips20)
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
    water = reagents["A2"]

    #Load fragment plates
    block_plate = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", location=2, label="Blocks")


    dil_plate = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", 5, label="Dilution Plate")
    

    if tc_mod.lid_position != open:
        tc_mod.open_lid()
    

    p300Single.distribute(14, water, [dil_plate.wells()[i] for i in range(blocks[-1][-1] + 1)])

    #add master mix to wells
    p300Single.pick_up_tip()
    for c in range(nCols):
        src=mastermix

        p300Single.aspirate(150, src)
        for w in range(8):
            p300Single.dispense(15, OEpcr_rack.wells()[w+(c*8)])
            p300Single.touch_tip()
        p300Single.blow_out(src)
    p300Single.drop_tip()

    def list_positions(ind):
    	positions = []
    	for i in blocks:
    		positions.append(i[ind])
    	positions = list(set(positions))
    	return(positions)



    b1_positions = list_positions(0)
    b2_positions = list_positions(1)



    def dilute_and_transfer_b1(pos):
    	p20Single.pick_up_tip()
    	p20Single.transfer(7, block_plate.wells()[pos], dil_plate.wells()[pos], mix_after=(2, 20), new_tip="never")
    	dests = []
    	for i in range(len(blocks)):
    		if blocks[i][0] == pos:
    			dests.append(i)

    	p20Single.distribute(1, dil_plate.wells()[pos], [OEpcr_rack.wells()[x] for x in dests], new_tip="never")
    	p20Single.drop_tip()


    def dilute_and_transfer_b2(pos):
    	p20Single.pick_up_tip()
    	p20Single.transfer(7, block_plate.wells()[pos], dil_plate.wells()[pos], mix_after=(2, 20), new_tip="never")
    	dests = []
    	for i in range(len(blocks)):
    		if blocks[i][1] == pos:
    			dests.append(i)

    	p20Single.transfer(1, dil_plate.wells()[pos], OEpcr_rack.wells()[dests[0]], mix_after=(2, 20), new_tip="never")
    	p20Single.drop_tip()

    	for x in dests[1:len(dests)]:
    			p20Single.transfer(1, dil_plate.wells()[pos], OEpcr_rack.wells()[x], mix_after=(2, 20))





    for i in b1_positions:
    	dilute_and_transfer_b1(i)

    for i in b2_positions:
    	dilute_and_transfer_b2(i)


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

    tc_mod.set_block_temperature(4)

    protocol.pause("Load Deepwell and A. Baylyi")

    falconRack = protocol.load_labware("opentrons_6_tuberack_falcon_50ml_conical", location=9, label="Baylyi Rack")
    baylyi = falconRack["A1"]
    deepWell = protocol.load_labware("usascientific_96_wellplate_2.4ml_deep", location= 4, label="DeepWell")

    
    protocol.comment("Transforming")

    p300Single.pick_up_tip()
    for i in range(len(blocks)):
        p300Single.transfer(500, baylyi,deepWell.wells()[i], new_tip="never")
    p300Single.drop_tip()

    tc_mod.open_lid()
    
    for i in range(len(blocks)):
        p20Single.transfer(5, OEpcr_rack.wells()[i], deepWell.wells()[i])

    protocol.comment("Congratulations! \nRun complete. Place deep well plate in 30 degree incubator")