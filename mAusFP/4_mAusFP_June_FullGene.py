blocks =[[18, 20], [18, 21], [18, 26], [18, 27], [18, 28], [18, 29], [18, 34], [18, 35], [18, 36], [18, 37], [18, 42], [18, 43], [18, 44], [18, 45], [18, 50], [18, 51], [19, 20], [19, 21], [19, 26], [19, 27], [19, 28], [19, 29], [19, 34], [19, 35], [19, 36], [19, 37], [19, 42], [19, 43], [19, 44], [19, 45], [19, 50], [19, 51]]
metadata = {
    'protocolName': 'SpeedyGenes Full Block Synthesis',
    'author': 'Lachlan Munro',
    'source': 'Protocol Library',
    'apiLevel': '2.8'
    }

lowEvapWell = [x + i for x in range(18, 75, 8) for i in (range(4))]

def run(protocol):
    # Load Tips
    tips20 = [protocol.load_labware('opentrons_96_tiprack_20ul', '6')]
    tips300 = [protocol.load_labware('opentrons_96_tiprack_300ul', '3')]

    # Load Pipettes
    p20Single = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=tips20)
    p300Single = protocol.load_instrument('p300_single', 'left', tip_racks=tips300)

    # Load Thermocylcer Module
    tc_mod = protocol.load_module('thermocycler')
    fullBlockPCR = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', label="Thermocylcer")

    pcrWells = [fullBlockPCR.wells()[i] for i in lowEvapWell]

    # Load temp_block
    temp_block = protocol.load_module("tempdeck", 1)
    temp_block.set_temperature(4)

    # Load Reagents
    reagents = temp_block.load_labware("opentrons_24_aluminumblock_nest_1.5ml_snapcap", label="Reagents")
    # Load 2x Mastermix with primers added
    mastermix = reagents["A1"]
    waterExo = reagents["A2"]
    mastermix_POEPCR = reagents["A3"]

    # Load fragment plates
    block_plate = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", location=2, label="Blocks")

    if tc_mod.lid_position != open:
        tc_mod.open_lid()

    # add master mix to wells
    p300Single.pick_up_tip()
    p300Single.transfer(15, mastermix, pcrWells, new_tip="never", touch_tip=True)
    p300Single.drop_tip()
    #TODO: Funtion to run as a distribute without wasting reagent

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
        dests = []
        for i in range(len(blocks)):
            if blocks[i][0] == pos:
                dests.append(i)
        p20Single.distribute(2, block_plate.wells()[pos], [pcrWells[x] for x in dests], new_tip="never")
        p20Single.drop_tip()


    def dilute_and_transfer_b2(pos):
        dests = []
        for i in range(len(blocks)):
            if blocks[i][1] == pos:
                dests.append(i)
        for x in dests:
                p20Single.transfer(2, block_plate.wells()[pos], pcrWells[x], mix_after=(2, 20))

    for i in b1_positions:
        protocol.comment(str(i))
        dilute_and_transfer_b1(i)

    for i in b2_positions:
        protocol.comment(str(i))
        dilute_and_transfer_b2(i)

    tc_mod.close_lid()
    tc_mod.set_lid_temperature(110)

    # Initial denaturing
    tc_mod.set_block_temperature(98, hold_time_seconds=30, block_max_volume=25)

    # Set Profile
    profile1 = [
        {'temperature': 98, 'hold_time_seconds': 10},
        {'temperature': 52, 'hold_time_seconds': 15},
        {'temperature': 72, 'hold_time_seconds': 30}
    ]

    profile2 = [
        {'temperature': 98, 'hold_time_seconds': 10},
        {'temperature': 65, 'hold_time_seconds': 15},
        {'temperature': 72, 'hold_time_seconds': 30}
    ]
    tc_mod.execute_profile(steps=profile1, repetitions=10, block_max_volume=25)
    tc_mod.execute_profile(steps=profile2, repetitions=18, block_max_volume=25)

    # Final extension
    tc_mod.set_block_temperature(72, hold_time_seconds=300, block_max_volume=25)

    tc_mod.set_block_temperature(4)
    tc_mod.open_lid()
    p300Single.transfer(50, waterExo, pcrWells, mix_after=(2,75), touch_tip=True)

    #Exonuclese 1 Digestion

    tc_mod.close_lid()
    tc_mod.set_lid_temperature(98)
    tc_mod.set_block_temperature(37, hold_time_minutes=20)
    tc_mod.set_block_temperature(80, hold_time_minutes=20)
    tc_mod.set_block_temperature(10)

    protocol.pause("Full Gene synthesis complete. Click proceed to open lid")
    tc_mod.open_lid()



