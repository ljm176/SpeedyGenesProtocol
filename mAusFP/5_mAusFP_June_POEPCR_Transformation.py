nSamples = 32
metadata = {
    'protocolName': 'SpeedyGenes Block Pooling',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.8'
    }

lowEvapWell = [x + i for x in range(18, 75, 8) for i in (range(4))]

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

    #Load fullGene plates
    gene_plate = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", location=2, label="Inserts")

    if tc_mod.lid_position != open:
        tc_mod.open_lid()
    POEPCRWells = [OEpcr_rack.wells()[i] for i in lowEvapWell[0:nSamples]]

    #TODO: Function to save mastermix.
    p300Single.distribute(22, mastermix, POEPCRWells, touch_tip=True)

    #Transfer genes
    for i in lowEvapWell[0:nSamples]:
        p20Single.transfer(3, gene_plate.wells()[i],
                           OEpcr_rack.wells()[i],
                           mix_before=(2, 20),
                           mix_after=(2, 20),
                           touch_tip=True)

    tc_mod.close_lid()
    tc_mod.set_lid_temperature(110)

    
    # Initial denaturing
    tc_mod.set_block_temperature(98, hold_time_seconds=30, block_max_volume=25)
                                 
    #Set Profile
    profile = [
        {'temperature': 98, 'hold_time_seconds': 15},
        {'temperature': 72, 'hold_time_seconds': 15},
        {'temperature': 72, 'hold_time_seconds': 300}
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
    for i in range(nSamples+1):
        p300Single.transfer(500, baylyi, deepWell.wells()[i], new_tip="never")
    p300Single.drop_tip()

    tc_mod.open_lid()

    p20Single.transfer(5,POEPCRWells, [deepWell.wells()[i] for i in range(nSamples)])

    protocol.comment("Congratulations! \nRun complete. Place deep well plate in 30 degree incubator")