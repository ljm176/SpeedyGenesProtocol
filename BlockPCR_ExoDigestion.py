n_blocks=8

lowEvapWells= [x + i for x in range(18, 75, 8) for i in (range(4))]

metadata = {
    'protocolName': 'BlockPCR and Digestion',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.8'
}

def run(protocol):
    # Load Tips
    tips20 = [protocol.load_labware('opentrons_96_tiprack_20ul', '1')]
    tips300 = [protocol.load_labware('opentrons_96_tiprack_300ul', '2')]

    # Load Pipettes
    p20Single = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=tips20)
    p300Single = protocol.load_instrument('p300_single', 'left', tip_racks=tips300)

    # Load Thermocylcer Module
    tc_mod = protocol.load_module('thermocycler')
    PCR_plate = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')

    if tc_mod.lid_position != open:
        tc_mod.open_lid()


    rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", "5")
    waterExo = rack.wells()[0]

    tc_mod.set_lid_temperature(110)
    tc_mod.close_lid()

    # Initial denaturing
    tc_mod.set_block_temperature(98, hold_time_seconds=30)

    # Set Profile
    profile = [
        {'temperature': 98, 'hold_time_seconds': 15},
        {'temperature': 52, 'hold_time_seconds': 15},
        {'temperature': 72, 'hold_time_seconds': 30}
    ]

    tc_mod.execute_profile(steps=profile, repetitions=25, block_max_volume=25)

    # Final extension
    tc_mod.set_block_temperature(72, hold_time_seconds=300)
    tc_mod.set_block_temperature(10)

    tc_mod.open_lid()

    for i in lowEvapWells[0:n_blocks]:
        p300Single.transfer(50, waterExo, PCR_plate.wells()[i], mix_after=(2,75), touch_tip=True)

    #Exonuclese 1 Digestion

    tc_mod.close_lid()
    tc_mod.set_lid_temperature(98)
    tc_mod.set_block_temperature(37, hold_time_minutes=20)
    tc_mod.set_block_temperature(80, hold_time_minutes=20)
    tc_mod.set_block_temperature(10)

    tc_mod.open_lid()
