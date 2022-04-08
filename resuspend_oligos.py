# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 07:27:40 2022

@author: lajamu
"""

metadata = {
    'protocolName': 'Add water to Oligos',
    'author': 'Lachlan <lajamu@biosustain.dtu.dk',
    'source': 'DTU Biosustain',
    'apiLevel': '2.9'
}

def run(protocol):
    tips1000 = [protocol.load_labware("geb_96_tiprack_1000ul", 1)]
    
    p1000 = protocol.load_instrument('p1000_single', 'right', tip_racks=tips1000)
    
    aluminium = protocol.load_labware("opentrons_24_aluminumblock_generic_2ml_screwcap", 2)
    rack = protocol.load_labware("opentrons_6_tuberack_falcon_50ml_conical", 5)
    
    water = rack["A1"]
    
    nmols = [19.4,
    21.8,
    78.7,
    19.4,
    15.9,
    18.9,
    28,
    19.3,
    16.9,
    22.8,
    30.3,
    68.9,
    20.5,
    21.6,
    25.2,
    27.4,
    31.4,
    22.2,
    22,
    22.7,
    22.3,
    68.5,
    71.6,
    26.4]
    
    p1000.pick_up_tip()
    
    for i in range(len(nmols)):
        p1000.transfer(nmols[i]*10, water, aluminium.wells()[i].top(), new_tip="never")
        
    p1000.drop_tip()
