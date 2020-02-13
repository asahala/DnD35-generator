#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" A. Sahala 2014 """

import re
import random

""" ===================================================================
 HOW TO ADD NEW RACES =================================================
=======================================================================

Adding new races should be fairly easy unless the racial bonuses are
very complicated and level-dependent. All standrd D&D 3.5 races have
been implemented with their bonuses.

´race_specs´
  Add new key (race's name) and fullfill all required field. Remember
  to add racial bonuses defined in ´racename_bonuses´ subdictionaries.

´races´
   Add new race under key ´any´. You may also build new subdictionaries
   for different types, e.g. ´giants´, ´outsiders´ etc.

´sizes´
   Add race's size modifiers. Very good summary can be found from:
   http://paizo.com/pathfinderRPG/prd/advancedRaceGuide/ageHeightWeight.html

´bonus_languages´
   Add possible bonus languages for new race.

=======================================================================
 HOW TO ADD NEW CLASSES================================================
=======================================================================

A lot more complicated than adding new races.

´class_languages´
   Define class specific languages if needed.

´classes´
   Add your class into subtypes

´class_specs´
   Define class specifications

´override´
   Define class skills.

´spells_per_day´, ´spells_known´
   If spellcaster, define spells

special_abs()
   Contains all class specific feats.
   Define class progression tables here. You may need to write new
   functions depending if abilities stack/have something very specific
   features.

=================================================================== """

# =====================================================================
# D&D 3.5 Character attributes
# =====================================================================

class Character(object):

    def __init__(self):
        abs = {'str': 0, 'dex': 0, 'con': 0, 'wis': 0, 'int': 0, 'cha': 0}

        self.name = str()
        self.gender = str()
        self.age = 0
        self.age_type = str()
        self.race = str()
        self.creature_type = str()
        self.alignment = str()
        self.eyes = str()
        self.skin = str()
        self.hair = str()
        self.size = str()
        self.size_for_items = str()
        self.physical = {'lbs': 0, 'kg': 0, 'ft':0, 'in': 0, 'cm': 0}
        self.speed_base = 0
        self.speed = 0
        self.run_speed_multiplier = 4
        self.speed_bonus = 0
        self.unarmored_speed_bonus = 0
        self.favored_enemy = list()

        self.class_feats = dict()
        self.race_feats = dict()
        self.feats = dict()
        self.spell_penetration = 0

        self.Class = list()
        self.level = list()

        self.has_animal_companion = False
        self.animal_companion = {'level': 0}

        self.has_familiar = False
        self.familiar = {'level': 0}

        self.turn_undead = 0

        self.grapple = 0
        self.initiative = 0

        self.level_type = str()
        self.power = 'normal'
        self.effective_level = 0
        self.skill_points = list()
        self.total_skill_points = dict()

        self.languages = list()
        self.scripts = list()

        #conditional AC modifiers
        self.ac_special_bonuses = {'dodge': {'vs. traps': 0,
                                            'vs. creatures': 0,
                                            'vs. giant types': 0}}

        self.armor_profiencies = list()
        self.weapon_profiencies = list()
        self.has_shield_profiency  = False
        self.sneak_attack = 0

        self.ac_unarmored_bonus = 0
        self.ac_modifiers = {
            'armor': 0,
            'shield': 0,
            'mods': 0,
            'size': 0,
            'natural': 0,
            'deflect': 0}
        self.ac = 0
        self.ac_base = 0
        self.ac_touch = 0
        self.ac_flat_footed = 0

        self.fast_healing = 0
        self.damage_reduction = {'-': 0, 'magic': 0,
                                'fire': 0, 'cold': 0,
                                'acid': 0}
        self.spell_resistance = 0

        self.hp = 0
        self.bab = 0

        self.unarmed_damage = None
        self.is_multiclass = False

        self.attacks = {1:0, 2:0, 3:0, 4:0}
        self.attack_adj = 0

        self.saves_total = {'fort': 0, 'ref': 0, 'will': 0}
        self.saves_base = {'fort': 0, 'ref': 0, 'will': 0}
        self.saves_mods = {
                            'fort': {'ab': 0, 'mag': 0, 'misc': 0},
                            'ref': {'ab': 0, 'mag': 0, 'misc': 0},
                            'will': {'ab': 0, 'mag': 0, 'misc': 0},
                            }

        self.save_special_bonuses = {
                'fort': {'vs. poison': 0},
                'ref': {'vs. traps': 0},
                'will': {'vs. ench.': 0},
                'general': {'vs. Fey': 0,
                            'vs. fear': 0,
                            'vs. spells': 0,
                            'vs. ench.': 0,
                            'vs. illusions': 0,
                            'vs. non-lethal': 0}}

        self.priority_order = list()
        self.abilities = abs.copy()
        self.ability_adjustments = abs.copy()
        self.ability_mods = abs.copy()

        self.wears_armor = False

        self.charisma_to_saves = False
        self.wisdom_to_ac = False

# Define D&D dice rolling rules =======================================
def roll_dice(dice, times, dice_mod, total_mod, ignore_lowest, *args):
    """ D&D dice roller
    ´dice´          dice type, e.g. d4, d6, d10
    ´times´         how many times dice will be rolled
    ´total_mod´     modifier applied to total score, e.g. 4d6+4
    ´dice_mod´      modifier applied to each roll (e.g. 1d8+1 x 4)
    ´ignore_lowest´ if multiple rolled, ignore lowest n rolls
    *args            may take input as a list too"""

    # If *args is given as a well-formed list, override variables
    if args:
        if isinstance(args[0], list) and len(args[0]) == 5:
            for arg in args[0]:
                if not isinstance(arg, int):
                    return 0
                else:
                    dice = args[0][0]
                    times = args[0][1]
                    dice_mod = args[0][2]
                    total_mod = args[0][3]
                    ignore_lowest = args[0][4]
        else:
            return 0

    total = total_mod
    rolls = []
    j = 0

    # If more rolls are ignored than thrown, return 0
    if ignore_lowest >= times:
        return 0
    else:
        while j < times:
            rolls.append(random.randint(1, dice) + dice_mod)
            j += 1
        rolls.sort()

        k = ignore_lowest
        while k < times:
            total += rolls[k]
            k += 1

        return total

# Define D&D dice =========================================================
#
#   dice                  dice types
#
# =========================================================================

dice = {'d00': 100,
        'd20': 20,
        'd12': 12,
        'd10': 10,
        'd8': 8,
        'd6': 6,
        'd4': 4}

# Define available genders ================================================

genders = ['male', 'female']

# Generate and define alignments ==========================================
#
#   alignment_types          different alignment subsets
#
# =========================================================================

def generate_alignments(alignments = []):
    for x in ['lawful', 'neutral', 'chaotic']:
        for y in ['good', 'neutral', 'evil']:
            alignments.append(re.sub('neutral neutral',
                                     'true neutral',
                                     '%s %s' % (x, y)))
    return alignments

alignments = generate_alignments()
alignment_types = {
    'any': alignments,
    'lawful': alignments[0:3],
    'nonneutral': [alignments[0], alignments[2],
                  alignments[6], alignments[8]],
    'lawfulgood': alignments[0],
    'nonlawful': alignments[3:],
    'nonlawfulgood': alignments[1:],
    'evil': [alignments[2], alignments[5], alignments[8]],
    'neutral': [alignments[1], alignments[4], alignments[7]],
    'good': [alignments[0], alignments[3], alignments[6]],
    'good_neutral': [alignments[0], alignments[3], alignments[6],
                    alignments[1], alignments[4], alignments[7]]}

# Define experience level types =======================================

level_types = {'novice\t(1-5)': [1, 5],
              'adventurer\t(6-9)': [6, 9],
              'master\t(10-14)': [10, 14],
              'champion\t(15-20)': [15, 20],
              'epic\t\t(21-30)': [21, 30],
              'demi-god\t(31-40)': [31, 40]}

# Define languages and scripts ========================================

languages = {
        "abyssal": "infernal",
        "aquan": "elven",
        "auran": "draconic",
        "celestial": "celestial",
        "common": "common",
        "draconic": "draconic",
        "druidic": "druidic",
        "dwarven": "dwarven",
        "elven": "elven",
        "giant": "dwarven",
        "gnome": "dwarven",
        "goblin": "dwarven",
        "gnoll": "common",
        "halfling": "common",
        "ignan": "draconic",
        "infernal": "infernal",
        "orc": "dwarven",
        "sylvan": "elven",
        "terran": "dwarven",
        "undercommon": "elven",
        "drow sign language": ""}

# Class specific bonus languages
class_languages = {
    'druid': ['druidic', 'sylvan'],
    'cleric': ['infernal', 'abyssal', 'celestial'],
    'wizard': ['draconic']}

# Race specific bonus languages
bonus_languages = {
    "human": list(set(languages.keys()) - set(["druidic"])),
    "half-elf": list(set(languages.keys()) - set(["druidic"])),
    "half-orc": ["draconic", "giant", "gnoll", "goblin", "abyssal"],
    "elf": ["draconic", "gnoll", "gnome", "goblin", "orc", "sylvan"],
    "halfling": ["dwarven", "elven", "gnome", "goblin", "orc"],
    "dwarf": ["giant", "gnome", "goblin", "orc", "terran", "undercommon"],
    "gnome": ["draconic", "dwarven", "elven", "giant", "goblin", "orc"],
    "drow": ["abyssal", "aquan", "draconic",
            "drow sign language", "gnome", "goblin"],
    "svirfneblin": ["dwarven", "elven", "giant", "goblin", "orc", "terran"],
    "duergar": ["draconic", "giant", "goblin", "orc", "terran"],
    "half-ogre": ["draconic", "gnoll", "goblin", "orc", "abyssal"],
    "orc": ["draconic", "giant", "gnoll", "goblin", "abyssal"],
    "ogre": ["dwarven", "orc", "goblin", "terran"]}

# Define character power types ========================================
#
#    ´ability_roll´            define how ability scores are rolled,
#                            cf. roll_dice()
#    ´hp_roll´                HP roll bonus (how many lowe rolls are ignored
#                            e.g. Fighter with 2: roll 3d10 and ignore 2 lowest
#
# =====================================================================

power_types = {'weaker': {'ability_roll': [dice['d8'], 2, 1, 0, 0],
                            'reroll_at': 4, 'hp_roll': 0},
                'normal': {'ability_roll': [dice['d6'], 4, 0, 0, 1],
                            'reroll_at': 4, 'hp_roll': 0},
                'stronger': {'ability_roll': [dice['d4'], 3, 2, 0, 0],
                            'reroll_at': 4, 'hp_roll': 1},
                'legendary': {'ability_roll': [dice['d6'], 6, 0, 0, 3],
                            'reroll_at': 10, 'hp_roll': 2}
                }

# Define tables =======================================================
#
#   BAB_tables              define on which levels classes get a bonus
#                           on their base attack bonus on levels 1-20
#                           and 21-40 (epic). Warriors use 'high' table
#                           clerics, druids and rogues 'medium' and
#                           arcane spellcasters 'low'.
#
#   save_increases          define on which level classes get a bonus
#                            on their saving throw on levels 1-20 and
#                           on levels 21-40 (epic).
#
#   save_tables             define which saves are primary for each class
#
#   spells_known            number of known spells for bard and sorcerer
#   C_spells_per_day        default spell level progression for class C
#   spells_per_day          number of spells character can cast per day
#
# =======================================================================

BAB_tables = {
    'high': [1]*20,
    'medium': [0, 1, 1, 1]*5,
    'low': [0, 1]*10,
    'epic': [1, 0]*10}

save_increases = {
    'secondary': [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
    'primary': [2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    'epic': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]}

save_tables = {'warrior': {'fort': save_increases['primary'],
                           'ref': save_increases['secondary'],
                           'will': save_increases['secondary']},
               'bard': {'fort': save_increases['secondary'],
                           'ref': save_increases['primary'],
                           'will': save_increases['primary']},
               'divine': {'fort': save_increases['primary'],
                           'ref': save_increases['secondary'],
                           'will': save_increases['primary']},
               'monk': {'fort': save_increases['primary'],
                           'ref': save_increases['primary'],
                           'will': save_increases['primary']},
               'ranger': {'fort': save_increases['primary'],
                           'ref': save_increases['primary'],
                           'will': save_increases['secondary']},
               'rogue': {'fort': save_increases['secondary'],
                           'ref': save_increases['primary'],
                           'will': save_increases['secondary']},
               'arcane': {'fort': save_increases['secondary'],
                           'ref': save_increases['secondary'],
                           'will': save_increases['primary']},
               'commoner': {'fort': save_increases['secondary'],
                           'ref': save_increases['secondary'],
                           'will': save_increases['secondary']},
               'epic': {'fort': save_increases['epic'],
                           'ref': save_increases['epic'],
                           'will': save_increases['epic']}}

spells_known = {
    'bard':
        {0: [4, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
         1: [None] + [2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5],
         2: [None]*3 + [2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5],
         3: [None]*6 + [2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5],
         4: [None]*9 + [2, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5],
         5: [None]*12 + [2, 3, 3, 4, 4, 4, 5, 5],
         6: [None]*15 + [2, 3, 3, 4, 4]},
    'sorcerer':
        {0: [4, 5, 6, 6, 7, 7, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
         1: [2, 2, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
         2: [None]*3 + [1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
         3: [None]*5 + [1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
         4: [None]*7 + [1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4],
         5: [None]*9 + [1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3],
         6: [None]*11 + [1, 2, 2, 3, 3, 3, 3, 3, 3],
         7: [None]*13 + [1, 2, 2, 3, 3, 3, 3],
         8: [None]*15 + [1, 2, 2, 3, 3],
         9: [None]*17 + [1, 2, 3]}}

cleric_spells_per_day = [
    1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
wizard_spells_per_day = [
    1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
sorcerer_spells_per_day = [
    3, 4, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]

spells_per_day = {
    'adept':
        {0: [3]*20,
        1: [1, 1, 2, 2, 2, 2] + [3]*14,
        2: [None]*3 + [0, 1, 1, 2, 2, 2, 2] + [3]*10,
        3: [None]*7 + [0, 1, 1, 2, 2, 2, 2] + [3]*6,
        4: [None]*11 + [0, 1, 1, 2, 2, 2, 2] + [3]*2,
        5: [None]*15 + [0, 1, 1, 2, 2]},
    'bard':
        {0: [2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4],
        1: [None] + [0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4],
        2: [None]*3 + [0, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4],
        3: [None]*6 + [0, 1, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4],
        4: [None]*9 + [0, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4],
        5: [None]*12 + [0, 1, 2, 2, 3, 3, 4, 4],
        6: [None]*15 + [0, 1, 2, 3, 4]},
    'ranger':
        {0: [None]*3 + [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3],
        1: [None]*7 + [0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3],
        2: [None]*10 + [0, 1, 1, 1, 1, 1, 2, 2, 3, 3],
        3: [None]*13 + [0, 1, 1, 1, 1, 2, 3]},
    'paladin': list(),
    'cleric':
        {0: [3, 4, 4, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        1: cleric_spells_per_day,
        2: [None]*2 + cleric_spells_per_day[0:18],
        3: [None]*4 + cleric_spells_per_day[0:16],
        4: [None]*6 + cleric_spells_per_day[0:14],
        5: [None]*8 + cleric_spells_per_day[0:12],
        6: [None]*10 + cleric_spells_per_day[0:10],
        7: [None]*12 + cleric_spells_per_day[0:8],
        8: [None]*14 + cleric_spells_per_day[0:6],
        9: [None]*16 + [1, 2, 3, 4]},
    'druid': list(),
    'wizard':
        {0: [3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        1: wizard_spells_per_day,
        2: [None]*2 + wizard_spells_per_day[0:18],
        3: [None]*4 + wizard_spells_per_day[0:16],
        4: [None]*6 + wizard_spells_per_day[0:14],
        5: [None]*8 + wizard_spells_per_day[0:12],
        6: [None]*10 + wizard_spells_per_day[0:10],
        7: [None]*12 + wizard_spells_per_day[0:8],
        8: [None]*14 + wizard_spells_per_day[0:6],
        9: [None]*16 + [1, 2, 3, 4]},
    'sorcerer':
        {0: [5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        1: sorcerer_spells_per_day,
        2: [None]*3 + sorcerer_spells_per_day[0:17],
        3: [None]*5 + sorcerer_spells_per_day[0:15],
        4: [None]*7 + sorcerer_spells_per_day[0:13],
        5: [None]*9 + sorcerer_spells_per_day[0:11],
        6: [None]*11 + sorcerer_spells_per_day[0:9],
        7: [None]*13 + sorcerer_spells_per_day[0:7],
        8: [None]*15 + sorcerer_spells_per_day[0:5],
        9: [None]*17 + [3, 4, 6]}}

spells_per_day['paladin'] = spells_per_day['ranger']
spells_per_day['druid'] = spells_per_day['cleric']


'''
for x in spells_per_day['ranger']:
    print spells_per_day['ranger'][x]
'''

# Define racial specifications ============================================
#
#   aging_modifiers                 age penalties and bonuses on ability
#                                   scores
#
#   eye_colors/hair_colors          define common eye/hair colors
#
#   race_specs
#       'adult/middle/old/venerable'    number of years race reaches
#                                       this age type
#       'simple/moderate/complex'       age modifier for adults [rolls, dice]
#       'ability_adjustments'             penalties and bonuses applied on
#                                       each ability score
#       'level_adjustment'              how many levels behind selected race
#                                       will develop
#       'speed'                         character speed in feet
#       'size'                          creature size
#                                       [small, medium, large]
#       'skin/eyes/hair'                physical appearance
#        'restricted_alignments'            restricted alignments
#
# =========================================================================

ac_size_adj = {'small': 1, 'medium': 0, 'large': -1}
grapple_adj = {'small': -4, 'medium': 0, 'large': 4}
attack_adj = {'small': 1, 'medium': 0, 'large': -1}

aging_modifiers = {
    'adult':
   {'str': 0, 'dex': 0, 'con': 0, 'wis': 0, 'int': 0, 'cha': 0},
   'middle':
   {'str': -1, 'dex': -1, 'con': -1, 'wis': 1, 'int': 1, 'cha': 1},
   'old':
   {'str': -3, 'dex': -3, 'con': -3, 'wis': 2, 'int': 2, 'cha': 2},
   'venerable':
   {'str': -6, 'dex': -6, 'con': -6, 'wis': 3, 'int': 3, 'cha': 3}
    }

eye_colors = {
    'default': ['green', 'blue', 'brown', 'gray'],
    'elf': ['green', 'light green', 'deep green', 'blue', 'emerald', 'jade']
    }

hair_colors = {
    'default': ['black', 'brown', 'dark', 'blonde', 'red', 'mixed', 'grayish'],
    'elf': ['black', 'brown', 'dark', 'mixed'],
    'dark': ['dark', 'black', 'dark grey', 'dark brown'],
    'old': ['light gray', 'white', 'grayish', 'white-gray']
    }

# Racial bonus feats

human_bonuses = {
    'racial_feat':
        {'Quick to learn': 'Gains one extra feat and extra skill points'}
        }

elf_bonuses = {
    'racial_feat':
        {'Immunities': 'Immune to sleep spells',
        'Skill bonus': '(+2 to listen, search, spot)'},
    'vision': 'Low-light',
    'skill_bonus': {'Listen': 2, 'Search': 2, 'Spot': 2},
    'special_save_bonus': {'general': {'vs. ench.': 2}},
        }

halfelf_bonuses = {
    'racial_feat':
        {'Immunities': 'Immune to sleep spells',
        'Skill bonus': '(+1 to listen, search, spot, '\
                        'gather information, diplomacy)'},
    'vision': 'Low-light',
    'skill_bonus': {'Listen': 1, 'Search': 1, 'Spot': 1,
                    'Gather Information': 2, 'Diplomacy': 2},
    'special_save_bonus': {'general': {'vs. ench.': 2}},
        }

halforc_bonuses = {'vision': 'Darkvision (60 ft)'}

halfling_bonuses = {
    'racial_feat':
        {'Ranged bonus': '+1 attack with slings and throwing weapons',
        'Skill bonus': '(+2 to Climb/listen/jump/move silently)'},
    'skill_bonus': {'Climb': 2, 'Listen': 2, 'Jump': 2, 'Move Silently': 2},
    'saves': {'fort': 1, 'ref': 1, 'will': 1},
    'special_save_bonus': {'general': {'vs. fear': 2}},
        }

dwarf_bonuses = {
    'racial_feat': {
        'Stonecunning': '+2 to search checks on unusual stonework',
        'Stability': '+4 to checks if tripped/bull rushed',
        'Attack bonus':
            '+1 to attack rolls vs. orcs, half-orcs and goblinoids',
        'Skill bonus': '(+2 to Appraise/Craft (metal items)'},
    'vision': 'darkvision (60 ft, monochrome)',
    'special_save_bonus': {'fort': {'vs. poison': 2},
                            'general': {'vs. spells': 2}},
    'special_armor_bonus': {'dodge': {'vs. giant types' :4}},
    'skill_bonus': {'Appraise': 2, 'Craft (metals)': 2}
    }

gnome_bonuses = {
    'racial_feat':
        {'Attack bonus': '+1 to attack rolls vs. goblinoids and kobolds',
        'Skill bonus': '(+2 to Listen, Craft (alchemy))',
        'Spell-like abilities':
            'Speak with animals. If charisma over 10: dancing lights, '\
                                'ghost sound, prestidigitation (1/day)',
        'Illusionist':
            "+1 to the difficulty class for all saving throws "\
                "against illusion spells cast by gnomes"},
    'vision': 'low-light',
    'special_armor_bonus': {'dodge': {'vs. giant types': 4}},
    'skill_bonus': {'Listen': 2, 'Craft (alchemy)': 2},
    'special_save_bonus': {'general': {'vs. illusions': 2}}
    }

svirfneblin_bonuses = {
    'racial_feat':
        {'Stonecunning': '+2 to search checks on unusual stonework',
        'Non-detection': 'Continuous non-detection',
        'Save bonus': '(Racial +2 to all saves)',
        'Attack bonus': '+1 to attack rolls vs. goblinoids and kobolds',
        'Skill bonus': '(+2 to Listen, Hide, Craft (alchemy))',
        'Spell-like abilities':
            'Blindness/deafness, blur, disguise self (1/day)',
        'Illusionist':
            "+1 to the difficulty class for all saving throws "\
                "against illusion spells cast by svirfneblins" },
    'vision': 'darkvision (120 ft), low-light',
    'spell_resistance': 11,
    'saves': {'fort': 2, 'ref': 2, 'will': 2},
    'special_armor_bonus': {'dodge': {'vs. creatures':4}},
    'skill_bonus': {'Listen': 2, 'Craft (alchemy)': 2, 'Hide': 2}
    }

orc_bonuses = {
    'racial_feat': {
        'Light sensitivity': 'Dazzled in bright sunlight'},
    'vision': 'Darkvision (60 ft)'}

duergar_bonuses = {
    'racial_feat': {
        'Stonecunning': '+2 to search checks on unusual stonework',
        'Stability': '+4 to checks if tripped/bull rushed',
        'Immunities': 'Immune to poison, paralysis and phantasms',
        'Spell-like abilities':
            'Enlarge person, invisibility (1/day)',
        'Light sensitivity': 'Dazzled in bright sunlight',
        'Attack bonus':
            '+1 to attack rolls vs. orcs, half-orcs and goblinoids',
        'Skill bonus': '(+2 to Appraise/Craft (metal items), '\
                        '+1 Listen, Spot, +4 Move Silently)'},
    'vision': 'darkvision (120 ft)',
    'special_save_bonus': {'general': {'vs. spells':2}},
    'special_armor_bonus': {'dodge': {'vs. giant types' :4}},
    'skill_bonus': {'Appraise': 2, 'Craft (metals)': 2, 'Listen': 1, 'Spot': 1,
                    'Move Silently': 4}
    }

halfogre_bonuses = {
    'racial_feat': {'Powerful build': '+4 to bull rush, overrun,'\
                    ' (grapple). May yield large weapons'},
    'grapple': 4,
    'class_skills': ['Intimidate'],
    'size_for_items': 'large',
    'vision': 'darkvision (60 ft.)',
    'armor': {'natural': 4}
            }

drow_bonuses = {
    'racial_feat': {
        'Immunities': 'Immune to sleep',
        'Light blindness': 'Blinded for 1 round in bright sunlight'\
                            ' and remains dazzled afterwards'},
    'special_save_bonus': {'general': {'vs. ench.': 4}},
    'spell_resistance': 11,
    'vision': 'darkvision (120 ft)',
    'skill_bonus': {'Search': 2, 'Listen': 2, 'Spot': 2}
            }

ogre_bonuses = {
    'racial_feat': {'Powerful build': '+4 to bull rush, overrun,'\
                    ' (grapple). May yield large weapons',
                    'Giant': '(+3 BAB, 8 HD at first four levels,'\
                    ' +4 FORT, +1 REF/WILL)'},
    'grapple': 4,
    'bab': 3,
    'class_skills': ['Climb', 'Listen', 'Spot'],
    'size_for_items': 'large',
    'vision': 'darkvision (60 ft.)',
    'armor': {'natural': 5},
    'saves': {'fort': 4, 'ref': 1, 'will': 1},
    'HD': [dice['d8'], 4] # [HD, how many levels this is used]
            }

# Racial general variables

race_specs = {
    'human':
        {'adult': 15, 'middle': 35, 'old': 53, 'venerable': 70,
        'simple': [1, dice['d4']],
         'moderate': [1, dice['d6']], 'complex': [2, dice['d6']],
        'ability_adjustments':
        {'str': 0, 'dex': 0, 'con': 0, 'wis': 0, 'int': 0, 'cha': 0},
        'level_adjustment': 0, 'speed': 30, 'size': 'medium',
        'skin': ['pale', 'tanned', 'lightly tanned', 'dark', 'brown'],
        'eyes': eye_colors['default'], 'hair': hair_colors['default'],
        'restricted_alignments': list(), 'type': 'humanoid (human)',
        'languages': ['common'],
        'bonuses': human_bonuses},
    'elf':
        {'adult': 110, 'middle': 175, 'old': 263, 'venerable': 350,
        'simple': [4, dice['d6']],
        'moderate': [6, dice['d6']], 'complex': [10, dice['d6']],
        'ability_adjustments':
        {'str': 0, 'dex': 2, 'con': -2, 'wis': 0, 'int': 0, 'cha': 0},
        'level_adjustment': 0, 'speed': 30, 'size': 'medium',
        'skin': ['pale', 'lightly tanned'],
        'eyes': eye_colors['elf'], 'hair': hair_colors['elf'],
        'restricted_alignments': list(), 'type': 'humanoid (elf)',
        'languages': ['common', 'elven'],
        'bonuses': elf_bonuses},
    'half-elf':
        {'adult': 20, 'middle': 62, 'old': 93, 'venerable': 125,
        'simple': [1, dice['d6']],
        'moderate': [1, dice['d6']], 'complex': [3, dice['d6']],
        'ability_adjustments':
        {'str': 0, 'dex': 0, 'con': 0, 'wis': 0, 'int': 0, 'cha': 0},
        'level_adjustment': 0, 'speed': 30, 'size': 'medium',
        'skin': ['pale', 'tanned', 'lightly tanned', 'light brown'],
        'eyes': eye_colors['elf'] + eye_colors['default'],
        'hair': hair_colors['elf'] + eye_colors['default'],
        'restricted_alignments': list(), 'type': 'humanoid (elf)',
        'languages': ['common', 'elven'],
        'bonuses': halfelf_bonuses},
    'half-orc':
        {'adult': 14, 'middle': 30, 'old': 45, 'venerable': 60,
        'simple': [1, dice['d4']],
        'moderate': [1, dice['d6']], 'complex': [2, dice['d6']],
        'ability_adjustments':
        {'str': 2, 'dex': 0, 'con': 0, 'wis': 0, 'int': -2, 'cha': -2},
        'level_adjustment': 0, 'speed': 30, 'size': 'medium',
        'skin': ['dark', 'grayish', 'gray', 'olive', 'brownish'],
        'eyes': ['black', 'gray', 'dark green', 'red', 'dark blue'],
        'hair': hair_colors['dark'],
        'restricted_alignments': list(), 'type': 'humanoid (orc)',
        'languages': ['common', 'orc'],
        'bonuses': halforc_bonuses},
    'halfling':
        {'adult': 20, 'middle': 50, 'old': 75, 'venerable': 100,
        'simple': [2, dice['d4']],
        'moderate': [3, dice['d6']], 'complex': [4, dice['d6']],
        'ability_adjustments':
        {'str': -2, 'dex': 2, 'con': 0, 'wis': 0, 'int': 0, 'cha': 0},
        'level_adjustment': 0, 'speed': 20, 'size': 'small',
        'skin': ['dark tan', 'ruddy', 'light brown', 'tanned'],
        'eyes': ['black', 'dark brown'], 'hair': hair_colors['dark'],
        'restricted_alignments': list(), 'type': 'humanoid (halfling)',
        'languages': ['common', 'halfling'],
        'bonuses': halfling_bonuses},
    'dwarf':
        {'adult': 40, 'middle': 125, 'old': 188, 'venerable': 250,
        'simple': [3, dice['d6']],
        'moderate': [5, dice['d6']], 'complex': [7, dice['d6']],
        'ability_adjustments':
        {'str': 0, 'dex': 0, 'con': 2, 'wis': 0, 'int': 0, 'cha': -2},
        'level_adjustment': 0, 'speed': 20, 'size': 'medium',
        'skin': ['dark tan', 'light brown', 'tanned'],
        'eyes': ['brown', 'dark', 'dark brown'],
        'hair': hair_colors['dark'],
        'restricted_alignments': list(), 'type': 'humanoid (dwarf)',
        'languages': ['common', 'dwarven'],
        'bonuses': dwarf_bonuses},
    'gnome':
        {'adult': 40, 'middle': 100, 'old': 150, 'venerable': 200,
        'simple': [4, dice['d6']],
        'moderate': [6, dice['d6']], 'complex': [9, dice['d6']],
        'ability_adjustments':
        {'str': -2, 'dex': 0, 'con': 2, 'wis': 0, 'int': 0, 'cha': 0},
        'level_adjustment': 0, 'speed': 20, 'size': 'small',
        'skin': ['dark tan', 'woody brown', 'tanned'],
        'eyes': ['deep blue', 'light blue', 'teal', 'blue'],
        'hair': hair_colors['dark'],
        'restricted_alignments': list(), 'type': 'humanoid (gnome)',
        'languages': ['common', 'gnome'],
        'bonuses': gnome_bonuses},
    'drow':
        {'adult': 110, 'middle': 175, 'old': 263, 'venerable': 350,
        'simple': [4, dice['d6']],
        'moderate': [6, dice['d6']], 'complex': [10, dice['d6']],
        'ability_adjustments':
        {'str': 0, 'dex': 2, 'con': -2, 'wis': 0, 'int': 0, 'cha': 2},
        'level_adjustment': 2, 'speed': 30, 'size': 'medium',
        'skin': ['dark gray', 'gray', 'dark blue', 'violet'],
        'eyes': ['red', 'lavender', 'blue', 'purple', 'amber'],
        'hair': ['white', 'light gray'],
        'restricted_alignments': alignment_types['good_neutral'],
        'type': 'humanoid (elf)',
        'languages': ['common', 'elven', 'undercommon'],
        'bonuses': drow_bonuses},
    'duergar':
        {'adult': 40, 'middle': 125, 'old': 188, 'venerable': 250,
        'simple': [3, dice['d6']],
        'moderate': [5, dice['d6']], 'complex': [7, dice['d6']],
        'ability_adjustments':
        {'str': 0, 'dex': 0, 'con': 2, 'wis': 0, 'int': 0, 'cha': -4},
        'level_adjustment': 1, 'speed': 20, 'size': 'medium',
        'skin': ['dark gray', 'gray', 'charcoal'],
        'eyes': ['dull black', 'black'],
        'hair': hair_colors['default'] + hair_colors['dark'],
        'restricted_alignments': alignment_types['good']
                            + [alignments[1]] + [alignments[4]],
        'type': 'humanoid (dwarf)',
        'languages': ['common', 'dwarven', 'undercommon'],
        'bonuses': duergar_bonuses
        },
    'svirfneblin':
        {'adult': 40, 'middle': 100, 'old': 158, 'venerable': 200,
        'simple': [4, dice['d6']],
        'moderate': [6, dice['d6']], 'complex': [9, dice['d6']],
        'ability_adjustments':
        {'str': 0, 'dex': 2, 'con': 0, 'wis': 2, 'int': 0, 'cha': -4},
        'level_adjustment': 3, 'speed': 20, 'size': 'small',
        'skin': ['dark gray', 'gray', 'charcoal', 'very dark'],
        'eyes': ['dull black', 'black', 'dark brown'],
        'hair': ['gray', 'light gray', 'white'],
        'restricted_alignments': alignment_types['nonneutral'],
        'type': 'humanoid (gnome)',
        'languages': ['common', 'gnome', 'undercommon'],
        'bonuses': svirfneblin_bonuses},
    'half-ogre':
        {'adult': 15, 'middle': 32, 'old': 49, 'venerable': 65,
        'simple': [1, dice['d4']],
        'moderate': [1, dice['d6']], 'complex': [1, dice['d10']],
        'ability_adjustments':
        {'str': 6, 'dex': 0, 'con': 2, 'wis': 0, 'int': -2, 'cha': -2},
        'level_adjustment': 2, 'speed': 30, 'size': 'medium',
        'skin': ['brown', 'dark gray', 'dull yellow', 'gray-greenish'],
        'eyes': eye_colors['default'] + ['white'],
        'hair': hair_colors['dark'],
        'restricted_alignments': list(), 'type': 'humanoid (giant)',
        'languages': ['common', 'giant'],
        'bonuses': halfogre_bonuses},
    'orc':
        {'adult': 12, 'middle': 20, 'old': 30, 'venerable': 40,
        'simple': [1, dice['d4']],
        'moderate': [1, dice['d6']], 'complex': [2, dice['d6']],
        'ability_adjustments':
        {'str': 4, 'dex': 0, 'con': 0, 'wis': -2, 'int': -2, 'cha': -2},
        'level_adjustment': 0, 'speed': 30, 'size': 'medium',
        'skin': ['dark', 'grayish', 'gray'],
        'eyes': ['black', 'red', 'dark orange'],
        'hair': hair_colors['dark'],
        'restricted_alignments': alignment_types['lawful']
                                + alignment_types['good'],
        'type': 'humanoid (orc)',
        'languages': ['common', 'giant'],
        'bonuses': orc_bonuses},
    'ogre':
        {'adult': 16, 'middle': 38, 'old': 65, 'venerable': 80,
        'simple': [1, dice['d4']],
        'moderate': [1, dice['d6']], 'complex': [1, dice['d10']],
        'ability_adjustments':
        {'str': 10, 'dex': -2, 'con': 4, 'wis': 0, 'int': -4, 'cha': -4},
        'level_adjustment': 2, 'speed': 40, 'size': 'large',
        'skin': ['brown', 'dark gray', 'dull yellow', 'gray-greenish'],
        'eyes': eye_colors['default'] + ['white'],
        'hair': hair_colors['dark'],
        'restricted_alignments': alignments[0:8],
        'type': 'humanoid (giant)',
        'languages': ['giant', 'common'],
        'bonuses': ogre_bonuses}
        }

# Define racial subgroups =================================================
#
#   'any'              any race
#   'nonexotic'        non-exotic races presented in the Players Handbook
#
# =========================================================================

races = {'any': ['human', 'elf', 'half-elf', 'halfling', 'gnome', 'dwarf',
                 'half-orc', 'drow', 'duergar', 'svirfneblin', 'half-ogre',
                 'orc', 'ogre'],
        'non-exotic': ['human', 'elf', 'half-elf',
                       'halfling', 'gnome', 'dwarf', 'half-orc'],
        'monstrous': ['orc', 'half-ogre', 'ogre']}

# Define racial pysical attributes ========================================
#
#   'base_height'          [feet, inches]
#   'height_mod'           [number of rolls, dice]
#   'base_weight'          [pounds]
#   'height_mod'           [number of rolls, dice]
#
# =========================================================================

sizes = {'human':
         {'male': {'base_height': [4, 10], 'height_mod': [2, dice['d10']],
                       'base_weight': 120, 'weight_mod': [2, dice['d4']]},
          'female': {'base_height': [4, 10], 'height_mod': [2, dice['d10']],
                     'base_weight': 120, 'weight_mod': [2, dice['d4']]}},
         'elf':
         {'male': {'base_height': [4, 5], 'height_mod': [2, dice['d6']],
                   'base_weight': 85, 'weight_mod': [1, dice['d6']]},
          'female': {'base_height': [4, 5], 'height_mod': [2, dice['d6']],
                     'base_weight': 80, 'weight_mod': [1, dice['d6']]}},
         'dwarf':
         {'male': {'base_height': [3, 9], 'height_mod': [2, dice['d4']],
                   'base_weight': 130, 'weight_mod': [2, dice['d6']]},
          'female': {'base_height': [3, 7], 'height_mod': [2, dice['d4']],
                    'base_weight': 100, 'weight_mod': [2, dice['d6']]}},
         'gnome':
         {'male': {'base_height': [3, 0], 'height_mod': [2, dice['d4']],
                   'base_weight': 40, 'weight_mod': [1, 1]},
          'female': {'base_height': [2, 10], 'height_mod': [2, dice['d4']],
                     'base_weight': 35, 'weight_mod': [1, 1]}},
         'half-elf':
         {'male': {'base_height': [4, 7], 'height_mod': [2, dice['d8']],
                   'base_weight': 100, 'weight_mod': [2, dice['d4']]},
          'female': {'base_height': [4, 5], 'height_mod': [2, dice['d8']],
                     'base_weight': 80, 'weight_mod': [2, dice['d4']]}},
         'half-orc':
         {'male': {'base_height': [4, 10], 'height_mod': [2, dice['d10']],
                   'base_weight': 130, 'weight_mod': [2, dice['d4']]},
          'female': {'base_height': [4, 4], 'height_mod': [2, dice['d10']],
                     'base_weight': 90, 'weight_mod': [2, dice['d4']]}},
         'halfling':
         {'male': {'base_height': [2, 8], 'height_mod': [2, dice['d4']],
                   'base_weight': 30, 'weight_mod': [1, 1]},
          'female': {'base_height': [2, 6], 'height_mod': [2, dice['d4']],
                     'base_weight': 25, 'weight_mod': [1, 1]}},
         'half-ogre':
         {'male': {'base_height': [7, 6], 'height_mod': [2, dice['d6']],
                   'base_weight': 250, 'weight_mod': [7, 1]},
          'female': {'base_height': [6, 10], 'height_mod': [2, dice['d6']],
                     'base_weight': 180, 'weight_mod': [7, 1]}},
         'drow':
         {'male': {'base_height': [4, 4], 'height_mod': [2, dice['d6']],
                   'base_weight': 85, 'weight_mod': [1, dice['d6']]},
          'female': {'base_height': [4, 6], 'height_mod': [2, dice['d6']],
                     'base_weight': 80, 'weight_mod': [1, dice['d6']]}},
         'duergar':
         {'male': {'base_height': [3, 9], 'height_mod': [2, dice['d4']],
                   'base_weight': 110, 'weight_mod': [2, dice['d4']]},
          'female': {'base_height': [3, 7], 'height_mod': [2, dice['d4']],
                     'base_weight': 80, 'weight_mod': [2, dice['d4']]}},
         'svirfneblin':
         {'male': {'base_height': [3, 0], 'height_mod': [2, dice['d4']],
                   'base_weight': 40, 'weight_mod': [1, 1]},
          'female': {'base_height': [2, 10], 'height_mod': [2, dice['d4']],
                     'base_weight': 35, 'weight_mod': [1, 1]}},
         'orc':
         {'male': {'base_height': [5, 1], 'height_mod': [2, dice['d12']],
                   'base_weight': 160, 'weight_mod': [7, 1]},
          'female': {'base_height': [4, 9], 'height_mod': [2, dice['d12']],
                     'base_weight': 120, 'weight_mod': [7, 1]}},
         'ogre':
         {'male': {'base_height': [9, 2], 'height_mod': [1, dice['d8']],
                   'base_weight': 600, 'weight_mod': [7, 1]},
          'female': {'base_height': [9, 0], 'height_mod': [1, dice['d8']],
                     'base_weight': 500, 'weight_mod': [7, 1]}},
         }

# =====================================================================
# Define class specifications =========================================
#
#  classes                     class subsets/groups
#
#  class_specifications
#      'age'                   starting age for the class
#      'HD'                    hit dice [dice]
#      'bab'                   base attack bonus table for the class
#      'saves'                 saving throw developmnet tables for the
#                              class
#      'ability_priorization'  which abilities are the most important
#                              for the class (most important first)
#       ´skill_mod´            skill modifier:
#                              (skill_mod + int_mod) [x 4])
#       'restricted_alignments'   restricted alignments
#       'restricted_multi'        restricted multi-classes
#
#    Note that multi-classing wizards to sorcerers or mixing civilians with
#    regular classes is no prohibited by the core rules.
#
#    Ability priorization will be recalculated if multi-classed
#    by forming a matrix from class specific priorization tables and
#    finding the optimal path. E.g. when multi-classing from Fighter
#    to Wizard:
#
#            Fighter:     STR    CON     DEX     WIS     INT     CHA
#                          |   /  |   __________/   \____
#                          v  /   v  /                    \
#            Wizard:      INT    DEX     CON     WIS     CHA     STR
#
#        Thus new priority order would be:
#
#            STR -> INT -> CON -> DEX -> WIS -> CHA
#
# =====================================================================

classes = {'any': ['fighter', 'paladin', 'ranger', 'barbarian', 'monk', 'bard',
                   'rogue', 'wizard', 'sorcerer', 'druid', 'cleric'],
           'warrior': ['fighter', 'paladin', 'ranger', 'barbarian', 'monk'],
           'standard': ['fighter', 'paladin', 'ranger', 'barbarian', 'monk',
                           'bard', 'rogue', 'wizard', 'sorcerer', 'druid',
                        'cleric'], # Do not add more classes here
           'arcane': ['sorcerer', 'wizard'],
           'armor_user': ['paladin', 'fighter', 'cleric', 'warrior'],
           'spellcaster': ['sorcerer', 'wizard', 'adept', 'druid'],
           'divine': ['druid', 'cleric'],
           'civilian': ['commoner', 'aristocrat', 'expert', 'adept', 'warrior']}

class_specs = {
    'fighter': {
        'age': 'moderate', 'HD': dice['d10'], 'bab': BAB_tables['high'],
        'saves': save_tables['warrior'],
        'ability_priorization': ['str', 'con', 'dex', 'wis', 'int', 'cha'],
        'skill_mod': 2,
        'restricted_alignments': list(),
        'restricted_multi': classes['civilian'],
        'bonus_feats': [1] + [x for x in range(2,41,2)]},
    'barbarian': {
        'age': 'simple', 'HD': dice['d12'], 'bab': BAB_tables['high'],
        'saves': save_tables['warrior'],
        'ability_priorization': ['str', 'con', 'dex', 'wis', 'int', 'cha'],
        'skill_mod': 4,
        'restricted_alignments': alignment_types['lawful'],
        'restricted_multi': classes['civilian'],
        'bonus_feats': [24, 28, 32, 36, 40]},
    'bard': {
        'age': 'moderate', 'HD': dice['d6'], 'bab': BAB_tables['medium'],
        'saves': save_tables['bard'],
        'ability_priorization': ['cha', 'dex', 'int', 'str', 'con', 'wis'],
        'skill_mod': 6,
        'restricted_alignments': alignment_types['lawful'],
        'restricted_multi': classes['civilian'],
        'bonus_feats': [x for x in range(23,40,3)]},
    'cleric': {
        'age': 'complex', 'HD': dice['d8'], 'bab': BAB_tables['medium'],
        'saves': save_tables['divine'],
        'ability_priorization': ['wis', 'str', 'con', 'cha', 'int', 'dex'],
        'skill_mod': 2,
        'restricted_alignments': list(),
        'restricted_multi': classes['civilian'],
        'bonus_feats': [x for x in range(23,40,3)]},
    'druid': {
        'age': 'complex', 'HD': dice['d8'], 'bab': BAB_tables['medium'],
        'saves': save_tables['divine'],
        'ability_priorization': ['wis', 'cha', 'con', 'str', 'int', 'dex'],
        'skill_mod': 4,
        'restricted_alignments': alignment_types['nonneutral'],
        'restricted_multi': classes['civilian'],
        'bonus_feats': [24, 28, 32, 36, 40]},
    'monk': {
        'age': 'complex', 'HD': dice['d8'], 'bab': BAB_tables['high'],
        'saves': save_tables['monk'],
        'ability_priorization': ['str', 'con', 'dex', 'wis', 'int', 'cha'],
        'skill_mod': 4,
        'restricted_alignments': alignment_types['nonlawful'],
        'restricted_multi': classes['civilian'],
        'bonus_feats': [1, 2, 6, 25, 30, 35, 40]},
    'paladin': {
        'age': 'moderate', 'HD': dice['d10'], 'bab': BAB_tables['high'],
        'saves': save_tables['warrior'],
        'ability_priorization': ['str', 'con', 'cha', 'wis', 'int', 'dex'],
        'skill_mod': 2,
        'restricted_alignments': alignment_types['nonlawfulgood'],
        'restricted_multi': classes['civilian'],
        'bonus_feats': [x for x in range(23,40,3)]},
    'ranger': {
        'age': 'moderate', 'HD': dice['d10'], 'bab': BAB_tables['high'],
        'saves': save_tables['ranger'],
        'ability_priorization': ['str', 'dex', 'con', 'wis', 'cha', 'int'],
        'skill_mod': 6,
        'restricted_alignments': list(),
        'restricted_multi': classes['civilian'],
        'bonus_feats': [x for x in range(23,40,3)]},
    'sorcerer': {
        'age': 'simple', 'HD': dice['d4'], 'bab': BAB_tables['low'],
        'saves': save_tables['arcane'],
        'ability_priorization': ['cha', 'int', 'dex', 'con', 'str', 'wis'],
        'skill_mod': 2,
        'restricted_alignments': list(),
        'restricted_multi': ['wizard'],
        'bonus_feats': [x for x in range(23,40,3)]},
    'wizard': {
        'age': 'complex', 'HD': dice['d4'], 'bab': BAB_tables['low'],
        'saves': save_tables['arcane'],
        'ability_priorization': ['int', 'dex', 'con', 'wis', 'cha', 'str'],
        'skill_mod': 2,
        'restricted_alignments': list(),
        'restricted_multi': ['sorcerer'],
        'bonus_feats': [5, 10, 15, 20] + [x for x in range(23,40,3)]},
    'rogue': {
        'age': 'simple', 'HD': dice['d6'], 'bab': BAB_tables['medium'],
        'saves': save_tables['rogue'],
        'ability_priorization': ['dex', 'int', 'str', 'cha', 'con', 'wis'],
        'skill_mod': 8,
        'restricted_alignments': alignment_types['lawful'],
        'restricted_multi': classes['civilian'],
        'bonus_feats': [24, 28, 32, 36, 40]},
    'adept': {
        'age': 'moderate', 'HD': dice['d8'], 'bab': BAB_tables['medium'],
        'saves': save_tables['arcane'],
        'ability_priorization': ['wis', 'str', 'con', 'cha', 'int', 'dex'],
        'skill_mod': 2,
        'restricted_alignments': list(),
        'restricted_multi': classes['any'],
        'bonus_feats': []},
    'commoner': {
        'age': 'simple', 'HD': dice['d4'], 'bab': BAB_tables['low'],
        'saves': save_tables['commoner'],
        'ability_priorization': ['wis', 'str', 'con', 'cha', 'int', 'dex'],
        'skill_mod': 2,
        'restricted_alignments': list(),
        'restricted_multi': classes['any'],
        'bonus_feats': []},
    'aristocrat': {
        'age': 'moderate', 'HD': dice['d8'], 'bab': BAB_tables['medium'],
        'saves': save_tables['arcane'],
        'ability_priorization': ['int', 'cha', 'wis', 'con', 'str', 'dex'],
        'skill_mod': 4,
        'restricted_alignments': list(),
        'restricted_multi': classes['any'],
        'bonus_feats': []},
    'warrior': {
        'age': 'simple', 'HD': dice['d8'], 'bab': BAB_tables['high'],
        'saves': save_tables['warrior'],
        'ability_priorization': ['str', 'con', 'dex', 'wis', 'int', 'cha'],
        'skill_mod': 2,
        'restricted_alignments': list(),
        'restricted_multi': classes['any'],
        'bonus_feats': []},
    'expert': {
        'age': 'moderate', 'HD': dice['d6'], 'bab': BAB_tables['medium'],
        'saves': save_tables['arcane'],
        'ability_priorization': ['int', 'dex', 'wis', 'str', 'cha', 'con'],
        'skill_mod': 6,
        'restricted_alignments': list(),
        'restricted_multi': classes['any'],
        'bonus_feats': []}}

# =====================================================================
# Define Skills =======================================================
#
#    ´bonus_skills´    Define races that have bonus skills:
#                    [1st level bonus, other levels]
#
#    ´skills´
#    key            skill name
#    value[0]    class skills for for sorted standard classes:
#                C = class skill, x = cross-class skill. See order
#                in ´order´
#    value[1]    can use untrained (boolean)
#    value[2]    key ability for the skill
#    value[3]    armor check penalty multiplier
#
# =====================================================================
bonus_skills = {'human': [4, 1],
                'ogre': [7, 0]}

skills = {
    'Appraise': ['xCxxxxxxCxx', True, 'int', 0],
    'Balance': ['xCxxxCxxCxx', True, 'dex', 1],
    'Bluff': ['xCxxxxxxCCx', True, 'cha', 0],
    'Climb': ['CCxxCCxCCxx', True, 'str', 1],
    'Concentration': ['xCCCxCCCxCC', True, 'con', 0],
    'Craft (alchemy)': ['CCCCCCCCCCC', True, 'int', 0],
    'Craft (metals)': ['CCCCCCCCCCC', True, 'int', 0],
    'Craft (wood/stone)': ['CCCCCCCCCCC', True, 'int', 0],
    'Craft (various)': ['CCCCCCCCCCC', True, 'int', 0],
    'Decipher Script': ['xCxxxxxxCxC', False, 'int', 0],
    'Diplomacy': ['xCCCxCCxCxx', True, 'cha', 0],
    'Disable Device': ['xxxxxxxxCxx', False, 'int', 0],
    'Disguise': ['xCxxxxxxCxx', True, 'cha', 0],
    'Escape Artist': ['xCxxxCxxCxx', True, 'dex', 1],
    'Forgery': ['xxxxxxxxCxx', True, 'int', 0],
    'Gather Information': ['xCxxxxxxCxx', True, 'cha', 0],
    'Handle Animal': ['CxxCCxCCxxx', False, 'cha', 0],
    'Heal': ['xxCCxxCCxxx', True, 'wis', 0],
    'Hide': ['xCxxxCxCCxx', True, 'dex', 1],
    'Intimidate': ['CxxxCxxxCxx', True, 'cha', 0],
    'Jump': ['CCxxCCxCCxx', True, 'str', 1],
    'Knowledge (arcana)': ['xCCxxCxxxCC', False, 'int', 0],
    'Knowledge (architecture and engineering)': ['xCxxxxxxxxC',False, 'int', 0],
    'Knowledge (dungeoneering)': ['xCxxxxxCxxC', False, 'int', 0],
    'Knowledge (geography)': ['xCxxxxxCxxC', False, 'int', 0],
    'Knowledge (history)': ['xCCxxxxxxxC', False, 'int', 0],
    'Knowledge (local)': ['xCxxxxxxCxC', False, 'int', 0],
    'Knowledge (nature)': ['xCxCxxxCxxC', False, 'int', 0],
    'Knowledge (nobility and royalty)': ['xCxxxxCxxxC', False, 'int', 0],
    'Knowledge (religion)': ['xCCxxCCxxxC', False, 'int', 0],
    'Knowledge (the planes)': ['xCCxxxxxxxC', False, 'int', 0],
    'Listen': ['CCxCxCxCCxx', True, 'wis', 0],
    'Move Silently': ['xCxxxCxCCxx', True, 'dex', 1],
    'Open Lock': ['xxxxxxxxCxx', False, 'dex', 0],
    'Perform': ['xCxxxCxxCxx', True, 'cha', 0],
    'Profession': ['xCCCxCCCCCC', False, 'wis', 0],
    'Ride': ['CxxCCxCCxxx', True, 'dex', 0],
    'Search': ['xxxxxxxCCxx', True, 'int', 0],
    'Sense Motive': ['xCxxxCCxCxx', True, 'wis', 0],
    'Sleight of Hand': ['xCxxxxxxCxx', False, 'dex', 1],
    'Speak Language': ['xCxxxxxxxxx', False, None, 0],
    'Spellcraft': ['xCCCxxxxxCC', False, 'int', 0],
    'Spot': ['xxxCxCxCCxx', True, 'wis', 0],
    'Survival': ['CxxCxxxCxxx', True, 'wis', 0],
    'Swim': ['CCxCCCxCCxx', True, 'str', 2],
    'Tumble': ['xCxxxCxxCxx', False, 'dex', 1],
    'Use Magic Device': ['xCxxxxxxCxx', False, 'cha', 0],
    'Use Rope': ['xxxxxxxCCxx', True, 'dex', 0]}

# Define dictionary for storing skill points on character creation
# Define list of skills that can be used untrained
untrained = []
skill_point_dict = {}
for key in skills.keys():
    if skills[key][1]:
        untrained.append(key)
    skill_point_dict[key] = {'ranks': 0, 'ability_mod': 0, 'misc_mod': 0}

# Group skills to ease class skill listing
knowledge = []
for key in skills.keys():
    if key.startswith('Knowledge'):
        knowledge.append(key)

craft = []
for key in skills.keys():
    if key.startswith('Craft'):
        craft.append(key)

# Generate class skill tables. To add class skills for those classes
# not represented in the 3.5 Player's Handbook, list them on ´override´.

class_skills = {}
order = sorted(classes['standard'])

for x in order:
    class_skills[x] = list()

for x in skills.keys():
    i = 0
    for s in skills[x][0]:
        if s == 'C':
            class_skills[order[i]].append(x)
        i += 1

override = {'adept': knowledge + craft + ['Concentration', 'Handle Animal',
                'Heal', 'Profession', 'Spellcraft', 'Survival'],
            'expert': skills.keys(),
            'warrior': ['Climb', 'Handle Animal', 'Intimidate', 'Jump',
                'Ride', 'Swim'],
            'aristocrat': knowledge + ['Appraise', 'Bluff', 'Diplomacy',
                'Disguise', 'Forgery', 'Gather Information', 'Handle Animal',
                'Intimidate', 'Listen', 'Perform', 'Ride', 'Sense Motive',
                'Speak Language', 'Spot', 'Swim', 'Survival'],
            'commoner': craft + ['Climb', 'Handle Animal', 'Jump', 'Listen',
                'Profession', 'Ride', 'Spot', 'Swim', 'Use Rope']}

for key in override.keys():
    class_skills[key] = override[key]
    for skill in override[key]:
        if skill not in skills.keys():
            # Debug warning for typoed skill name
            print('Warning: Unknown skill "%s" at \'override[%s]\'!'\
                    % (skill, key))


# Define class special features ===========================================
#
# Most data automatically extracted from D&D wiki. Contains only text.
# Does not affect modifiers etc. (to do later)
#
# =========================================================================

def special_abs(npc, act_class, active_class_level, act_max_lvl):

    des = {
    "Uncanny Dodge": "Retains DEX bonus if caught Flat-footed",
    "Imp. Uncanny Dodge": "Cannot be flanked"}

    # Stacking or partially stacking feats are defined as functions
    # If only higher applies, they can be represented as a key:value pair
    def fast_movement():
        npc.speed_bonus += 10
        npc.class_feats['Fast Movement'] = "(+10ft)"

    def speed_bonus():
        npc.unarmored_speed_bonus += 10
        npc.class_feats['Unarmored Speed Bonus'] = "(%s)"\
                                        % str(npc.unarmored_speed_bonus)

    def trap_sense():
        npc.save_special_bonuses['ref']['vs. traps'] += 1
        npc.ac_special_bonuses['dodge']['vs. traps'] += 1
        npc.class_feats['Trap Sense'] = "(+%s)" \
                        % str(npc.save_special_bonuses['ref']['vs. traps'])

    def true_damage_reduction():
        npc.damage_reduction['-'] += 1
        dr = "(%s/-)" % str(npc.damage_reduction['-'])
        npc.class_feats['Damage Reduction'] = dr

    def indomitable_will():
        npc.save_special_bonuses['will']['vs. ench.'] += 4
        npc.class_feats['Indomitable Will'] = "(+%s)" \
                    % str(npc.save_special_bonuses['will']['vs. ench.'])

    def nature_sense():
        npc.total_skill_points['Knowledge (nature)']['misc_mod'] += 2
        npc.total_skill_points['Survival']['misc_mod'] += 2
        npc.class_feats['Nature Sense'] = "(+2 nature checks)"

    def resist_natures_lure():
        npc.save_special_bonuses['general']['vs. Fey'] += 4
        npc.class_feats["Resist Nature's Lure"] = "(+%s)" \
                        % str(npc.save_special_bonuses['general']['vs. Fey'])

    def still_mind():
        npc.save_special_bonuses['will']['vs. ench.'] += 2
        npc.class_feats['Still Mind'] = "(+%s)" \
            % str(npc.save_special_bonuses['will']['vs. ench.'])

    def diamond_soul():
        if act_max_lvl+10 >= npc.spell_resistance:
            npc.spell_resistance += act_max_lvl+10
            npc.class_feats['Diamond Soul'] = "(SR +%s)" %str(act_max_lvl+10)
        else:
            pass

    def perfect_self():
        if npc.damage_reduction['magic'] <= 10:
            npc.damage_reduction['magic'] = 10
        else:
            pass

        dr = "%s/magic" % str(npc.damage_reduction['magic'])
        npc.class_feats['Perfect Self'] = "Considered extraplanar, DR %s" %dr
        npc.race_type = "Outsider (Extraplanar)"

    def sneak_attack():
        npc.sneak_attack += 1

    def monk_ac_bonus():
        npc.ac_unarmored_bonus += 1
        npc.class_feats['Monk AC bonus'] = "(+%s)" % str(npc.ac_unarmored_bonus)

    def divine_grace():
        npc.charisma_to_saves = True
        npc.class_feats['Divine Grace'] = "(CHA modifier to saving throws)"

    def aura_of_courage():
        npc.save_special_bonuses['general']['vs. fear'] += 4
        npc.class_feats["Aura of Courage"] = "(saves +%s vs. fear 10ft radius)"\
                        % str(npc.save_special_bonuses['general']['vs. fear'])

    def favored_enemy():
        favored_enemies =["Aberration", "Humanoid (reptilian)",
                        "Animal", "Magical beast",
                        "Construct", "Monstrous humanoid",
                        "Dragon", "Ooze",
                        "Elemental", "Outsider (air)",
                        "Fey", "Outsider (chaotic)",
                        "Giant", "Outsider (earth)",
                        "Outsider (evil)",
                        "Dwarf", "Outsider (fire)",
                        "Elf", "Outsider (good)",
                        "Goblinoid", "Outsider (lawful)",
                        "Gnoll", "Outsider (native)",
                        "Gnome", "Outsider (water)",
                        "Halfling", "Plant",
                        "Human", "Undead",
                        "Orc", "Vermin"]

        possible = list(set(favored_enemies) - set(npc.favored_enemy))
        npc.favored_enemy.append(random.choice(possible))

    def moon_and_sun():
        msg = "Can speak with any living creature"
        npc.class_feats['Tongue of the Sun and Moon'] = msg
        npc.languages = [msg]

    def animal_companion():
        npc.has_animal_companion = True
        npc.animal_companion['level']\
                += (act_max_lvl + 1) - active_class_level
        npc.class_feats['Animal Companion']\
                = 'level %i' % npc.animal_companion['level']

    def summon_familiar():
        npc.has_familiar = True
        npc.familiar['level']\
                += (act_max_lvl + 1) - active_class_level
        npc.class_feats['Summon familiar']\
                = 'level %i' % npc.familiar['level']

    def turn_undead():
        npc.turn_undead += (act_max_lvl + 1) - active_class_level
        npc.class_feats['Turn undead'] = 'level %i' % npc.turn_undead

    cleric = {
        1: {"Turn undead": turn_undead}}

    wizard = {
        1: {"Summon familiar": summon_familiar,
            "Scribe scroll": "Can create a scroll of any known spell"}}

    barbarian = {
        1:{"Fast Movement": fast_movement,
            "Illiteracy": "Cannot read unless spends 2 points on a language",
            "Rage": "+4 STR/CON, -2 AC, +2 WILL, +%i HP (1/day)" % (2*act_max_lvl)},
        2:{"Uncanny Dodge": des['Uncanny Dodge']},
        3:{"Trap Sense": trap_sense},
        4:{"Rage": "+4 STR/CON, -2 AC, +2 WILL, +%i HP (2/day)" % (2*act_max_lvl)},
        5:{"Imp. Uncanny Dodge": des['Imp. Uncanny Dodge']},
        6:{"Trap Sense": trap_sense},
        7:{"Damage Reduction (-)": true_damage_reduction},
        8:{"Rage": "+4 STR/CON, -2 AC, +2 WILL, +%i HP (3/day)" % (2*act_max_lvl)},
        9:{"Trap Sense": trap_sense},
        10:{"Damage Reduction (-)": true_damage_reduction},
        11:{"Rage": "Greater: +6 STR/CON, -2 AC, +3 WILL, +%i HP (3/day)" % (2*act_max_lvl)},
        12:{"Rage": "Greater: +6 STR/CON, -2 AC, +3 WILL, +%i HP (4/day)" % (2*act_max_lvl), "Trap Sense": trap_sense},
        13:{"Damage Reduction (-)": true_damage_reduction},
        14:{"Indomitable Will": indomitable_will},
        15:{"Trap Sense": trap_sense},
        16:{"Damage Reduction (-)": true_damage_reduction,
            "Rage": "Greater: +6 STR/CON, -2 AC, +3 WILL, +%i HP (5/day)" % 2*act_max_lvl},
        17:{"Rage": "Greater and tireless: +6 STR/CON, -2 AC, +3 WILL, +%i HP (5/day)" % (2*act_max_lvl)},
        18:{"Trap Sense": trap_sense},
        19:{"Damage Reduction (-)": true_damage_reduction},
        20:{"Rage": "Mighty and tireless: +8 STR/CON, -2 AC, +4 WILL, +%i HP (6/day)" % (2*act_max_lvl)},
        21:{"Trap Sense": trap_sense},
        22:{"Damage Reduction (-)": true_damage_reduction},
        24:{"Trap Sense": trap_sense,
            "Rage": "Mighty and tireless: +8 STR/CON, -2 AC, +4 WILL, +%i HP (7/day)" % (2*act_max_lvl)},
        25:{"Damage Reduction (-)": true_damage_reduction},
        27:{"Trap Sense": trap_sense},
        28:{"Damage Reduction (-)": true_damage_reduction,
            "Rage": "Mighty and tireless: +8 STR/CON, -2 AC, +4 WILL, +%i HP (8/day)" % (2*act_max_lvl)},
        30:{"Trap Sense": trap_sense},
        31:{"Damage Reduction (-)": true_damage_reduction},
        33:{"Trap Sense": trap_sense},
        34:{"Rage": "Mighty and tireless: +8 STR/CON, -2 AC, +4 WILL, +%i HP (9/day)" % (2*act_max_lvl),
            "Damage Reduction (-)": true_damage_reduction},
        36:{"Trap Sense": trap_sense},
        37:{"Damage Reduction (-)": true_damage_reduction},
        38:{"Rage": "Mighty and tireless: +8 STR/CON, -2 AC, +4 WILL, +%i HP (10/day)" % (2*act_max_lvl)},
        39:{"Trap Sense": trap_sense},
        40:{"Damage Reduction (-)": true_damage_reduction}}

    bard = {
        1:{"Bardic Music": "May play music (%s per day)" % (act_max_lvl),
           "Bardic Knowledge":
                "May attempt lore checks to gain obscure information",
           "Countersong": "Can use music or poetics to counter magical "\
                                            "effects that depend on sound",
           "Fascinate": "Can use music or poetics to cause one or "\
                            "more creatures to become fascinated with him",
           "Inspire Courage": "Gives allies +1 to saves and damage rolls"},
        3:{"Inspire Competence": "+2 to ally skill checks"},
        6:{"Suggestion": "Influence the actions of the target creature by "\
                    "suggesting a course of activity (Perform vs. Will)"},
        8:{"Inspire Courage": "Gives allies +2 to saves and damage rolls"},
        9:{"Inspire Greatness": "Give allies +2d10 HP, +2 to attack rolls, "\
                                "+1 fortitude save"},
        12:{"Song of Freedom": "Free ally from enchantment "\
                                "(perform for 1 minute)"},
        14:{"Inspire Courage": "Gives allies +3 to saves and damage rolls"},
        15:{"Inspire Heroics": "Gives allies +4 AC and +4 to saves"},
        18:{"Mass Suggestion": "Influence masses of people"},
        20:{"Inspire Courage": "Gives allies +4 to saves and damage rolls"},
        26:{"Inspire Courage": "Gives allies +5 to saves and damage rolls"},
        32:{"Inspire Courage": "Gives allies +6 to saves and damage rolls"},
        38:{"Inspire Courage": "Gives allies +7 to saves and damage rolls"}}

    druid = {
        1: {"Animal Companion": animal_companion,
            "Nature Sense": nature_sense,
            "Wild Empathy": "Charm animals"},
        2: {"Woodland Stride": "Move through natural obstacles"},
        3: {"Trackless Step": "Leaves no trackable trails"},
        4: {"Resist Nature's Lure": resist_natures_lure},
        5: {"Wild Shape": "1/day (small, medium)"},
        6: {"Wild Shape": "2/day (small, medium)"},
        7: {"Wild Shape": "3/day (small, medium)"},
        8: {"Wild Shape": "3/day (small, medium, large)"},
        9: {"Venom Immunity" :"Immunity to all poisons"},
        10: {"Wild Shape": "4/day (small, medium, large)"},
        11: {"Wild Shape": "4/day (tiny, small, medium, large)"},
        12: {"Wild Shape": "4/day (plant, tiny, small, medium, large)"},
        13: {"A Thousand Faces": "Change appearance at will"},
        14: {"Wild Shape": "5/day (plant, tiny, small, medium, large)"},
        15: {"Timeless Body": "Does not age, does not receive aging penalties",
            "Wild Shape": "5/day (plant, tiny, small, medium, large, huge)"},
        16: {"Elemental Shape": "1/day (small, medium, large)"},
        18: {"Wild Shape": "6/day (plant, tiny, small, medium, large, huge)",
            "Elemental Shape": "2/day (small, medium, large)"},
        20: {"Elemental Shape": "3/day (small, medium, large, huge)"},
        22: {"Wild Shape": "7/day (plant, tiny, small, medium, large, huge)",
                 "Elemental Shape": "4/day (small, medium, large, huge)"},
        26: {"Wild Shape": "8/day (plant, tiny, small, medium, large, huge)",
                 "Elemental Shape": "5/day (small, medium, large, huge)"},
        30: {"Wild Shape": "infinite (plant, tiny, small, medium, large, huge)",
                 "Elemental Shape": "infinite (small, medium, large, huge)"}}

    fighter = {}

    monk_dmg = {'medium': '1d4', 'small': '1d2', 'large': '1d6'}
    if act_class == 'monk':
        if act_max_lvl in [1, 2, 3]:
            monk_dmg = {'medium': '1d6', 'small': '1d4', 'large': '1d8'}
        if act_max_lvl in [4, 5, 6, 7]:
            monk_dmg = {'medium': '1d8', 'small': '1d6', 'large': '2d6'}
        if act_max_lvl in [8, 9, 10, 11]:
            monk_dmg = {'medium': '1d10', 'small': '1d8', 'large': '2d8'}
        if act_max_lvl in [12, 13, 14, 15]:
            monk_dmg = {'medium': '2d6', 'small': '1d10', 'large': '3d6'}
        if act_max_lvl in [16, 17, 18, 19]:
            monk_dmg = {'medium': '2d8', 'small': '2d6', 'large': '3d8'}
        if act_max_lvl >= 20:
            monk_dmg = {'medium': '2d10', 'small': '2d8', 'large': '4d8'}

        npc.unarmed_damage = monk_dmg[npc.size]

    if npc.unarmed_damage is None:
        npc.unarmed_damage = monk_dmg[npc.size]

    monk = {
        1: {"Flurry of Blows": "If unarmored, gain one extra attack '\
                                            'with highest BAB -2",
            "Unarmed Strike": "Fists do %s damage" % monk_dmg[npc.size]},
        2: {"Evasion": "No damage from successful REF saves '\
                                            'that would halve damage"},
        3: {"Still Mind": still_mind, "Unarmored Speed Bonus": speed_bonus},
        4: {"Ki Strike": "Fists +1 magic weapons", "Slow Fall": "20 ft."},
        5: {"Purity of Body": "Immunity to non-magical diseases",
            'AC Bonus': monk_ac_bonus,
            "Flurry of Blows":
                "If unarmored, gain one extra attack with highest BAB -1",},
        6: {"Slow Fall": "30 ft.", "Unarmored Speed Bonus": speed_bonus},
        7: {"Wholeness of Body": "Heal %s HP per day" % (act_max_lvl*2)},
        8: {"Slow Fall": "40 ft."},
        9: {"Improved Evasion": "Take half damage from failed REF saves",
            "Unarmored Speed Bonus": speed_bonus},
        10: {"Ki Strike": "Fists +2 magic weapons", "Slow Fall": "50 ft.",
            'AC Bonus': monk_ac_bonus},
        11: {"Diamond Body": "Immunity to all poisons",
            "Flurry of Blows":
                "Greater: If unarmored, gain two extra attacks with highest BAB"},
        12: {"Abundant Step":
                "1/day (teleport %s ft.)" % str(400+(act_max_lvl*20)),
            "Slow Fall": "60 ft.", "Unarmored Speed Bonus": speed_bonus},
        13: {"Diamond Soul": diamond_soul},
        14: {"Slow Fall": "70 ft."},
        15: {"Quivering Palm": "",
            'AC Bonus': monk_ac_bonus, "Unarmored Speed Bonus": speed_bonus},
        16: {"Ki Strike": "Fists +3 magic weapons", "Slow Fall": "80 ft."},
        17: {"Timeless Body": "Does not age",
            "Tongue of the Sun and Moon": moon_and_sun},
        18: {"Slow Fall": "90 ft.", "Unarmored Speed Bonus": speed_bonus},
        19: {"Empty Body" : "Etherealness 1/day"},
        20: {"Perfect Self": perfect_self,
            "Slow Fall": "Any Distance",
            'AC Bonus': monk_ac_bonus},
        21: {"Unarmored Speed Bonus": speed_bonus},
        24: {"Unarmored Speed Bonus": speed_bonus},
        25: {'AC Bonus': monk_ac_bonus},
        27: {"Unarmored Speed Bonus": speed_bonus},
        30: {'AC Bonus': monk_ac_bonus, "Unarmored Speed Bonus": speed_bonus},
        33: {"Unarmored Speed Bonus": speed_bonus},
        35: {'AC Bonus': monk_ac_bonus},
        36: {"Unarmored Speed Bonus": speed_bonus},
        39: {"Unarmored Speed Bonus": speed_bonus},
        40: {'AC Bonus': monk_ac_bonus}}

    paladin = {
        1: {"Aura of Good": "Detect presence of good (60 ft radius)",
            "Detect Evil": "Detect evil at will (60 ft radius)",
            "Smite Evil": "1/day"},
        2: {"Divine Grace": divine_grace, "Lay on Hands": ""},
        3: {"Aura of Courage": aura_of_courage,
            "Divine Health": "Immunity to all types of diseases"},
        4: {"Turn Undead": turn_undead},
        5: {"Smite Evil": "2/day", "Special Mount": ""},
        6: {"Remove Disease": "1/week"},
        9: {"Remove Disease": "2/week"},
        10: {"Smite Evil": "3/day"},
        12: {"Remove Disease": "3/week"},
        15: {"Remove Disease": "4/week", "Smite Evil": "4/day"},
        18: {"Remove Disease": "5/week"},
        20: {"Smite Evil": "5/day"},
        21: {"Remove Disease": "6/week"},
        24: {"Remove Disease": "7/week"},
        25: {"Smite Evil": "6/day"},
        27: {"Remove Disease": "8/week"},
        30: {"Remove Disease": "9/week", "Smite Evil": "6/day"},
        33: {"Remove Disease": "10/week"},
        35: {"Smite Evil": "7/day"},
        36: {"Remove Disease": "11/week"},
        39: {"Remove Disease": "12/week"},
        40: {"Smite Evil": "8/day"}}

    ranger = {
        1: {"Favored Enemy": favored_enemy,
            "Track": "May track by using survival skill",
            "Wild Empathy": "Charm animals"},
        2: {"Combat Style": ""},
        3: {"Endurance": "+4 to checks involving non-lethal"\
                " damage holding-breath. May sleep in medium armor."},
        4: {"Animal Companion": animal_companion},
        5: {"Favored Enemy": favored_enemy},
        6: {"Improved Combat Style": ""},
        7: {"Woodland Stride": "Move through natural obstacles"},
        8: {"Swift Tracker": "Can move normal speed while tracking"},
        9: {"Evasion":
            "On succesful REF save that would halve damage, takes no damage"},
        10: {"Favored Enemy": favored_enemy},
        11: {"Combat Style Mastery": ""},
        13: {"Camouflage": "Can hide in any sort of natural terrain"},
        15: {"Favored Enemy": favored_enemy},
        17: {"Hide in Plain Sight":
                "When in natural terrain, can use hide skill when observed"},
        20: {"Favored Enemy": favored_enemy},
        25: {"Favored Enemy": favored_enemy},
        30: {"Favored Enemy": favored_enemy},
        35: {"Favored Enemy": favored_enemy},
        40: {"Favored Enemy": favored_enemy}}

    rogue = {
        1: {"Sneak Attack": sneak_attack,
                "Trapfinding": "Can use search skill to locate traps"},
        2: {"Evasion": "On succesful REF save that would '\
                        'halve damage, takes no damage"},
        3: {"Sneak Attack": sneak_attack, "Trap Sense": trap_sense},
        4: {"Uncanny Dodge": des['Uncanny Dodge']},
        5: {"Sneak Attack": sneak_attack},
        6: {"Trap Sense": trap_sense},
        7: {"Sneak Attack": sneak_attack},
        8: {"Imp. Uncanny Dodge": des['Imp. Uncanny Dodge']},
        9: {"Sneak Attack": sneak_attack, "Trap Sense": trap_sense},
        10: {"Crippling Strike":
            "Sneak attacks do 2 strength damage (heals 1 point per day)"},
        11: {"Sneak Attack": sneak_attack},
        12: {"Trap Sense": trap_sense},
        13: {"Sneak Attack": sneak_attack, "Special Ability": ""},
        15: {"Sneak Attack": sneak_attack, "Trap Sense": trap_sense},
        16: {"Special Ability": ""},
        17: {"Sneak Attack": sneak_attack},
        18: {"Trap Sense": trap_sense},
        19: {"Sneak Attack": sneak_attack, "Special Ability": ""},
        21: {"Sneak Attack": sneak_attack, "Trap Sense": trap_sense},
        23: {"Sneak Attack": sneak_attack},
        24: {"Trap Sense": trap_sense},
        25: {"Sneak Attack": sneak_attack},
        27: {"Sneak Attack": sneak_attack, "Trap Sense": trap_sense},
        29: {"Sneak Attack": sneak_attack},
        30: {"Trap Sense": trap_sense},
        31: {"Sneak Attack": sneak_attack},
        33: {"Sneak Attack": sneak_attack, "Trap Sense": trap_sense},
        35: {"Sneak Attack": sneak_attack},
        36: {"Trap Sense": trap_sense},
        37: {"Sneak Attack": sneak_attack},
        39: {"Sneak Attack": sneak_attack, "Trap Sense": trap_sense}}

    commoner = {}
    expert = {}
    adept = {2: {'Summon familiar': summon_familiar}}
    aristocrat = {}
    warrior = {}

    class_special_feats = {
        'barbarian': barbarian,
        'cleric': cleric,
        'wizard': wizard,
        'sorcerer': wizard,
        'bard': bard,
        'druid': druid,
        'fighter': fighter,
        'monk': monk,
        'paladin': paladin,
        'ranger': ranger,
        'rogue': rogue,
        'aristocrat': aristocrat,
        'expert': expert,
        'adept': adept,
        'commoner': commoner,
        'warrior': warrior}

    specials = class_special_feats[act_class]

    if active_class_level in specials.keys():
        level_abilities = specials[active_class_level]
        for key in level_abilities.keys():
            if isinstance(level_abilities[key], str):
                # Append class feats as tuples (level, feat)
                if key not in npc.class_feats.keys():
                    npc.class_feats[key] = (act_max_lvl, level_abilities[key])
                else:
                    if isinstance(npc.class_feats[key], tuple):
                        # Overwrite only if ability is higher level
                        if act_max_lvl >= npc.class_feats[key][0]:
                            npc.class_feats[key] = (act_max_lvl,
                                                    level_abilities[key])
                        else:
                            pass
            if hasattr(level_abilities[key], '__call__'):
                level_abilities[key]()

# =====================================================================
""" Feats """
# =====================================================================

# Keep track on epic feats that can be taken multiple times
epic_counter = {}

def add_feats(npc, act_cls, act_cls_lvl, act_cls_lvl_max, comb_level):

    # Temporary variables, fix later
    npc.str = npc.abilities['str']
    npc.con = npc.abilities['con']
    npc.dex = npc.abilities['dex']
    npc.wis = npc.abilities['wis']
    npc.int = npc.abilities['int']
    npc.cha = npc.abilities['cha']
    npc.lvl = act_cls_lvl

    def check_reqs(name, args, index):
        """ Check if feat pre-requirements are met
        Return True if requirements are ok or not specified """
        if not args['reqs']:
            return True
        else:
            for requirement in args['reqs'].keys():
                val = args['reqs'][requirement]
                if isinstance(val, int):
                    if npc.__dict__[requirement] < val:
                        return False
                if isinstance(val, str):
                    if val not in npc.__dict__[requirement].keys():
                        return False
            return True

    def pre_req_feat(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        npc.feats[name] = args['descr']
        return True

    def improved_grapple(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        npc.feats[name] = args['descr']
        npc.grapple += 4
        return True

    def count_epic(name, descr):
        if name not in epic_counter.keys():
            epic_counter[name] = 1
        else:
            epic_counter[name] += 1

        ft_name = "%s (+%s)" % (name, str(epic_counter[name]))
        npc.feats[ft_name] = descr

    def epic_armor_skin(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        count_epic(name, args['descr'])
        npc.ac_modifiers['natural'] += 1
        return True

    def epic_toughness(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        count_epic(name, args['descr'])
        npc.hp += 30
        return True

    def epic_polyglot(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        npc.languages = ['Can speak all lanugages']
        return True

    def epic_sneak_attack(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        count_epic(name, args['descr'])
        npc.sneak_attack += 1
        return True

    def epic_ability(name, args, index):
        """ Pump up ability scores on epic levels """
        if not check_reqs(name, args, index):
            return False

        abrs = {'str': 'Strength',
                'dex': 'Dexterity',
                'con': 'Constitution',
                'wis': 'Wisdom',
                'int': 'Intelligence',
                'cha': 'Charisma'}

        if npc.abilities[npc.priority_order[0]] > 30:
            increase = npc.priority_order[1]
        else:
            increase = npc.priority_order[0]

        count_epic("%s %s" % (name, abrs[increase]), args['descr'])
        npc.abilities[increase] += 1
        return True

    def epic_dr(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        count_epic(name, args['descr'])
        npc.damage_reduction['-'] += 3
        return True

    def epic_initiative(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        npc.initiative += 8
        npc.feats[name] = args['descr']
        return True

    def epic_fast_healing(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        npc.fast_healing += 3
        npc.feats[name] = args['descr']
        return True

    def epic_skill_focus(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        ranked = []
        for skill in npc.total_skill_points.keys():
            if npc.total_skill_points[skill]['ranks'] > 10:
                ranked.append(skill)

        if len(ranked) < 1:
            return False
        else:
            increase = random.choice(ranked)
            count_epic(name, "(Improved %s)" % increase)
            npc.total_skill_points[increase]['misc_mod'] += 10
            return True

    def epic_energy_resistance(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        count_epic(name, args['descr'])
        type_ = random.choice(['fire', 'cold', 'acid'])
        npc.damage_reduction[type_] += 10
        return True

    def wpn_focus(name, args, index):
        """ Check feats with pre-requirements """
        if not check_reqs(name, args, index):
            return False

        if len(npc.weapon_profiencies) == 0:
            return False
        else:
            weapon_type = random.choice(npc.weapon_profiencies)

        npc.feats[name + ' ('+weapon_type+')'] = args['descr']
        return True

    def skill_feat(name, args, index):
        descr = []
        for k in args.keys():
            npc.skill_points[index][k]['ranks'] += args[k]
            descr.append('+%i to %s' % (args[k], k))
        npc.feats[name] = "(%s)" % ', '.join(descr)
        return True

    def save_feat(name, args, index):
        descr = []
        for k in args.keys():
            npc.saves_mods[k]['misc'] += args[k]
            descr.append('+%i to %s saves' % (args[k], k))
        npc.feats[name] = "(%s)" % ', '.join(descr)
        return True

    def save_special_feat(name, args, index):
        descr = []
        for k in args.keys():
            for j in args[k].keys():
                npc.save_special_bonuses[k][j] += args[k][j]
            descr.append('+%i to saves %s' % (args[k][j], j))
        npc.feats[name] = "%s" % ', '.join(descr)
        return True

    def armor_light(name):
        npc.armor_profiencies.append('light')
        npc.feats[name] = ""
        return True

    def armor_medium(name):
        npc.armor_profiencies.append('medium')
        npc.feats[name] = ""
        return True

    def spell_penetration(name):
        npc.spell_penetration += 2
        npc.feats[name] = "+2 to checks breaking enemy spell resistance"

    def armor_heavy(name):
        if npc.ability_mods['dex'] > 1:
            return False
        else:
            npc.armor_profiencies.append('heavy')
            npc.feats[name] = ""
            return True

    def shield_profiency(name):
        npc.has_shield_profiency = True
        npc.feats[name] = "No armor check penalty on attack rolls"
        return True

    def improved_initiative(name):
        val = 4
        npc.initiative += val
        npc.feats[name] = "(+%i to initiative)" % val
        return True

    def run(name):
        npc.run_speed_multiplier = 5
        npc.feats[name] = "Run speed increased"
        return True

    def wpn_profiency(name, args, index):
        npc.weapon_profiencies.append(args)
        npc.feats[name] = 'No -4 penalty with %s weapons' % args
        return True

    def toughness(name):
        npc.hp += 3
        npc.feats[name] = '(+3 hitpoints)'
        return True

    # Feat dictionary combiner
    def merge_dicts(*dict_args):
        """Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts."""
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    general_feats = {
        'Acrobatic': [skill_feat, {'Jump': 2, 'Tumble': 2}],
        'Agile': [skill_feat, {'Balance': 2, 'Escape Artist': 2}],
        'Alertness': [skill_feat, {'Listen': 2, 'Spot': 2}],
        'Animal Affinity': [skill_feat, {'Ride': 2, 'Handle Animal': 2}],
        'Armor Profiency (light)': armor_light,
        'Armor Profiency (medium)': armor_medium,
        'Armor Profiency (heavy)': armor_heavy,
        'Athletic': [skill_feat, {'Climb': 2, 'Swim': 2}],
        'Blind-fight': 'When fighting concealed creatures, reroll misses '\
                        'once. Half penalties when blinded',
        'Combat reflexes': 'Additional attack of opportunity',
        'Deceitful': [skill_feat, {'Disguise': 2, 'Forgery': 2}],
        'Deft hands': [skill_feat, {'Use Rope': 2, 'Sleight of Hand': 2}],
        'Endurance': [save_special_feat, {'general': {'vs. non-lethal': 4}}],
        'Great Fortitude': [save_feat, {'fort': 2}],
        'Improved initiative': improved_initiative,
        'Iron Will': [save_feat, {'will': 2}],
        'Lightning Reflexes': [save_feat, {'ref': 2}],
        'Point Blank Shot': '+1 bonus on ranged attack and damage within 30 ft.',
        'Run': run,
        'Shield Profiency': shield_profiency,
        'Simple Weapon Profiency': [wpn_profiency, 'simple'],
        'Martial Weapon Profiency': [wpn_profiency, 'martial'],
        'Exotic Weapon Profiency': [wpn_profiency, 'exotic'],
        'Toughness': toughness
        }

    magic_feats = {
        'Augment Summoning': 'Summoned monsters have +4 STR/CON',
        'Combat Casting': '+4 concentration when casting defensively',
        'Eschew Materials': 'Cast spells without material components',
        'Improved counterspell': 'Counterspell with spell of same school',
        'Spell Penetration': spell_penetration}

    metamagic_feats = {
        'Empower Spell': "Increase spell's variable, numeric effects by 50%",
        'Enlarge Spell': "Double spell's range",
        'Extend Spell': "Double spell's duration",
        'Heighten Spell': "Cast spells as higher level",
        'Maximize Spell': "Maximize spell's variable, numeric effects",
        'Quicken Spell': "Cast spells as free action",
        'Silent Spell': "Cast spells without verbal components",
        'Still Spell': "Cast spells without somatic components",
        'Widen Spell': "Double spell's area"}

    fighter_bonus_feats = {
        'Power Attack': [pre_req_feat,
            {'descr':
                    'Trade attack bonus for damage (up to base attack bonus)',
            'reqs': {'str': 13}}],
        'Cleave': [pre_req_feat,
            {'descr': 'Extra melee attack after killing target',
            'reqs': {'feats': 'Power Attack'}}],
        'Great Cleave': [pre_req_feat,
            {'descr': 'No limit to cleave attacks each round',
            'reqs': {'feats': 'Cleave', 'bab': 4}}],
        'Improved Shield Bash': [pre_req_feat,
            {'descr': 'Retain shield bonus to AC when bashing',
            'reqs': {'feats': 'Shield Profiency'}}],
        'Two Weapon Fighting': [pre_req_feat,
            {'descr': 'Reduce two-weapon fighting penalties by 2',
            'reqs': {'dex': 15}}],
        'Two Weapon Defense': [pre_req_feat,
            {'descr': 'Off-hand weapon grants +1 shield bonus to AC',
            'reqs': {'feats': 'Two Weapon Fighting'}}],
        'Impr. Two Weapon Fighting': [pre_req_feat,
            {'descr': 'Gain second off-hand attack',
            'reqs': {'dex': 17, 'feats': 'Two Weapon Fighting', 'bab': 6}}],
        'Greater Two Weapon Fighting': [pre_req_feat,
            {'descr': 'Gain second off-hand attack',
            'reqs': {'dex': 19,
                    'feats': 'Impr. Two Weapon Fighting', 'bab': 11}}],
        'Weapon Focus': [wpn_focus,
            {'descr': '(+1 with selected weapon type)',
            'reqs': {'bab': 1}}],
            }

    wizard_bonus_feats = {'Spell Mastery':
                                'Can prepare some spells without spell book'}

    monk_bonus_feats = {
        'Improved Unarmed Strike': [pre_req_feat,
            {'descr': 'Does not provoke attacks of opportunity when unarmed',
            'reqs': {}}],
        'Improved grapple': [improved_grapple,
            {'descr': '(+4 to grapple checks)',
            'reqs': {}}],
        'Stunning Fist': [pre_req_feat,
            {'descr': 'May attempt to stun opponents with unarmed strikes',
            'reqs': {'lvl': 2}}],
        'Combat Reflexes': [pre_req_feat,
            {'descr': 'May make a number of additional attacks of '\
                        'opportunity equal to DEX bonus',
            'reqs': {'lvl': 2}}],
        'Deflect Arrows': [pre_req_feat,
            {'descr': 'May dodge ranged attack once per round',
            'reqs': {'lvl': 2}}],
        'Improved Disarm': [pre_req_feat,
            {'descr': 'Does not provoke AOO when disarming enemy',
            'reqs': {'lvl': 6}}],
            }

    warrior_type_feats = merge_dicts(general_feats, fighter_bonus_feats)
    mixed_type_feats = merge_dicts(warrior_type_feats,
                                    magic_feats, metamagic_feats, general_feats)
    wizard_type_feats = merge_dicts(magic_feats, metamagic_feats, general_feats)

    # Which kind of feats each class will pick
    gen_feats = {
        'fighter': warrior_type_feats,
        'barbarian': warrior_type_feats,
        'paladin': warrior_type_feats,
        'ranger': warrior_type_feats,
        'cleric': mixed_type_feats,
        'wizard': wizard_type_feats,
        'sorcerer': wizard_type_feats,
        'bard': mixed_type_feats,
        'rogue': warrior_type_feats,
        'monk': warrior_type_feats,
        'druid': mixed_type_feats,
        'commoner': general_feats,
        'expert': general_feats,
        'adept': mixed_type_feats,
        'aristocrat': general_feats,
        'warrior': mixed_type_feats}

    non_epic_bonus_feats = {
        'wizard': merge_dicts(wizard_bonus_feats, metamagic_feats),
        'monk': monk_bonus_feats,
        'fighter': fighter_bonus_feats}

    # NON BONUS epic feats
    epic_feats = {
        'Great': [epic_ability,
            {'descr': '(Ability score bonus)',
            'reqs': {}}]
        }

    fighter_epic_bonus_feats = {
        'Armor Skin': [epic_armor_skin,
            {'descr': '(Improved natural armor)',
            'reqs': {}}],
        'Epic Toughness': [epic_toughness,
            {'descr': '(Additional hitpoints)',
            'reqs': {}}],
        'Superior Initiative': [epic_initiative,
            {'descr': '(+8 to initiative)',
            'reqs': {}}],
        'Energy Resistance': [epic_energy_resistance,
            {'descr': '(Elemental damage reduction)',
            'reqs': {}}],
        'Perfect Two Weapon Fighting': [pre_req_feat,
            {'descr': 'The character can make as many attacks with his or '\
                        'her off-hand weapon as with his or her primary '\
                        'weapon, using the same base attack bonus.',
            'reqs': {'feats': 'Greater Two Weapon Fighting', 'dex': 25}}],
        'Epic Damage Reduction': [epic_dr,
            {'descr': '(Increased damage reduction)',
            'reqs': {}}]    }

    rogue_epic_bonus_feats = {
        'Epic Sneak Attack': [epic_sneak_attack,
            {'descr': 'Improved Sneak Attack',
            'reqs': {'sneak_attack': 8}}],
        'Legendary Climber': [pre_req_feat,
            {'descr': 'May ignore all penalties applied for accelerated climbing',
            'reqs': {'dex': 21}}],
        'Sneak Attack of Opportunity': [pre_req_feat,
            {'descr': 'Attack of opportunities gain sneak attack bonus',
            'reqs': {'sneak_attack': 8}}],
        'Combat Archery': [pre_req_feat,
            {'descr': 'Enemies do not get AOO when using bow',
            'reqs': {'feats': 'Point Blank Shot'}}],
        'Dexterous Will': [pre_req_feat,
            {'descr': 'May use reflex save instead of will save once per round',
            'reqs': {'dex': 25}}],
        'Dexterous Fortitude': [pre_req_feat,
            {'descr': 'May use reflex save instead of fortitude save once per round',
            'reqs': {'dex': 25}}],
        'Epic Skill Focus': [epic_skill_focus,
            {'descr': '(Bonus to skill checks)',
            'reqs': {}}]}

    cleric_epic_bonus_feats = {
        'Armor Skin': fighter_epic_bonus_feats['Armor Skin'],
        'Impr. Combat Casting': [pre_req_feat,
            {'descr': 'Does not incur AOO when casting spells',
            'reqs': {'feats': 'Combat Casting'}}],
        'Planar Turning': [pre_req_feat,
            {'descr': 'May turn outsiders as undead',
            'reqs': {'wis': 25, 'cha': 25}}],
        'Undead Mastery': [pre_req_feat,
            {'descr': 'The character may command up to ten times his or '\
                            'her level in HD of undead',
            'reqs': {'cha': 21}}],
        'Spell Penetration': spell_penetration,
        'Greater Spell Penetration': [pre_req_feat,
            {'descr': 'Additional +2 to checks breaking enemy spell resistance',
            'reqs': {'feats': 'Spell Penetration'}}],
        'Epic Spell Penetration': [pre_req_feat,
            {'descr': 'Additional +2 to checks breaking enemy spell resistance',
            'reqs': {'feats': 'Greater Spell Penetration'}}],
            }

    druid_epic_bonus_feats = {
        'Wildshape (Colossal)': [pre_req_feat,
            {'descr': 'May shapeshift into colossal animals',
            'reqs': {'feats': 'Wildshape (Gargantuan)'}}],
        'Wildshape (Diminutive)': [pre_req_feat,
            {'descr': 'May shapeshift into diminutive animals',
            'reqs': {}}],
        'Wildshape (Gargantuan)': [pre_req_feat,
            {'descr': 'May shapeshift into gargantuan animals',
            'reqs': {'feats': 'Wildshape (Huge)'}}],
        'Wildshape (Huge)': [pre_req_feat,
            {'descr': 'May shapeshift into huge animals',
            'reqs': {}}],
        'Wildshape (Fine)': [pre_req_feat,
            {'descr': 'May shapeshift into fine sized animals',
            'reqs': {'feats': 'Wildshape (Diminutive)'}}],
        'Dragon Shape': [pre_req_feat,
            {'descr': 'May shapeshift into Dragon. '\
                    'Maximum size is determined by Wildshape feats',
            'reqs': {'wis': 30}}],
        'Fast Healing': [epic_fast_healing,
            {'descr': '(Improved HP regeneration)',
            'reqs': {'con': 25}}],
        'Energy Resistance': fighter_epic_bonus_feats['Energy Resistance'],
        'Spell Penetration': spell_penetration,
        'Greater Spell Penetration':
            cleric_epic_bonus_feats['Greater Spell Penetration'],
        'Epic Spell Penetration':
            cleric_epic_bonus_feats['Epic Spell Penetration']
            }

    wizard_epic_bonus_feats = {
        'Impr. Combat Casting': cleric_epic_bonus_feats['Impr. Combat Casting'],
        'Spell Penetration': spell_penetration,
        'Greater Spell Penetration':
            cleric_epic_bonus_feats['Greater Spell Penetration'],
        'Epic Spell Penetration':
            cleric_epic_bonus_feats['Epic Spell Penetration']
            }

    bard_epic_bonus_feats = {
        'Impr. Combat Casting': cleric_epic_bonus_feats['Impr. Combat Casting'],
        'Epic Skill Focus': rogue_epic_bonus_feats['Epic Skill Focus'],
        'Polyglot': [epic_polyglot,
            {'descr': 'Can speak all languages',
            'reqs': {'int': 25}}]}

    epic_bonus_feats = {
        'fighter': fighter_epic_bonus_feats,
        'paladin': fighter_epic_bonus_feats,
        'monk': fighter_epic_bonus_feats,
        'barbarian': fighter_epic_bonus_feats,
        'ranger': fighter_epic_bonus_feats,
        'rogue': rogue_epic_bonus_feats,
        'cleric': cleric_epic_bonus_feats,
        'druid': druid_epic_bonus_feats,
        'wizard': wizard_epic_bonus_feats,
        'sorcerer': wizard_epic_bonus_feats,
        'bard': bard_epic_bonus_feats,
        }

    def pick_feats(available_feats, feats):
        picked = False
        max_iteration = 0
        while not picked:
            pick = random.choice(available_feats)
            if isinstance(feats[pick], str):
                npc.feats[pick] = feats[pick]
                picked = True
            if isinstance(feats[pick], list):
                if hasattr(feats[pick][0], '__call__'):
                    args = feats[pick][1]
                    picked = feats[pick][0](pick, args, index)
            if hasattr(feats[pick], '__call__'):
                picked = feats[pick](pick)
            max_iteration += 1
            # Safety mechanism if no feats available
            if max_iteration == 100:
                picked = True

    # Define basic feat progression
    feat_progression = [1] + [x for x in range(3,40,3)]
    bonus_feat_progression = class_specs[act_cls]['bonus_feats']

    # Active class index for skillpoints
    index = npc.Class.index(act_cls)
    if act_cls_lvl in feat_progression:
        if comb_level < 21:
            available = list(set(gen_feats[act_cls].keys()) - set(npc.feats.keys()))
            # Prevent feeding empty arrays to random.choice()
            if len(available) > 0:
                pick_feats(available, gen_feats[act_cls])
        else:
            available = list(set(epic_feats.keys()) - set(npc.feats.keys()))
            if len(available) > 0:
                pick_feats(available, epic_feats)

    print(act_cls, act_cls_lvl, '# DEBUG #######################')
    if act_cls_lvl in bonus_feat_progression:
        if comb_level < 21:
            bfeats = non_epic_bonus_feats[act_cls]
        else:
            bfeats = epic_bonus_feats[act_cls]
        available = list(set(bfeats.keys()) - set(npc.feats.keys()))
        # Prevent feeding empty arrays to random.choice()
        if len(available) > 0:
            pick_feats(available, bfeats)


# ======= DEFINITIONS END =================================================
