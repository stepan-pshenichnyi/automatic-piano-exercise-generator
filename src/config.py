GRADE_SETTINGS = {
        
    "initial": {
        "structures": [
            {"bars": 4, "time_signature": "4/4"},
            {"bars": 6, "time_signature": "2/4"}
        ],
        "keys": ["C_major", "D_minor"],
        "position": "5_finger"
    },

    1: {

        "structures": [
            {"bars": 4, "time_signature": "4/4"},
            {"bars": 4, "time_signature": "3/4"},
            {"bars": 6, "time_signature": "2/4"}
        ],

        "keys": [
            "C_major",
            "D_minor",
            "G_major",
            "F_major",
            "A_minor"
        ],
        "position": "any_5_finger"
    },


    2: {"structures": [
        {"bars": 4, "time_signature": "4/4"},
        {"bars": 4, "time_signature": "3/4"},
        {"bars": 6, "time_signature": "2/4"},
    ],
    "keys": [
            "C_major",
            "D_minor",
            "G_major",
            "F_major",
            "D_major", 
            "A_minor",
            "E_minor",
            "G_minor" 
        ],
        
    "position": "any_5_finger"

    },

    3: {

    "structures": [
        {"bars": 4, "time_signature": "4/4"},
        {"bars": 4, "time_signature": "3/4"},
        {"bars": 6, "time_signature": "2/4"},
        {"bars": 8, "time_signature": "2/4"},   
        {"bars": 8, "time_signature": "3/4"},   
        {"bars": 4, "time_signature": "3/8"},   
    ],

    "keys": [
        "C_major",
        "G_major",
        "D_major",
        "F_major",
        "B_flat_major",     
        "E_flat_major",     

        "A_minor",
        "D_minor",
        "E_minor",
        "G_minor",
        "B_minor"           
    ],

    
    "position": "extended"

    },

    4: {

    "structures": [
        {"bars": 8, "time_signature": "4/4"},
        #{"bars": 4, "time_signature": "3/4"},
        {"bars": 6, "time_signature": "2/4"},
        {"bars": 8, "time_signature": "2/4"},   
        {"bars": 8, "time_signature": "3/4"},   
        {"bars": 8, "time_signature": "3/8"},
        #{"bars": 4, "time_signature": "6/8"}, #grade4
        {"bars": 8, "time_signature": "6/8"}  #grade4
    ],

    "keys": [
        "C_major",
        "G_major",
        "D_major",
        "F_major",
        "B_flat_major",     
        "E_flat_major",     

        "A_minor",
        "D_minor",
        "E_minor",
        "G_minor",
        "B_minor"           
    ],

    
    "position": "extended"

}  
}


DIFFICULTY_PROFILES = {

    "initial": {

        "max_interval": 4,
        "preferred_interval": 2,

        "range": (55, 76),

        "use_position_range": True,

        "allowed_durations": {1.0, 0.5, 2.0},

        "step_bias": 1.5,
        "leap_penalty": 0.6,

        "accidentals": False,

        "cadence_strength": 3.0,
        "staff_limits": {
            "RH": (60, 76),  # C4 to E5 (no ledger lines)
            "LH": (48, 64)   # C3 to E4
            }},

    1: {

        "max_interval": 5,
        "preferred_interval": 3,

        "range": (55, 76),
        "use_position_range": True,

        "allowed_durations": {1.0, 0.5, 2.0, 1.5},

        "step_bias": 1.5,
        "leap_penalty": 0.8,

        "accidentals": True,

        "cadence_strength": 2.5,
        "staff_limits": {
            "RH": (60, 76),  # C4 to E5 (no ledger lines)
            "LH": (48, 64)   # C3 to E4
            }
    },

    2: {

        "max_interval": 6,
        "preferred_interval": 3,

        "range": (53, 78),

        "allowed_durations": {1.0, 0.5, 2.0, 4.0, 1.5, 0.25}, 

        "step_bias": 1.35,
        "leap_penalty": 0.9,

        "accidentals": True,

        "cadence_strength": 2.5,
        "staff_limits": {
            "RH": (60, 76),  # C4 to E5 (no ledger lines)
            "LH": (48, 64)   # C3 to E4
            }
        },
        
    3: {
        "max_interval": 8,
        "preferred_interval": 4,

        "range": (50, 81),

        "allowed_durations": {
            4.0,
            2.0,
            1.5,
            1.0,
            0.75,   # dotted eighth
            0.5,
            0.25    # semiquaver
        },

        "step_bias": 1.25,
        "leap_penalty": 0.95,

        "accidentals": True,

        "cadence_strength": 2.2,

        "staff_limits": {
            "RH": (58, 81),
            "LH": (43, 65)
        },

        
        "allow_two_note_chords": True,
        "allow_position_shift": True,
        "allow_eighth_rest": True,
        "compound_meter": True
        },

    4: {
        "max_interval": 9,
        "preferred_interval": 4,

        "range": (50, 81),

        "allowed_durations": {
            4.0,
            3.0,      # dotted minim for 6/8 
            2.0,
            1.5,
            1.0,
            0.75,
            0.5,
            0.25
        },

        "step_bias": 1.20,
        "leap_penalty": 1.0,

        "accidentals": True,

        "cadence_strength": 2.0,

        "staff_limits": {
            "RH": (58, 81),
            "LH": (43, 65)
        },

        "allow_two_note_chords": True,
        "allow_position_shift": True,
        "allow_eighth_rest": True,
        "compound_meter": True,

        # New Grade 4 features
        "allow_chromatic_notes": True,
        "chromatic_probability": 0.08,

        "allow_fermata": True,
        "fermata_probability": 0.15,

        "allow_anacrusis": True
    }
    }


TIME_SIGNATURE_BEATS = {
    "2/4": 2.0,
    "3/4": 3.0,
    "4/4": 4.0,
    "3/8": 1.5,
    "6/8": 3.0 # grade4
}
