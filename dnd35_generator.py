#! /usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$1.0$"

import random
import re
import dnd35_defs as dnd
import html_template as html_sheet

# owwww|=================> Dungeons & Dragons <==================|wwwwo
# TODO:
#    - Improve multi-class ability score distribution
#    - Fix level adjustments (now roll chr lvl 0)
#    - Split code into modules
#
# Python 2.7 -- A. Sahala
# #####################################################################

NPC = dnd.Character()
roll = dnd.roll_dice
d00 = dnd.dice['d00']
d20 = dnd.dice['d20']
d10 = dnd.dice['d10']
d8 = dnd.dice['d8']
d6 = dnd.dice['d6']
d4 = dnd.dice['d4']

class NPCBuilder():

    def __init__(self):
        self.use_only_standard_rolls = False
        self.current_level = 0

    def check_if_racial_bonus(self, bonus, null):
        ret = null
        """ Call this fuction to check if racial bonuses are available
        ´bonus´ = category name, ´type_´ = return if not available"""
        if 'bonuses' in dnd.race_specs[NPC.race].keys():
            if bonus in dnd.race_specs[NPC.race]['bonuses'].keys():
                ret = dnd.race_specs[NPC.race]['bonuses'][bonus]
        return ret

    def make_priority_order(self, char_class, race_specs):
        """ Create a hybrid priorization table for multi-class characters
        by forming a matrix from class specific priorization tables and
        finding the optimal path. E.g. when multi-classing from Fighter
        to Wizard:

            Fighter:     STR    CON     DEX     WIS     INT     CHA
                          |   /  |   __________/   \____
                          v  /   v  /                    \
            Wizard:      INT    DEX     CON     WIS     CHA     STR

        Thus new priority order would be:

            STR -> INT -> CON -> DEX -> WIS -> CHA

        """

        if len(char_class) == 2:
            p_order = []
            high_class = NPC.Class[NPC.level.index(max(NPC.level))]
            low_class = NPC.Class[NPC.level.index(min(NPC.level))]
            for pair in zip(dnd.class_specs[high_class]['ability_priorization'],
                        dnd.class_specs[low_class]['ability_priorization']):
                for ability in pair:
                    if ability not in p_order:
                        p_order.append(ability)
                    else:
                        pass
        else:
            p_order = dnd.class_specs[char_class[0]]['ability_priorization']
        NPC.priority_order = p_order

    def distribute_abilities(self, char_class, race_specs):
        """ Assign ability scores following the priority order """

        sort_list = list()
        for key in NPC.abilities.keys():
            sort_list.append(NPC.abilities[key])

        sort_list = sorted(sort_list, reverse=True)
        i = 0
        for ability in NPC.priority_order:
            if sort_list[i] < 3:
                sort_list[i] = 3
            ability_score = sort_list[i]\
                            + race_specs['ability_adjustments'][ability]\
                            + dnd.aging_modifiers[NPC.age_type][ability]
            NPC.ability_adjustments[ability] = \
                            + race_specs['ability_adjustments'][ability]\
                            + dnd.aging_modifiers[NPC.age_type][ability]

            # Disallow scores lower than 3
            if ability_score < 3:
                ability_score = 3

            NPC.abilities[ability] = ability_score
            i += 1
        self.update_ability_mods()

    def update_variables(self):
        cha_mod = NPC.ability_mods['cha']
        wis_mod = NPC.ability_mods['wis']
        str_mod = NPC.ability_mods['str']
        size = NPC.size
        race_specs = dnd.race_specs[NPC.race]

        def update_AC():
            """ Special AC modifiers """
            specials = self.check_if_racial_bonus('special_armor_bonus', dict())
            for b in specials.keys():
                for k in specials[b].keys():
                    NPC.ac_special_bonuses[b][k] += specials[b][k]

            """ Check racial modifiers """
            racial_bonus = self.check_if_racial_bonus('armor', dict())
            for b in racial_bonus.keys():
                NPC.ac_modifiers[b] = racial_bonus[b]

            """ Check item modifiers """

            if NPC.wears_armor:
                unarmored = 0
            else:
                if NPC.wisdom_to_ac:
                    unarmored = NPC.ac_unarmored_bonus+NPC.ability_mods['wis']
                else:
                    unarmored = NPC.ac_unarmored_bonus

            NPC.ac_modifiers['mods'] = NPC.ability_mods['dex']
            NPC.ac_modifiers['size'] = dnd.ac_size_adj[NPC.size]
            NPC.ac_base = 10 + unarmored
            total_ac = NPC.ac_base

            for bonus in NPC.ac_modifiers.keys():
                total_ac += NPC.ac_modifiers[bonus]
            NPC.ac = total_ac
            NPC.ac_touch = NPC.ac_base + NPC.ability_mods['dex']\
                                        + NPC.ac_modifiers['size']
            if "Uncanny Dodge" in NPC.class_feats.keys():
                NPC.ac_flat_footed = NPC.ac
            else:
                NPC.ac_flat_footed = NPC.ac - NPC.ability_mods['dex']

        def update_saves():
            # Special bonuses
            spec_bonus = self.check_if_racial_bonus('special_save_bonus',
                                                                dict())
            for b in spec_bonus.keys():
                for k in spec_bonus[b].keys():
                    NPC.save_special_bonuses[b][k] += spec_bonus[b][k]

            # General saves
            empty = {'fort': 0, 'ref': 0, 'will': 0}
            bonus = 0
            if NPC.charisma_to_saves:
                bonus = NPC.ability_mods['cha']

            racial = self.check_if_racial_bonus('saves', empty)

            for save in NPC.saves_mods.keys():
                NPC.saves_mods[save]['misc'] += racial[save] + bonus

            key_abs = {
                'fort': NPC.ability_mods['con'],
                'ref': NPC.ability_mods['dex'],
                'will': NPC.ability_mods['wis']}

            for save in NPC.saves_mods.keys():
                NPC.saves_mods[save]['ab'] = key_abs[save]
                NPC.saves_total[save] = NPC.saves_mods[save]['ab']\
                                        + NPC.saves_mods[save]['mag']\
                                        + NPC.saves_mods[save]['misc']\
                                        + NPC.saves_base[save]

        def update_class_feats():
            """ Recount lay on hands magnitude """
            if 'Lay on Hands' in NPC.class_feats.keys():
                if cha_mod > 0:
                    level = NPC.class_feats['Lay on Hands'][0]
                    txt = 'Heal {amt} HPs/day (may be used in small portions)'\
                                    .format(amt=(str(cha_mod*level)))
                    NPC.class_feats['Lay on Hands'] = (level, txt)

            """ Recount smite evil magnitude """
            feat = 'Smite Evil'
            if feat in NPC.class_feats.keys():
                level = NPC.class_feats[feat][0]
                amount = (level/5)+1
                txt = '+{hit} to hit, +{dmg} to dmg vs. evil ({amt}/day)'\
                                .format(amt=amount,
                                        hit=cha_mod,
                                        dmg=level)
                NPC.class_feats[feat] = (level, txt)

            feat = "Quivering Palm"
            if feat in NPC.class_feats.keys():
                level = NPC.class_feats[feat][0]
                txt = "Enemy must do a successful fortitude save vs. {DC} or die (1/week)".format(
                    DC = ((level/2)+wis_mod+10))
                NPC.class_feats[feat] = (level, txt)

        def update_speed():
            if not NPC.wears_armor:
                bonus = NPC.unarmored_speed_bonus
            else:
                bonus = 0
            NPC.speed = NPC.speed_base + NPC.speed_bonus + bonus

        def update_grapple():
            bonus = self.check_if_racial_bonus('grapple', 0)
            """
            if 'bonuses' in race_specs.keys():
                if 'grapple' in race_specs['bonuses']:
                    bonus = race_specs['bonuses']['grapple']"""
            NPC.grapple = NPC.bab + str_mod + dnd.grapple_adj[size] + bonus

        update_AC()
        update_saves()
        update_class_feats()
        update_speed()
        update_grapple()

    def update_hitpoints(self, change):
        # Apply changes in constitution to overall hitpoints
        NPC.hp += (change * self.current_level)

    def update_ability_mods(self):
        """ Update ability score modifiers if scores are changed """
        old_con_modifier = NPC.ability_mods['con']
        scoretable = dict()
        sco = 0
        min_mod = -5
        while sco < 50:
            # Define breakpoints for ability modifier change
            if sco in range(1, 51, 2): min_mod += 1
            sco += 1
            scoretable[sco] = min_mod

        for key in NPC.abilities:
            NPC.ability_mods[key] = scoretable[NPC.abilities[key]]

        self.update_hitpoints(NPC.ability_mods['con'] - old_con_modifier)

    def check_ability_increase(self, level, active_class):
        """ Ability increases are chosen by class specific priorities """
        primary_abilities = dnd.class_specs[active_class]\
                            ['ability_priorization'][0:3]
        all_abilities = dnd.class_specs[active_class]\
                        ['ability_priorization'][0:6]

        """ Ability increase priorities:
        1) Raise severely negative stats to 8 to overcome negative modifiers.
            If CHA, WIS or DEX are irrelevant for the class, do not raise.
        2) If caster, pump primary ability to 19 to unlock all spell levels.
            Bards and Adepts pump primary to 16.
        3) Raise odd primary abilities having negative modifiers.
        4) Raise any ability score if 9 to overcome negative modifier,
            ignore irrelevant stats.
        5) raise odd positive primary abilities to improve modifiers
        6) raise primary abilities if under 16. Exception being dexterity
            if class is a heavy armor user.
        7) pump two primary abilities randomly, spellcasters pump primary  """

        # Define two least significant ability scores
        irrelevant = NPC.priority_order[-2:]
        stat_increased = False
        if not stat_increased:
            for key in all_abilities:
                if NPC.abilities[key] < 8 and key not in irrelevant\
                and key not in ['cha', 'wis', 'dex']:
                    NPC.abilities[key] += 1
                    stat_increased = True
                    break
        if not stat_increased:
            if active_class in dnd.classes['spellcaster']\
                and NPC.abilities[primary_abilities[0]] < 19:
                NPC.abilities[primary_abilities[0]] += 1
                stat_increased = True
            elif active_class in ['bard', 'adept']\
                and NPC.abilities[primary_abilities[0]] < 16:
                NPC.abilities[primary_abilities[0]] += 1
                stat_increased = True
        if not stat_increased:
            for key in primary_abilities:
                if NPC.abilities[key] in range(1,11,2)\
                and key not in irrelevant:
                    NPC.abilities[key] += 1
                    stat_increased = True
                    break
        if not stat_increased:
            for key in all_abilities:
                if NPC.abilities[key] in [9]:
                    NPC.abilities[key] += 1
                    stat_increased = True
                    break
        if not stat_increased:
            for key in primary_abilities:
                if NPC.abilities[key] in sorted(range(11,41,2),
                                                   reverse=True):
                    NPC.abilities[key] += 1
                    stat_increased = True
                    break
        if not stat_increased:
            for key in primary_abilities:
                if NPC.abilities[key] < 16\
                and active_class not in dnd.classes['armor_user']\
                and key != 'dex':
                    NPC.abilities[key] += 1
                    stat_increased = True
                    break
        if not stat_increased:
            for c in NPC.Class:
                caster_primary = dnd.class_specs[c]['ability_priorization'][0]
                if c in dnd.classes['spellcaster']\
                and caster_primary < 19:
                    NPC.abilities[caster_primary] += 1
                    break
            else:
                NPC.abilities[random.choice(primary_abilities[0:2])] += 1

            stat_increased = True

    def level_up(self, level, active_class_level):
        """ Level up chacter as long as the wanted char level is met."""

        self.update_ability_mods() # update_modifiers

        """ Define breakpoint after which second class will be developed """
        breakpoint = NPC.level[0]

        # ==============================================================
        """ Main level up loop consists of following phases:
        1) roll HP
        2) check if ability increase is possible
        3) calculate new BAB
        4) calculate saving throws
        5) calculate number of attacks per round """
        # ==============================================================
        # Define current level for re-calculations
        self.current_level = level

        # Select active class to level
        if level <= breakpoint:
            skill_index = 0 # used to store skills separately
            active_class = NPC.Class[0]
            active_class_level = level
            active_class_level_max = NPC.level[0]
        else:
            skill_index = 1
            active_class = NPC.Class[1]
            active_class_level = level - NPC.level[0]
            active_class_level_max = NPC.level[1]


        HD = dnd.class_specs[active_class]['HD']

        # Check if race has a special HD
        if 'HD' in dnd.race_specs[NPC.race]['bonuses'].keys():
            if level <= dnd.race_specs[NPC.race]['bonuses']['HD'][1]:
                if HD < dnd.race_specs[NPC.race]['bonuses']['HD'][0]:
                    HD = dnd.race_specs[NPC.race]['bonuses']['HD'][0]

        # Max HP roll at level 1
        if level == 1:
            hp_roll = HD + NPC.ability_mods['con']
        else:
            # Adjust HP rolls according to NPC power type
            # e.g. legendary barbarian rolls 3x1d12 and ignores 2 lowest
            ignore_lowest = dnd.power_types[NPC.power]['hp_roll']
            times = ignore_lowest + 1

            hp_roll = roll(HD, times, 0, NPC.ability_mods['con'],
                            ignore_lowest)
            # Disallow lower rolls than 1
            if hp_roll < 1:
                hp_roll = 1

        NPC.hp += hp_roll

        # ==============================================================
        """ Check if eligible for ability increase """
        # ==============================================================
        if level in range(4, 40, 4):
            print(NPC.abilities)
            self.check_ability_increase(level, active_class)
            self.update_ability_mods()

        # ==============================================================
        """ Increase base attack bonus and saving throws"""
        # ==============================================================
        if level < 21:
            NPC.bab += dnd.class_specs[active_class]['bab'][level-1]
            for key in NPC.saves_base:
                NPC.saves_base[key]\
                    += dnd.class_specs[active_class]['saves'][key][level-1]
        if level in range(21, 40, 1):
            NPC.bab += dnd.BAB_tables['epic'][level-21]
            for key in NPC.saves_base:
                NPC.saves_base[key]\
                    += dnd.save_tables['epic'][key][level-21]

        # ==============================================================
        """ Count how many attacks character can make. Nonetype indicates
        that the BAB is too low for gaining an additional attack """
        # ==============================================================
        i = 1
        for new_attack in range(0, 16, 5):
            attack = NPC.bab - new_attack
            if attack > 1:
                NPC.attacks[i] = attack
            else:
                if i > 1:
                    NPC.attacks[i] = None
                else:
                    NPC.attacks[i] = attack
            i += 1

        # ==============================================================
        """ Increase skills """
        # ==============================================================
        # Get class skills and cross-class skills
        bonus = self.check_if_racial_bonus('class_skills', list())

        class_skills = dnd.class_skills[active_class] + bonus
        cross_skills = list(set(dnd.skills.keys()) - set(class_skills))

        # Define max ranks for class and cross-class skills
        # Max ranks are based on total level instead of active class level
        # (see PHB p. 62)
        class_max_ranks = level + 3
        cross_max_ranks = class_max_ranks / 2

        # Five x4 multiplier on first level. Check if race is eligible
        # for bonus points, defined in ´dnd.bonus_skills´
        if level == 1:
            multiplier = 4
            if NPC.race in dnd.bonus_skills.keys():
                bonus = dnd.bonus_skills[NPC.race][0]
            else:
                bonus = 0
        else:
            multiplier = 1
            if NPC.race in dnd.bonus_skills.keys():
                bonus = dnd.bonus_skills[NPC.race][1]
            else:
                bonus = 0

        mod = dnd.class_specs[active_class]['skill_mod'] + bonus
        points = (mod + NPC.ability_mods['int']) * multiplier
        # Character cannot get fewer skill points than the multiplier
        if points < 1:
            points = multiplier + bonus

        # Distribute available skill points
        while points > 0:
            random_index = random.randint(0, len(class_skills)-1)
            random_skill = NPC.skill_points[skill_index]\
                                        [class_skills[random_index]]

            if random_skill['ranks'] < class_max_ranks:
                random_skill['ranks'] += 1

            points -= 1

        # Combine skills from both classes and count bonuses
        racial_bonus = self.check_if_racial_bonus('skill_bonus', dict())

        for c in NPC.skill_points:
            for skill in c.keys():
                key_ability = dnd.skills[skill][2]
                total_ranks = NPC.total_skill_points[skill]['ranks']
                total_ranks += c[skill]['ranks']
                if skill in racial_bonus.keys():
                    bonus = racial_bonus[skill]
                    NPC.total_skill_points[skill]['misc_mod'] = bonus
                if key_ability is not None:
                    NPC.total_skill_points[skill]['ability_mod']\
                                = NPC.ability_mods[key_ability]

        self.update_ability_mods()

        # ==============================================================
        """ Set level specific bonuses for classes """
        # ==============================================================
        #NPC = dnd.special_abs(NPC, active_class_level)
        dnd.special_abs(NPC, active_class, active_class_level,
                        active_class_level_max)

        # ==============================================================
        """ Set feats for classes """
        # ==============================================================
        dnd.add_feats(NPC, active_class, active_class_level,
                        active_class_level_max, level)

    def generate(self):
        """ This function initializes the character by assigning
        Levels, ability scores, classes, physical appearance etc. """
        race = NPC.race
        gender = NPC.gender
        race_specs = dnd.race_specs[race]
        # ===================================================================

        """ Randomize Character level """
        high = dnd.level_types[NPC.level_type][1]
        low = dnd.level_types[NPC.level_type][0]
        NPC.effective_level = random.randint(low, high)
        NPC.total_level = NPC.effective_level - race_specs['level_adjustment']

        # Multi-class characters must be at least level 2
        if NPC.total_level <= 1 and len(NPC.Class) == 2:
            NPC.total_level = 2

        # Distribute randomized levels among character classes
        if not NPC.is_multiclass:
            NPC.skill_points = [dnd.skill_point_dict.copy()]
            NPC.level.append(NPC.total_level)
        else:
            NPC.skill_points = [dnd.skill_point_dict.copy()]*2
            NPC.level = [0,0]
            i = 1
            while i <= NPC.total_level:
                if i == 1:
                    NPC.level[0] += 1
                elif i == 2:
                    NPC.level[1] += 1
                else:
                    NPC.level[random.randint(0, 1)] += 1
                i += 1
        # ===================================================================
        """ Count age. Take into account age modifiers from both
        classes and total level (here divided by 1d6+3) """
        class_age_mods = []
        i = 0
        for class_ in NPC.Class:
            dice = race_specs[dnd.class_specs[NPC.Class[i]]['age']][1]
            rolls = race_specs[dnd.class_specs[NPC.Class[i]]['age']][0]
            class_age_mods.append(roll(dice, rolls, 0, 0, 0))
            i += 1

        # Roll 1d6+3 and divide total level by it, add this sum to total age
        divider = roll(d6, 1, 0, 3, 0)
        modifier = NPC.total_level/divider
        if len(class_age_mods) == 2:
            modifier += max(class_age_mods) + (min(class_age_mods) / 2)
        else:
            modifier += max(class_age_mods)

        # If rolled age would give unwanted penalties, reduce it by 1/15th
        age = race_specs[NPC.age_type] + modifier
        if NPC.age_type == 'adult' and age > race_specs['middle']:
            age = race_specs['middle'] - (race_specs['middle']/15)

        NPC.age = age
        # ===================================================================
        """ Count NPC height and weight based on racial stats """
        base_height = dnd.sizes[race][gender]['base_height']
        base_weight = dnd.sizes[race][gender]['base_weight']
        height_modifier = dnd.sizes[race][gender]['height_mod']
        weight_modifier = dnd.sizes[race][gender]['weight_mod']

        # Convert into metric and imperial units
        extra_height = roll(height_modifier[1],
                            height_modifier[0], 0, 0, 0)
        extra_weight = extra_height * roll(weight_modifier[1],
                                                weight_modifier[0], 0, 0, 0)

        base_height[0] += extra_height / 12
        base_height[1] += extra_height % 12

        if base_height[1] > 12:
            base_height[1] -= 12
            base_height[0] += 1

        NPC.physical['ft'] += base_height[0]
        NPC.physical['in'] += base_height[1]
        NPC.physical['lbs'] += base_weight + extra_weight
        NPC.physical['cm'] += int((base_height[1] * 2.54)
                                     + base_height[0] * (2.54*12))
        NPC.physical['kg'] += int((base_weight + extra_weight) * 0.45)
        NPC.size = dnd.race_specs[race]['size']
        # Set size regarding items and carrying
        NPC.size_for_items = self.check_if_racial_bonus('size_for_items',
                                                        NPC.size)
        # Set size adjustment to attack rolls
        NPC.attack_adj += dnd.attack_adj[NPC.size]
        # ===================================================================
        """ Set character appearance """
        NPC.eyes = random.choice(race_specs['eyes'])
        NPC.skin = random.choice(race_specs['skin'])
        if NPC.age_type in ['old', 'venerable']:
            NPC.hair = random.choice(dnd.hair_colors['old'])
        else:
            NPC.hair = random.choice(race_specs['hair'])

        # ===================================================================
        """ Define base ability scores according to NPC power type:
        ´weaker´        roll 1d8+1 twice (avg 11.0, mean 11)
        ´normal´        roll 4d6 and ignore lowest (avg 12.3, mean 12)
        ´stronger´      roll 1d4 + 2 three times (avg. 13.5, mean 14)
        ´legendary´        roll 6d6, ignore 3 lowest; reroll at 9
                        (avg. 14.2, mean 15)

        Note that rolls totaling under 4 may be rerolled. This may be
        changed from the core settings ´allow_ability_reroll_at´.
        However, scores may get below 4 from racial or age penalties """

        ability_roll = dnd.power_types[NPC.power]['ability_roll']
        ability_reroll_at = dnd.power_types[NPC.power]['reroll_at']

        for score in NPC.abilities:
            result = 0
            while result < ability_reroll_at:
                #print(score, result)
                result = roll(0,0,0,0,0,ability_roll)
            NPC.abilities[score] += result

        # ===================================================================
        """ Initialize skill points and feats """
        NPC.total_skill_points = dnd.skill_point_dict.copy()

        """ Initialize race specs """
        NPC.race_type = race_specs['type']
        NPC.speed_base = race_specs['speed']
        NPC.vision = self.check_if_racial_bonus('vision', 'normal')
        NPC.race_feats = self.check_if_racial_bonus('racial_feat', dict())
        bonus = self.check_if_racial_bonus('spell_resistance', 0)
        if bonus > 0:
            NPC.spell_resistance = bonus + NPC.total_level
        else:
            NPC.spell_resistance = 0

        bonus = self.check_if_racial_bonus('bab', 0)
        NPC.bab += bonus

        # ===================================================================
        """ Make priority order for distributing ability scores """
        self.make_priority_order(NPC.Class, race_specs)

        # ===================================================================
        """ Distribute ability scores according to the priority order """
        self.distribute_abilities(NPC.Class, race_specs)
        # ====================================================================
        """ Set languages and bonus languages: choose bonus languages from
        racial bonus languages and class languages """

        default_languages = race_specs['languages']
        class_specific_languages = []
        for c in NPC.Class:
            if c in dnd.class_languages.keys():
                for l in dnd.class_languages[c]:
                    class_specific_languages.append(l)

        bonus_langs = list(set(dnd.bonus_languages[race]
                            + class_specific_languages)
                            - set(default_languages))

        number_of_bonus_langs = NPC.ability_mods['int']
        langs = []
        if number_of_bonus_langs > 0:
            while number_of_bonus_langs > 0:
                index = random.randint(0, len(bonus_langs)-1)
                langs.append(bonus_langs[index])
                del bonus_langs[index]
                number_of_bonus_langs -= 1

        NPC.languages = sorted(langs + default_languages)
        NPC.scripts = sorted(list(
                            set([dnd.languages[x] for x in NPC.languages])))

        # ===================================================================
        """ Level up NPC """
        level = 1
        active_class_level = 1
        while level < NPC.total_level + 1:
            self.level_up(level, active_class_level)
            level += 1

        self.update_variables()

class UIBuilder():

    def __init__(self, probabilities, random_ages):
        self.probabilities = probabilities
        self.random_ages = random_ages

    def format_menu(self, opts, category):
        """ Format question menu outlook: ´opts´ possible answe options
        ´category´ menu's gategory used as a title """
        menu = '\n{title} {line}\n\n'.format(
                            title=category.upper().replace('_', ' '),
                            line='='*(25-len(category)))

        for key in sorted(opts.keys()):
            if key in ['r']: menu += '\n'
            menu += '%s) %s\n' % (key, opts[key].capitalize())

        return menu

    def check_restrictions(self, next_menu, key):
        """ Check race, alignment or class incompatibilities and filter
        out prohibited items from the ´next_menu´. ´key´ refers to the
        next menu key in the dictionary"""
        restricted = list()

        def filter_list(next_menu, allowed):
            """ Filter out restricted choices from next menu """
            for key in next_menu.keys():
                if next_menu[key] not in allowed:
                    next_menu.pop(key, None)
                    next_menu['r'] = 'random'
            return next_menu

        # Collect prohibited alignments
        if key == 'alignment':
            restricted = dnd.race_specs[NPC.race]['restricted_alignments']
            allowed = list(set(dnd.alignment_types['any']) - set(restricted))
            next_menu = filter_list(next_menu, allowed)
        # Collect prohibited classes
        if key in ['Class']:
            for c in dnd.class_specs.keys():
                if NPC.alignment in dnd.class_specs[c]['restricted_alignments']:
                    restricted.append(c)
            if NPC.Class:
                for x in NPC.Class:
                    restricted += dnd.class_specs[x]['restricted_multi'] + [x]
            allowed = list(set(self.categories[key]) - set(restricted))
            next_menu = filter_list(next_menu, allowed)
        return next_menu

    def show_menu(self, opts, category, randomize):
        """ Get answer and return it or randomize """
        if not randomize:
            while True:
                answer = raw_input(self.format_menu(opts, category) + '\n>> ')
                non_random = list(set(opts.keys()) - set('r'))
                if answer in non_random:
                    return opts[answer]
                if 'r' in opts.keys() and answer == 'r':
                    return opts[random.choice(non_random)]
        else:
            if not self.random_ages and category == 'age_type':
                return 'adult'
            else:
                return opts[random.choice(list(set(opts.keys()) - set(['r'])))]

    def iterate_menus(self, options, menu_order):
        """ Iterate through every NPC customization submenu in the
        previously given order. If multi-class is chosen, ask for
        second class """
        randomize = False
        i = 0
        for key in menu_order:
            if key == 'main_menu':
                if self.show_menu(options[key], key, randomize) == 'random':
                    randomize = True
                key = menu_order[i+1]
                del menu_order[i+1]
            if key == 'multi':
                # Re-ask class if multi-class is chosen
                answer = self.show_menu(options[key], key, randomize)
                if answer == 'random':
                    NPC.is_multiclass = random.choice([True] + [False]*3)
                    if NPC.is_multiclass:
                        key = 'Class'
                    else:
                        key = menu_order[i+1]
                        del menu_order[i+1]
                elif answer == 'multi-class':
                    NPC.is_multiclass = True
                    key = 'Class'
                else:
                    NPC.is_multiclass = False
                    key = menu_order[i+1]
                    del menu_order[i+1]
            else:
                pass

            """ Check variable types for each NPC attribute """
            npc = NPC.__dict__
            if isinstance(npc[key], list):
                npc[key].append(self.show_menu(self.check_restrictions(
                            options[key], key), key, randomize))
            elif isinstance(npc[key], str or bool):
                npc[key] = self.show_menu(self.check_restrictions(
                        options[key], key), key, randomize)
            elif isinstance(npc[key], int):
                npc[key] += self.show_menu(self.check_restrictions(
                        options[key], key), key, randomize)
            i += 1

    def generate_menu(self):
        options = {}
        self.categories = {}

        """ Generate the question menu from definitions file
        ´menu_order´ contains the order questions are asked.
        ´categories´ contains possible answer options for each menu """

        prequery = '\n1) Standard class \n2) NPC class\n\n>>'
        while True:
            char_type = raw_input(prequery)
            if char_type == '1':
                classes = dnd.classes['any']
                menu_order = ['main_menu', 'gender', 'race', 'alignment',
                        'Class', 'multi', 'age_type', 'power', 'level_type']
                break
            if char_type == '2':
                classes = dnd.classes['civilian']
                menu_order = ['main_menu', 'gender', 'race', 'alignment',
                        'Class', 'age_type', 'level_type']
                break
            if char_type == '3':
                classes = ['barbarian', 'wizard', 'cleric', 'bard', 'druid']
                menu_order = ['main_menu', 'gender', 'race', 'alignment',
                        'Class', 'age_type', 'level_type']
                break

        categories = {
            'main_menu': ['customize', 'random'],
            'gender': dnd.genders,
            'race': dnd.races['any'],
            'alignment': dnd.alignment_types['any'],
            'Class': classes,
            'multi': ['single class', 'multi-class'],
            'age_type': sorted(dnd.aging_modifiers.keys()),
            'power': dnd.power_types.keys(),
            'level_type': sorted(dnd.level_types, key=dnd.level_types.get)}

        for category in menu_order:
            self.categories[category] = categories[category]

        """ Generate hotkeys for answers. """
        for key in self.categories.keys():
            i = 0
            options[key] = {}
            for value in self.categories[key]:
                options[key][str(hex(i+1))[2:]] = self.categories[key][i]
                if key != 'main_menu':
                    options[key]['r'] = 'random'
                i += 1

        self.iterate_menus(options, menu_order)

def main():
    print("\nD&D 3.5 NPC Generator v%s" % __version__.strip('$'))
    UIBuilder(False, False).generate_menu()

    NPCBuilder().generate()
    noprint = False


    for k in sorted(NPC.__dict__.keys()):
        if k == 'skill_points':
            noprint = True
        if k == 'total_skill_points':
            noprint = True
            for q in sorted(NPC.__dict__[k]):
                ranks = NPC.__dict__[k][q]['ranks']
                abmod = NPC.__dict__[k][q]['ability_mod']
                misc = NPC.__dict__[k][q]['misc_mod']
                if ranks > 0 or q in dnd.untrained:
                    print(q + ': ' + str(ranks+abmod+misc) + ' = ' + str(ranks) + ' + ' + str(abmod) + ' + ' + str(misc))
        else:
            if not noprint:
                print(k, NPC.__dict__[k])

        noprint = False

    f = open('character_sheet.html', 'w')
    f.writelines(html_sheet.generate(NPC.__dict__, dnd.untrained, True))
    f.close()

if __name__ == "__main__":
    main()

"""
    dist = {}
    tot = []
    i = 0
    while i < 100000:
        rull = roll_dice(dnd.dice['d6'], 4, 0, 0, True)
        tot.append(rull)
        if rull not in dist.keys():
            dist[rull] = 1
        else:
            dist[rull] += 1

        i += 1

    print(float(sum(tot) / float(len(tot))))
    print(sorted(tot)[len(tot)/2])
    for k in sorted(dist.keys()):
        print(k, dist[k])
14,21
15
(3, 3)
(4, 9)
(5, 54)
(6, 156)
(7, 454)
(8, 972)
(9, 1924)
(10, 3565)
(11, 5787)
(12, 9021)
(13, 11971)
(14, 14953)
(15, 16849)
(16, 16163)
(17, 11809)
(18, 6310)
"""
