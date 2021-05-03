n_reactions = 18

metadata = {
    'protocolName': 'BlockPCR and iIgestion',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.8'
}

# Set initial denaturing
init_temp = 98
init_time = 60

# set Denaturing
d_temp = 98
d_time = 15

# Set annealing
a_temp = 52
a_time = 15

# Set Extension
e_temp = 72
e_time = 30



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
    tc_mod.set_block_temperature(init_temp, hold_time_seconds=init_time)

    # Set Profile
    profile = [
        {'temperature': d_temp, 'hold_time_seconds': d_time},
        {'temperature': a_temp, 'hold_time_seconds': a_time},
        {'temperature': e_temp, 'hold_time_seconds': e_time}
    ]

    tc_mod.execute_profile(steps=profile, repetitions=25, block_max_volume=25)

    # Final extension
    tc_mod.set_block_temperature(72, hold_time_seconds=300)
    tc_mod.set_block_temperature(4)

    tc_mod.open_lid()
    protocol.pause("Remove Seal")

    for i in range(n_reactions):
        p300Single.transfer(50, waterExo, PCR_plate.wells()[i], mix_after=(2,75), touch_tip=True)

    protocol.pause("Add seal")

    #Exonuclese 1 Digestion

    tc_mod.close_lid()
    tc_mod.set_lid_temperature(98)
    tc_mod.set_block_temperature(37, hold_time_minutes=15)
    tc_mod.set_block_temperature(80, hold_time_minutes=15)
    tc_mod.set_block_temperature(10)

    tc_mod.open_lid()
