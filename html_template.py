# -*- coding: utf-8 -*-

# A. Sahala 2014

HIDE_CALCULATED = False

def add_plus(digit):
    if digit > 0:
        return '+' + str(digit)
    else:
        return str(digit)

def format_height(npc):
    height = "{ft}' {inc}&quot; <small>({cm} cm)</small>".format(
        cm=int(npc['physical']['cm']),
        ft=int(npc['physical']['ft']),
        inc=int(npc['physical']['in']))
    return height

def format_weight(npc):
    weight = "{lb} lb <small>({kg} kg)</small>".format(
        lb=int(npc['physical']['lbs']),
        kg=int(npc['physical']['kg']))
    return weight

def format_ac_special(npc):
    bonuses = []
    asb = npc['ac_special_bonuses']
    for t in asb.keys():
        for b in asb[t].keys():
            if asb[t][b] > 0:
                bonuses.append(add_plus(asb[t][b]) + ' (' + t + ') ' + b)
    return('<br/>'.join(bonuses))

def format_langs(langs):
    out = []
    for lang in langs:
        out.append(lang.capitalize())

    return ', '.join(out)

def format_dr(npc):
    bonuses = []
    dr = npc['damage_reduction']
    for t in dr.keys():
        if dr[t] > 0:
            bonuses.append('%s/%s' % (dr[t], t))

    return(', '.join(bonuses))

def format_save_special(save, general):
    bonuses = []
    saves = [save, general]
    for x in saves:
        for s in x.keys():
            if x[s] > 0:
                bonuses.append(add_plus(x[s]) + ' ' +  s)

    return(', '.join(bonuses))

def generate_skill_tables(npc, untrained, compact=True):
    skills = npc['total_skill_points']
    table = []
    for q in sorted(skills):
        ranks = skills[q]['ranks']
        abmod = skills[q]['ability_mod']
        misc = skills[q]['misc_mod']
        if ranks > 0 or q in untrained:
            if compact:
                table.append('{skill_name}: <b>{total}</b>'.format(
                skill_name=q, total=str(ranks+abmod+misc)).replace(' ', '&nbsp;'))
            else:
                table.append('<tr><td>{skill_name}<td><td class="boxed"><b>{total}</b></td><td>=</td><td class="boxed">{ranks}</td><td>+</td><td class="boxed">{abmod}</td><td>+</td><td class="boxed">{misc}</td></tr>'.format(
                    skill_name=q,
                    total=str(ranks+abmod+misc),
                    ranks=str(ranks),
                    abmod=str(abmod),
                    misc=str(misc)))

    if compact:
        output = '<tr><td>%s</td></tr>' % ' | '.join(table)
    else:
        output = '\n'.join(table)
    return output

def count_attacks(attacks, mod, size_adj):
    if mod is None:
        mod = 0
    ats = []
    for attack in attacks.keys():
        if attacks[attack] is not None:
            ats.append(add_plus(attacks[attack] + mod + size_adj))

    return '/'.join(ats)

def format_class(cl, lvl):
    classes = []
    for pair in zip(cl, lvl):
        classes.append("%s (%s)" % (pair[0], str(pair[1])))

    return ' / '.join(classes)

def format_class_feats(cfeats):
    class_feats = []
    for f in sorted(cfeats):
        if isinstance(cfeats[f], tuple):
            val = cfeats[f][1]
        else:
            val = cfeats[f]

        if HIDE_CALCULATED and val.startswith('('):
            pass
        else:
            class_feats.append('<tr><td width="24%" class="lined"><b>{name}</b></td><td class="lined">{val}</td></tr>'.format(
                name = f, val=val)
            )

    return '\n'.join(class_feats)
    #'\n'.join(['<tr><td><b><small>'+x+'</small></b></td><td><small>'+str(npc['class_feats'][x])+'</small></td></tr>' for x in sorted(npc['class_feats'].keys())])

def generate(npc, untrained, compact):
    template = '''
<html>
<head>
<title>D&D 3.5 NPC Character sheet - A. J. Sahala 2014</title>
<link rel="stylesheet" type="text/css" href="sheet.css" />
</head>
<body>
<center>
<table class="main">
<tr>
<td valign="top">
<center> <!-- Sheet top -->

<table class="section"> <!-- Section for basic character info -->
<tr>
<td colspan="2">{name}</td>
<td colspan="2">{cls}</td>
<td colspan="3" rowspan="4" align="center"><img width="235" src="logo.png"/></td>
</tr>
<tr>
<td colspan="2">CHARACTER NAME</td>
<td colspan="2">CLASS AND LEVEL</td>
</tr>
<tr>
<td>{race}</td>
<td>{race_type}</td>
<td>{alignment}</td>
<td>{deity}</td>
</tr>
<tr>
<td>RACE</td>
<td>SUBTYPE</td>
<td>ALIGNMENT</td>
<td>DEITY</td>
</tr>
<tr>
<td>{gender}</td>
<td>{age} <small>({agetype})</small></td>
<td>{height}</td>
<td>{weight}</td>
<td>{skin}</td>
<td>{eyes}</td>
<td>{hair}</td>
</tr>
<tr>
<td>GENDER</td>
<td>AGE</td>
<td>HEIGHT</td>
<td>WEIGHT</td>
<td>SKIN</td>
<td>EYES</td>
<td>HAIR</td>
</tr>

<tr>
<td colspan="2">{vision}</td>
<td colspan="5">{languages}</td>
</tr>
<tr>
<td colspan="2">VISION</td>
<td colspan="5">LANGUAGES</td>
</tr>



</table>




<table class="section2"> <!-- Section for ability scores, AC etc -->
<tr>
<td class="description" width="45">ABILITY</td>
<td class="description" width="45">SCORE</td>
<td class="description" width="45">MODIFIER</td>
<td class="description" width="45">TEMP SCORE</td>
<td class="description" width="45">TEMP MOD</td>
<td class="description" width="45"></td>
<td class="description" width="45">TOTAL</td>
<td colspan="4" class="description">WOUNDS</td>
<td colspan="2" class="description">NON-LETHAL DMG</td>
<td class="description">SPEED</td>
</tr>
<tr>
<td class="title">STR</td>
<td class="boxed">{Str}</td>
<td class="boxed">{strm}</td>
<td class="boxedtemp"></td>
<td class="boxedtemp"></td>
<td class="title">HP</td>
<td class="boxed">{hp}</td>
<td colspan="4" class="boxed"></td>
<td colspan="2" class="boxed"></td>
<td class="boxed">{speed}</td>
</tr>
<tr>
<td class="title">DEX</td>
<td class="boxed">{dex}</td>
<td class="boxed">{dexm}</td>
<td class="boxedtemp"></td>
<td class="boxedtemp"></td>
<td class="title">AC</td>
<td class="boxed">{ac}</td>
<td><small>=&nbsp;{base_ac}&nbsp;+</small></td>
<td class="boxed">{aB}</td> <!-- armor bonus -->
<td class="boxed">{sB}</td> <!-- shield bonus -->
<td class="boxed">{dM}</td> <!-- dexterity mod -->
<td class="boxed">{sM}</td> <!-- size mod -->
<td class="boxed">{na}</td> <!-- natural armor -->
<td class="boxed">{de}</td> <!-- deflection modifier -->
</tr>
<tr>
<td class="title">CON</td>
<td class="boxed">{con}</td>
<td class="boxed">{conm}</td>
<td class="boxedtemp"></td>
<td class="boxedtemp"></td>
<td colspan="2" class="title">TEMP AC</td>
<td class="boxedtemp"></td>
<td class="descriptiontop">ARMOR +</td>
<td class="descriptiontop">SHLD +</td>
<td class="descriptiontop">DEX +</td>
<td class="descriptiontop">SIZE +</td>
<td class="descriptiontop">NATU +</td>
<td class="descriptiontop">DEFLECT.</td>
</tr>
<tr>
<td class="title">INT</td>
<td class="boxed">{Int}</td>
<td class="boxed">{Intm}</td>
<td class="boxedtemp"></td>
<td class="boxedtemp"></td>
<td colspan="2" class="title">TOUCH AC</td>
<td class="boxed">{TAC}</td>
<td class="title">SR</td>
<td colspan="2" class="boxed">{SR}</td>
<td colspan="3" rowspan="2" class="boxed">{spec_ac}</td>
</tr>
<tr>
<td class="title">WIS</td>
<td class="boxed">{wis}</td>
<td class="boxed">{wism}</td>
<td class="boxedtemp"></td>
<td class="boxedtemp"></td>
<td colspan="2" class="title">FLAT. AC</td>
<td class="boxed">{FF}</td>
<td rowspan="2" class="title">DR</td>
<td colspan="2" rowspan="2" class="boxed">{DR}</td>
</tr>
<tr>
<td class="title">CHA</td>
<td class="boxed">{cha}</td>
<td class="boxed">{cham}</td>
<td class="boxedtemp"></td>
<td class="boxedtemp"></td>
<td colspan="2" class="title">INIT</td>
<td class="boxed">{init}</td>
<td colspan="3" rowspan="2" class="descriptiontop">SPECIAL AC MODIFIERS</td>
</tr>

</table>

<table class="section2"> <!-- Section for Saving throws -->
<tr>
<td class="description">SAVE</td>
<td class="description">TOTAL</td>
<td></td>
<td class="description">BASE</td>
<td></td>
<td class="description">KEY AB</td>
<td></td>
<td class="description">MAG</td>
<td></td>
<td class="description">MISC</td>
<td width="40"></td>
<td class="description">TEMP</td>
<td class="description" width="40%">SPECIAL</td>
</tr>
<tr>
<td class="title">FORTITUDE</td>
<td class="boxed">{ftot}</td>
<td>=</td>
<td class="boxed">{fbas}</td>
<td>+</td>
<td class="boxed">{conm}</td>
<td>+</td>
<td class="boxed">{fmod}</td>
<td>+</td>
<td class="boxed">{fmi}</td>
<td></td>
<td class="boxedtemp"></td>
<td class="boxed">{fspecial}</td>
</tr>
<tr>
<td class="title">REFLEX</td>
<td class="boxed">{rtot}</td>
<td>=</td>
<td class="boxed">{rbas}</td>
<td>+</td>
<td class="boxed">{dexm}</td>
<td>+</td>
<td class="boxed">{rmod}</td>
<td>+</td>
<td class="boxed">{rmi}</td>
<td></td>
<td class="boxedtemp"></td>
<td class="boxed">{rspecial}</td>
</tr>
<tr>
<td class="title">WILL</td>
<td class="boxed">{wtot}</td>
<td>=</td>
<td class="boxed">{wbas}</td>
<td>+</td>
<td class="boxed">{wism}</td>
<td>+</td>
<td class="boxed">{wmod}</td>
<td>+</td>
<td class="boxed">{wmi}</td>
<td></td>
<td class="boxedtemp"></td>
<td class="boxed">{wspecial}</td>
</tr>
</table>



<table class="section2"> <!-- Section for Saving throws -->
<tr>
<td colspan="2" class="title">BAB</td>
<td colspan="2" class="boxed">{bab}</td>
<td colspan="2" class="title">FISTS</td>
<td colspan="2" class="boxed">{fistdmg}</td>
<td width="40%" class="title">SKILLS (all modifiers included)</td>
</tr>

<tr>
<td colspan="2" class="title">MELEE</td>
<td colspan="2" class="boxed">{M_total}</td>
<td>=</td>
<td class="boxed">{strm}</td>
<td>+</td>
<td class="boxed">{M_base}</td>
<td rowspan="25" valign="top">
<!-- Generate skills here -->

  <table class="skills">
	{skills}
   </table>

</td>
</tr>

<tr>
<td colspan="2" class="title">RANGED</td>
<td colspan="2" class="boxed">{R_total}</td>
<td>=</td>
<td class="boxed">{dexm}</td>
<td>+</td>
<td class="boxed">{R_base}</td>
</tr>

<tr>
<td colspan="2"></td>
<td colspan="2" class="descriptiontop">TOTAL</td>
<td></td>
<td class="descriptiontop">ABIL</td>
<td></td>
<td class="descriptiontop">BASE ATTACKS</td>
</tr>

<tr>
<td colspan="8" class="wpntitle">{wpn1_name}</td>
</tr>

<tr>
<td colspan="2" class="title">TYPE</td>
<td colspan="6" class="boxed">{wpn1_type}</td>
</tr>

<tr>
<td colspan="2" class="title">DAMAGE</td>
<td colspan="6" class="boxed">{wpn1_damage}</td>
</tr>

<tr>
<td colspan="2" class="title">ATTACKS</td>
<td colspan="2" class="boxed">{wpn1_attacks}</td>
<td colspan="3" class="title">CRITICAL</td>
<td colspan="1" class="boxed">{wpn1_crit}</td>
</tr>

<tr>
<td colspan="2" class="title">SPECIAL</td>
<td colspan="6" class="boxed">{wpn1_special}</td>
</tr>

<tr>
<td colspan="8" class="wpntitle">{wpn2_name}</td>
</tr>

<tr>
<td colspan="2" class="title">TYPE</td>
<td colspan="6" class="boxed">{wpn2_type}</td>
</tr>

<tr>
<td colspan="2" class="title">DAMAGE</td>
<td colspan="6" class="boxed">{wpn2_damage}</td>
</tr>

<tr>
<td colspan="2" class="title">ATTACKS</td>
<td colspan="2" class="boxed">{wpn2_attacks}</td>
<td colspan="3" class="title">CRITICAL</td>
<td colspan="1" class="boxed">{wpn2_crit}</td>
</tr>

<tr>
<td colspan="2" class="title">SPECIAL</td>
<td colspan="6" class="boxed">{wpn2_special}</td>
</tr>

<tr>
<td colspan="8" class="wpntitle">&nbsp;</td>
</tr>

<tr>
<td colspan="2" class="title">TYPE</td>
<td colspan="6" class="boxed"></td>
</tr>

<tr>
<td colspan="2" class="title">DAMAGE</td>
<td colspan="6" class="boxed"></td>
</tr>

<tr>
<td colspan="2" class="title">ATTACKS</td>
<td colspan="2" class="boxed"></td>
<td colspan="3" class="title">CRITICAL</td>
<td colspan="1" class="boxed"></td>
</tr>

<tr>
<td colspan="2" class="title">SPECIAL</td>
<td colspan="6" class="boxed"></td>
</tr>

<tr>
<td colspan="8" class="title">WORN ITEMS</td>
</tr>

<tr>
<td colspan="8" rowspan="5" class="boxed">{items}</td>
</tr>

</table>

<table class="section3"> <!-- Section for special abilities -->
<tr>
<td colspan="2" class="title">RACE FEATS (Bonuses already count if in parentheses)</td>
</tr>

{race_feats}

</table>

<table class="section3"> <!-- Section for special abilities -->
<tr>
<td colspan="2" class="title">CLASS FEATS (Bonuses already count if in parentheses)</td>
</tr>

{class_feats}

</table>

<table class="section3"> <!-- Section for special abilities -->
<tr>
<td colspan="2" class="title">FEATS (Bonuses already count if in parentheses)</td>
</tr>

{feats}

</table>


</center> <!-- Sheet bottom -->
</td>
</tr>
</table>
</center>
</body>
</html>'''.format(
           deity = ''.title(),
           vision = npc['vision'].capitalize(),
           languages = format_langs(npc['languages']),
           race_type = npc['race_type'].title(),
           agetype = npc['age_type'].title(),
           name = '', #npc['name'],
           gender = npc['gender'].title(),
           race = npc['race'].title(),
           age = npc['age'],
           cls = format_class(npc['Class'], npc['level']).title(),
           alignment = npc['alignment'].title(),
           Str = npc['abilities']['str'],
           dex = npc['abilities']['dex'],
           con = npc['abilities']['con'],
           wis = npc['abilities']['wis'],
           Int = npc['abilities']['int'],
           cha = npc['abilities']['cha'],
           strm = npc['ability_mods']['str'],
           dexm = npc['ability_mods']['dex'],
           conm = npc['ability_mods']['con'],
           wism = npc['ability_mods']['wis'],
           Intm = npc['ability_mods']['int'],
           cham = npc['ability_mods']['cha'],
           ac = npc['ac'],
           base_ac = npc['ac_base'],
           aB = npc['ac_modifiers']['armor'],
           sB = npc['ac_modifiers']['shield'],
           dM = npc['ac_modifiers']['mods'],
           sM = npc['ac_modifiers']['size'],
           na = npc['ac_modifiers']['natural'],
           de = npc['ac_modifiers']['deflect'],
           TAC = npc['ac_touch'],
           FF = npc['ac_flat_footed'],
           SR = npc['spell_resistance'],
           DR = format_dr(npc),
           spec_ac = format_ac_special(npc),
           age_type = npc['age_type'],
           hp = npc['hp'],
           bab = npc['bab'],
           ftot = npc['saves_total']['fort'],
           rtot = npc['saves_total']['ref'],
           wtot = npc['saves_total']['will'],
           fbas = npc['saves_base']['fort'],
           rbas = npc['saves_base']['ref'],
           wbas = npc['saves_base']['will'],
           fmod = npc['saves_mods']['fort']['mag'],
           rmod = npc['saves_mods']['ref']['mag'],
           wmod = npc['saves_mods']['will']['mag'],
           fmi = npc['saves_mods']['fort']['misc'],
           rmi = npc['saves_mods']['ref']['misc'],
           wmi = npc['saves_mods']['will']['misc'],
           fspecial = format_save_special(npc['save_special_bonuses']['fort'],
                        npc['save_special_bonuses']['general']),
           rspecial = format_save_special(npc['save_special_bonuses']['ref'],
                        npc['save_special_bonuses']['general']),
           wspecial = format_save_special(npc['save_special_bonuses']['will'],
                        npc['save_special_bonuses']['general']),
           skin = npc['skin'].title(),
           hair = npc['hair'].title(),
           eyes = npc['eyes'].title(),
           fistdmg = npc['unarmed_damage'],
           M_total = count_attacks(npc['attacks'],
                                    npc['ability_mods']['str'],
                                    npc['attack_adj']),
           R_total = count_attacks(npc['attacks'], npc['ability_mods']['dex'],
                                    npc['attack_adj']),
           M_base = count_attacks(npc['attacks'], None, npc['attack_adj']),
           R_base = count_attacks(npc['attacks'], None, npc['attack_adj']),
           wpn1_name = '',
           wpn1_type = '',
           wpn1_damage = '',
           wpn1_attacks = '',
           wpn1_crit = '',
           wpn1_special = '',
           wpn2_name = '',
           wpn2_type = '',
           wpn2_damage = '',
           wpn2_attacks = '',
           wpn2_crit = '',
           wpn2_special = '',
           items = '',
           skills = generate_skill_tables(npc, untrained, compact),
           #melee = attacks['melee'],
           #ranged = attacks['ranged'],
           speed = npc['speed'],
           dmg_reduction = npc['damage_reduction'],
           init = npc['ability_mods']['dex'] + npc['initiative'],
           height = format_height(npc),
           weight = format_weight(npc),
           size = npc['size'],
           heavy = '', heavy_kg = '',
           medium = '', medium_kg ='',
           light = '', light_kg ='',
           class_feats = format_class_feats(npc['class_feats']),
           race_feats = format_class_feats(npc['race_feats']),
           feats = format_class_feats(npc['feats'])
           )

    return template
