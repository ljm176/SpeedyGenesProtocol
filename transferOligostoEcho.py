     

   
metadata = {
    'protocolName': 'Load Echo Plates with Glycerol',
    'author': 'Lachlan <lajamu@biosustain.dtu.dk',
    'source': 'DTU Biosustain',
    'apiLevel': '2.9'
}


def run(protocol):
        #Load Tips
    
        tips20 = [protocol.load_labware('opentrons_96_tiprack_20ul', 1)]
        p20Single = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=tips20)
        
        
        echoPlate1 = protocol.load_labware("echo_384_pp_standard", 3)
        
        aluminium = protocol.load_labware("opentrons_24_aluminumblock_generic_2ml_screwcap", 6)
        
        for i in range(24):
            p20Single.transfer(6, aluminium.wells()[i], 
                               echoPlate1.wells()[i], 
                               mix_after = (3, 20), 
                               touch_tip=True)
        
        
        
        



        






        
