# DnD35-generator
Dungeons and Dragons 3.5 NPC generator

## What does this do?
This tool is Dungeons & Dragons 3.5 DM's best friend. Need to create a random NPC party that matches the player levels? A random merchant, aristocrat or a cleric with proper feats, skills and stats? This little script will do it automatically from ground up following the DnD 3.5 core rules rather rigorously. Thus no more sweat rolling a character that your players will ignore or slay anyway.

The program will generate a nice HTML-character sheet with all necessary information, including feats, skills, BAB for different weapon types, Saves, AC, HP, Spell resistance, damage reduction, appearance, spoken languages, ability scores etc.

## Missing features
At the moment the script does not memorize spells.

## Requirements
At the moment this works on Python 2.7 (or 2.x). 

## How to use?
Run dnd35_generator.py and follow the given instruction in the console. You can either give specific base info for the character or just pick anything randomly.

#### 1. Class type
(1) Standard player class or (2) NPC classe (e.g. aristocrat, acolyte etc.)

#### 2. Customization
(1) Customize your character, (2) just generate it completely randomly. If you go with option (1), you'll be asked questions below:

#### 3. Gender
(1) Male, (2) Female

#### 4. Race
Human, Elf, Half-elf, Halfling, Gnome, Dwarf, Half-orc, Drow, Duergar, Svirfneblin, Half-Ogre, Orc, Ogre

#### 5. Alignment
Any that is not restricted by your race

#### 6. Class
All base classes in DnD 3.5 PHB that are allowed by your alignment 

#### 7. Multi-class
Make a multi-class if wanted, select another class.

#### 8. Age type
(1) Adult, (2) Middle, (3) Old, (4) Venerable. Gives relevant penalties or bonuses and calculates age to your character based on its class and race.

#### 9. Power
Defines how HP and ability scores are rolled. (1) Weaker, (2) Stronger, (3) Legendary, (4) Normal. For example, ablility scores are rolled as follows:

      ´weaker´        roll 1d8+1 twice (avg 11.0, mean 11)
      ´normal´        roll 4d6 and ignore lowest (avg 12.3, mean 12)
      ´stronger´      roll 1d4 + 2 three times (avg. 13.5, mean 14)
      ´legendary´     roll 6d6, ignore 3 lowest; reroll at 9 (avg. 14.2, mean 15)

The ability points are distributed following a simple priorization algorithm. For example, if the NPC is a Fighter/Wizard, the optimal path would be (from most important score to the least important)

       Fighter:     STR    CON     DEX     WIS     INT     CHA
                     |   /  |   __________/   \__
                     v  /   v  /                   \
       Wizard:      INT    DEX     CON     WIS     CHA     STR

        Thus new priority order would be:

            STR -> INT -> CON -> DEX -> WIS -> CHA

#### 10. Level type
Select the level range for the character.

