from typing import Any
from .bit_field import BitField
from .version import Version
from .section_utils import SECTION_IDS
from . import constants


def process_compat_rules(reader: Any, rules: BitField):
    qrs = constants.quest_rules
    version = reader.section_headers[SECTION_IDS.RULES].version
    compatrule_version = reader.section_headers[SECTION_IDS.RULES].extra or 0

    # This first part if from readheader.
    if reader.version.zelda_version < 0x187:
        for qr in range(4*8, 20*8):
            rules.set(qr, False)
    else:
        if reader.version.zelda_version <= 0x190:
            rules.set(qrs.index('qr_MEANPLACEDTRAPS'), False)
    
    if reader.version < Version(zelda_version=0x192, build=149):
        rules.set(qrs.index('qr_BRKNSHLDTILES'), rules.get(qrs.index('qr_BRKBLSHLDS_DEP')))
        rules.set(qrs.index('qr_BRKBLSHLDS_DEP'), True)
    # --- end

    if version < 2:
        rules.set(14, False)
        rules.set(27, False)
        rules.set(28, False)
        rules.set(29, False)
        rules.set(30, False)
        rules.set(32, False)
        rules.set(36, False)
        rules.set(49, False)
        rules.set(50, False)
        rules.set(51, False)
        rules.set(68, False)
        rules.set(75, False)
        rules.set(76, False)
        rules.set(98, False)
        rules.set(110, False)
        rules.set(113, False)
        rules.set(116, False)
        rules.set(102, False)
        rules.set(132, False)

    if reader.version < Version(zelda_version=0x211, build=18):
        rules.set(qrs.index('qr_SMOOTHVERTICALSCROLLING'), True)
        rules.set(qrs.index('qr_REPLACEOPENDOORS'), True)
        rules.set(qrs.index('qr_OLDLENSORDER'), True)
        rules.set(qrs.index('qr_NOFAIRYGUYFIRES'), True)
        rules.set(qrs.index('qr_TRIGGERSREPEAT'), True)

    if reader.version < Version(zelda_version=0x193, build=3):
        rules.set(qrs.index('qr_WALLFLIERS'), True)
        rules.set(qrs.index('qr_NOSCROLLCONTINUE'), True)

    if reader.version < Version(zelda_version=0x193, build=4):
        rules.set(qrs.index('qr_NOBOMBPALFLASH'), True)

    if reader.version.zelda_version <= 0x210:
        rules.set(qrs.index('qr_ARROWCLIP'), True)
        rules.set(qrs.index('qr_OLDSTYLEWARP'), True)
        rules.set(qrs.index('qr_210_WARPRETURN'), True)

    if reader.version.zelda_version == 0x210:
        rules.set(qrs.index('qr_NOSCROLLCONTINUE'),
                  rules.get(qrs.index('qr_CMBCYCLELAYERS')))
        rules.set(qrs.index('qr_CMBCYCLELAYERS'), False)
        rules.set(qrs.index('qr_CONT_SWORD_TRIGGERS'), True)

    if reader.version.zelda_version < 0x210:
        rules.set(qrs.index('qr_OLDTRIBBLES_DEP'), True)
        rules.set(qrs.index('qr_OLDHOOKSHOTGRAB'), True)

    if reader.version.zelda_version < 0x211:
        rules.set(qrs.index('qr_WRONG_BRANG_TRAIL_DIR'), True)

    if reader.version == Version(zelda_version=0x192, build=163):
        rules.set(qrs.index('qr_192b163_WARP'), True)

    if reader.version.zelda_version == 0x210:
        rules.set(qrs.index('qr_OLDTRIBBLES_DEP'),
                  rules.get(qrs.index('qr_DMGCOMBOPRI')))
        rules.set(qrs.index('qr_DMGCOMBOPRI'), False)

    if reader.version < Version(zelda_version=0x211, build=15):
        rules.set(qrs.index('qr_OLDPICKUP'), True)

    if reader.version < Version(zelda_version=0x211, build=18):
        rules.set(qrs.index('qr_NOSOLIDDAMAGECOMBOS'), True)
        rules.set(qrs.index('qr_ITEMPICKUPSETSBELOW'), True)

    if reader.version.zelda_version < 0x250:
        rules.set(qrs.index('qr_HOOKSHOTDOWNBUG'), True)

    if reader.version == Version(zelda_version=0x250, build=24):
        rules.set(qrs.index('qr_PEAHATCLOCKVULN'), True)

    if reader.version < Version(zelda_version=0x250, build=22):
        rules.set(qrs.index('qr_OLD_DOORREPAIR'), True)

    if reader.version < Version(zelda_version=0x250, build=20):
        rules.set(qrs.index('qr_OLD_SECRETMONEY'), True)

    if reader.version < Version(zelda_version=0x250, build=28):
        rules.set(qrs.index('qr_OLD_POTION_OR_HC'), True)

    if reader.version < Version(zelda_version=0x250, build=28):
        rules.set(qrs.index('qr_OFFSCREENWEAPONS'), True)

    if reader.version.zelda_version == 0x250:
        if reader.version.build == 24:
            rules.set(qrs.index('qr_BOMBCHUSUPERBOMB'), True)
        if reader.version.build == 28:
            rules.set(qrs.index('qr_BOMBCHUSUPERBOMB'), True)
        if reader.version.build == 29:
            rules.set(qrs.index('qr_BOMBCHUSUPERBOMB'), False)
        if reader.version.build == 30:
            rules.set(qrs.index('qr_BOMBCHUSUPERBOMB'), False)

    if reader.version < Version(zelda_version=0x250, build=29):
        rules.set(qrs.index('qr_OFFSETEWPNCOLLISIONFIX'), True)

        if reader.version >= Version(zelda_version=0x211, build=18):
            rules.set(qrs.index('qr_BROKENSTATUES'), True)

    if reader.version.zelda_version <= 0x190:
        rules.set(qrs.index('qr_COPIED_SWIM_SPRITES'), True)

    if (
        reader.version <= Version(zelda_version=0x250, build=33) or
        reader.version.zelda_version == 0x254 or
        (reader.version.zelda_version == 0x255 and reader.version.build < 50)
    ):
        rules.set(qrs.index('qr_OLD_SLASHNEXT_SECRETS'), True)

    if reader.version.zelda_version < 0x211:
        rules.set(qrs.index('qr_OLD_210_WATER'), True)

    if reader.version < Version(zelda_version=0x255, build=51):
        rules.set(qrs.index('qr_STEP_IS_FLOAT'), False)

    if reader.version.zelda_version < 0x250:
        rules.set(qrs.index('qr_8WAY_SHOT_SFX'), True)

    if version < 3:
        rules.set(qrs.index('qr_HOLDNOSTOPMUSIC'), True)
        rules.set(qrs.index('qr_CAVEEXITNOSTOPMUSIC'), True)

    if version < 4:
        rules.set(10, False)

    if version < 5:
        rules.set(27, False)

    if version < 6:
        rules.set(46, False)

    if version < 7:
        rules.set(qrs.index('qr_HEARTSREQUIREDFIX'), False)
        rules.set(qrs.index('qr_PUSHBLOCKCSETFIX'), True)

    if version < 8:
        rules.set(12, False)

    if version < 9:
        rules.set(qrs.index('qr_NOROPE2FLASH_DEP'), False)
        rules.set(qrs.index('qr_NOBUBBLEFLASH_DEP'), False)
        rules.set(qrs.index('qr_GHINI2BLINK_DEP'), False)
        rules.set(qrs.index('qr_PHANTOMGHINI2_DEP'), False)

    if version < 10:
        rules.set(qrs.index('qr_NOCLOCKS_DEP'), False)
        rules.set(qrs.index('qr_ALLOW10RUPEEDROPS_DEP'), False)

    if version < 11:
        rules.set(qrs.index('qr_SLOWENEMYANIM_DEP'), False)

    if version < 12:
        rules.set(qrs.index('qr_BRKBLSHLDS_DEP'), False)
        rules.set(qrs.index('qr_OLDTRIBBLES_DEP'), False)

    if reader.version < Version(zelda_version=0x250, build=24):
        rules.set(qrs.index('qr_SHOPCHEAT'), True)

    if reader.version < Version(zelda_version=0x250, build=29):
        rules.set(qrs.index('qr_BITMAPOFFSETFIX'), True)

    if reader.version.zelda_version == 0x250 and reader.version.build in [29, 30, 31]:
        rules.set(qrs.index('qr_BITMAPOFFSETFIX'), False)

    if reader.version.zelda_version == 0x254:
        rules.set(qrs.index('qr_BITMAPOFFSETFIX'), False)

    if reader.version.zelda_version == 0x255 and reader.version.build < 42:
        rules.set(qrs.index('qr_BITMAPOFFSETFIX'), False)

    if reader.version < Version(zelda_version=0x255, build=42):
        rules.set(qrs.index('qr_OLDSPRITEDRAWS'), True)

    if reader.version.zelda_version == 0x254 or reader.version < Version(zelda_version=0x255, build=42):
        rules.set(qrs.index('qr_OLDEWPNPARENT'), True)

    if reader.version.zelda_version == 0x254 or reader.version < Version(zelda_version=0x255, build=44):
        rules.set(qrs.index('qr_OLDCREATEBITMAP_ARGS'), True)

    if reader.version.zelda_version == 0x254 or reader.version < Version(zelda_version=0x255, build=45):
        rules.set(qrs.index('qr_OLDQUESTMISC'), True)

    if reader.version.zelda_version < 0x254:
        rules.set(qrs.index('qr_OLDCREATEBITMAP_ARGS'), False)
        rules.set(qrs.index('qr_OLDEWPNPARENT'), False)
        rules.set(qrs.index('qr_OLDQUESTMISC'), False)

    if reader.version < Version(zelda_version=0x255, build=44):
        rules.set(qrs.index('qr_ITEMSCRIPTSKEEPRUNNING'), False)
        rules.set(qrs.index('qr_SCRIPTSRUNINHEROSTEPFORWARD'), False)
        rules.set(qrs.index('qr_FIXSCRIPTSDURINGSCROLLING'), False)
        rules.set(qrs.index('qr_SCRIPTDRAWSINWARPS'), False)
        rules.set(qrs.index('qr_DYINGENEMYESDONTHURTHERO'), False)
        rules.set(qrs.index('qr_OUTOFBOUNDSENEMIES'), False)
        rules.set(qrs.index('qr_SPRITEXY_IS_FLOAT'), False)

    if reader.version < Version(zelda_version=0x255, build=46):
        rules.set(qrs.index('qr_CLEARINITDONSCRIPTCHANGE'), True)

    if reader.version < Version(zelda_version=0x255, build=46):
        rules.set(qrs.index('qr_TRACESCRIPTIDS'), False)
        rules.set(qrs.index('qr_SCRIPT_FRIENDLY_ENEMY_TYPES'), True)
        rules.set(qrs.index('qr_PARSER_BOOL_TRUE_DECIMAL'), True)
        rules.set(qrs.index('qr_PARSER_250DIVISION'), True)
        rules.set(qrs.index('qr_PARSER_BOOL_TRUE_DECIMAL'), True)
        rules.set(qrs.index('qr_PARSER_TRUE_INT_SIZE'), False)
        rules.set(qrs.index('qr_PARSER_FORCE_INLINE'), False)
        rules.set(qrs.index('qr_PARSER_BINARY_32BIT'), False)
        if rules.get(qrs.index('qr_SELECTAWPN')):
            rules.set(qrs.index('qr_NO_L_R_BUTTON_INVENTORY_SWAP'), True)

    if reader.version < Version(zelda_version=0x255, build=47):
        rules.set(qrs.index('qr_DISALLOW_SETTING_RAFTING'), True)
        rules.set(qrs.index('qr_BROKEN_ASKIP_Y_FRAMES'), True)
        rules.set(qrs.index('qr_ENEMY_BROKEN_TOP_HALF_SOLIDITY'), True)
        rules.set(qrs.index('qr_OLD_SIDEVIEW_CEILING_COLLISON'), True)
        rules.set(qrs.index('qr_0AFRAME_ITEMS_IGNORE_AFRAME_CHANGES'), True)
        rules.set(qrs.index('qr_OLD_ENEMY_KNOCKBACK_COLLISION'), True)

    if reader.version.zelda_version < 0x255:
        rules.set(qrs.index('qr_NOFFCWAITDRAW'), True)
        rules.set(qrs.index('qr_NOITEMWAITDRAW'), True)
        rules.set(qrs.index('qr_SETENEMYWEAPONSPRITESONWPNCHANGE'), True)
        rules.set(qrs.index('qr_OLD_INIT_SCRIPT_TIMING'), True)

    if reader.version < Version(zelda_version=0x255, build=48):
        rules.set(qrs.index('qr_SETENEMYWEAPONSPRITESONWPNCHANGE'), True)

    if reader.version < Version(zelda_version=0x255, build=52):
        rules.set(qrs.index('qr_OLD_PRINTF_ARGS'), True)

    if reader.version < Version(zelda_version=0x255, build=54):
        rules.set(qrs.index('qr_BROKEN_RING_POWER'), True)

    if reader.version < Version(zelda_version=0x255, build=56):
        rules.set(qrs.index('qr_NO_OVERWORLD_MAP_CHARTING'), True)

    if reader.version < Version(zelda_version=0x255, build=57):
        rules.set(qrs.index('qr_DUNGEONS_USE_CLASSIC_CHARTING'), True)

    if reader.version < Version(zelda_version=0x255, build=58):
        if rules.get(qrs.index('qr_SET_XBUTTON_ITEMS')):
            rules.set(qrs.index('qr_SET_YBUTTON_ITEMS'), True)

    if reader.version < Version(zelda_version=0x255, build=59):
        rules.set(qrs.index('qr_ALLOW_EDITING_COMBO_0'), True)

    if reader.version < Version(zelda_version=0x255, build=60):
        rules.set(qrs.index('qr_OLD_CHEST_COLLISION'), True)

    if reader.version.zelda_version < 0x254:
        rules.set(qrs.index('qr_250WRITEEDEFSCRIPT'), True)

    if reader.version < Version(zelda_version=0x254, build=27):
        rules.set(qrs.index('qr_OLDSIDEVIEWSPIKES'), True)

    if reader.version < Version(zelda_version=0x254, build=31):
        rules.set(qrs.index('qr_MELEEMAGICCOST'), False)
        rules.set(qrs.index('qr_GANONINTRO'), False)
        rules.set(qrs.index('qr_OLDMIRRORCOMBOS'), True)
        rules.set(qrs.index('qr_BROKENBOOKCOST'), True)
        rules.set(qrs.index('qr_BROKENCHARINTDRAWING'), True)

    if reader.version < Version(zelda_version=0x254, build=41):
        rules.set(qrs.index('qr_MELEEMAGICCOST'), True)

    if reader.version.zelda_version < 0x193:
        rules.set(qrs.index('qr_SHORTDGNWALK'), True)

    if reader.version.zelda_version < 0x255:
        rules.set(qrs.index('qr_OLDINFMAGIC'), True)

    if reader.version.zelda_version < 0x250:
        rules.set(qrs.index('qr_SIDEVIEWTRIFORCECELLAR'), True)

    if reader.version < Version(zelda_version=0x255, build=47):
        rules.set(qrs.index('qr_OLD_F6'), True)

    if reader.version < Version(zelda_version=0x255, build=49):
        rules.set(qrs.index('qr_NO_OVERWRITING_HOPPING'), True)

    if reader.version < Version(zelda_version=0x255, build=50):
        rules.set(qrs.index('qr_STRING_FRAME_OLD_WIDTH_HEIGHT'), True)

    if reader.version < Version(zelda_version=0x255, build=53):
        rules.set(qrs.index('qr_BROKEN_OVERWORLD_MINIMAP'), True)

    if compatrule_version < 1:
        rules.set(qrs.index('qr_ENEMIES_SECRET_ONLY_16_31'), True)

    if compatrule_version < 2:
        rules.set(qrs.index('qr_OLDCS2'), True)

    if compatrule_version < 3:
        rules.set(qrs.index('qr_HARDCODED_ENEMY_ANIMS'), True)

    if compatrule_version < 4:
        rules.set(qrs.index('qr_OLD_ITEMDATA_SCRIPT_TIMING'), True)

    if compatrule_version < 5 and reader.version.zelda_version >= 0x250:
        rules.set(qrs.index('qr_NO_LANMOLA_RINGLEADER'), True)

    if compatrule_version < 6:
        rules.set(qrs.index('qr_NO_LANMOLA_RINGLEADER'), True)

    if compatrule_version < 7:
        rules.set(qrs.index('qr_ALLTRIG_PERMSEC_NO_TEMP'), True)

    if compatrule_version < 8:
        rules.set(qrs.index('qr_HARDCODED_LITEM_LTMS'), True)

    if compatrule_version < 9:
        rules.set(qrs.index('qr_HARDCODED_BS_PATRA'), True)
        rules.set(qrs.index('qr_PATRAS_USE_HARDCODED_OFFSETS'), True)
        rules.set(qrs.index('qr_BROKEN_BIG_ENEMY_ANIMATION'), True)
        rules.set(qrs.index('qr_BROKEN_ATTRIBUTE_31_32'), True)

    if compatrule_version < 10:
        rules.set(qrs.index('qr_CANDLES_SHARED_LIMIT'), True)

    if compatrule_version < 11:
        rules.set(qrs.index('qr_OLD_RESPAWN_POINTS'), True)

    if compatrule_version < 12:
        rules.set(qrs.index('qr_OLD_FLAMETRAIL_DURATION'), True)
        rules.set(qrs.index('qr_GANONINTRO'),
                  not rules.get(qrs.index('qr_GANONINTRO')))

    if compatrule_version < 13 and reader.version.zelda_version >= 0x255:
        rules.set(qrs.index('qr_ANONE_NOANIM'), True)

    if compatrule_version < 14:
        rules.set(qrs.index('qr_OLD_BRIDGE_COMBOS'), True)

    if compatrule_version < 15:
        rules.set(qrs.index('qr_BROKEN_Z3_ANIMATION'), True)

    if compatrule_version < 16:
        rules.set(qrs.index('qr_OLD_TILE_INITIALIZATION'), True)

    if compatrule_version < 18:
        rules.set(qrs.index('qr_BROKEN_DRAWSCREEN_FUNCTIONS'), True)
        rules.set(qrs.index('qr_SCROLLING_KILLS_CHARGE'), True)

    if compatrule_version < 19:
        rules.set(qrs.index('qr_BROKEN_ITEM_CARRYING'), True)

    if compatrule_version < 20:
        rules.set(qrs.index('qr_CUSTOMWEAPON_IGNORE_COST'), True)

    if compatrule_version < 21:
        rules.set(qrs.index('qr_LEEVERS_DONT_OBEY_STUN'), True)
        rules.set(qrs.index('qr_GANON_CANT_SPAWN_ON_CONTINUE'), True)
        rules.set(qrs.index('qr_WIZZROBES_DONT_OBEY_STUN'), True)
        rules.set(qrs.index('qr_OLD_BUG_NET'), True)
        rules.set(qrs.index('qr_MANHANDLA_BLOCK_SFX'), True)

    if compatrule_version < 22:
        rules.set(qrs.index('qr_BROKEN_KEEPOLD_FLAG'), True)

    if compatrule_version < 23:
        rules.set(qrs.index('qr_OLD_HALF_MAGIC'), True)

    if compatrule_version < 24:
        rules.set(qrs.index('qr_WARPS_RESTART_DMAPSCRIPT'), True)
        rules.set(qrs.index('qr_DMAP_0_CONTINUE_BUG'), True)

    if compatrule_version < 25:
        rules.set(qrs.index('qr_OLD_FAIRY_LIMIT'),
                  not rules.get(qrs.index('qr_OLD_FAIRY_LIMIT')))
        rules.set(qrs.index('qr_OLD_SCRIPTED_KNOCKBACK'), True)

    if compatrule_version < 26:
        rules.set(qrs.index('qr_OLD_KEESE_Z_AXIS'), True)
        rules.set(qrs.index('qr_POLVIRE_NO_SHADOW'), True)
        rules.set(qrs.index('qr_SUBSCR_OLD_SELECTOR'), True)

    if compatrule_version < 27:
        for qr in range(qrs.index('qr_POLVIRE_NO_SHADOW') + 1, qrs.index('qr_PARSER_250DIVISION')):
            rules.set(qr, False)
        for qr in range(qrs.index('qr_COMBODATA_INITD_MULT_TENK') + 1, 800):
            rules.set(qr, False)

    if compatrule_version < 28:
        rules.set(qrs.index('qr_SUBSCR_BACKWARDS_ID_ORDER'), True)

    if compatrule_version < 29:
        rules.set(qrs.index('qr_OLD_LOCKBLOCK_COLLISION'), True)

    if compatrule_version < 30:
        rules.set(qrs.index('qr_DECO_2_YOFFSET'), True)
        rules.set(qrs.index('qr_SCREENSTATE_80s_BUG'), True)

    if compatrule_version < 31:
        rules.set(qrs.index('qr_GOHMA_UNDAMAGED_BUG'), True)
        rules.set(qrs.index('qr_FFCPRELOAD_BUGGED_LOAD'), True)

    if compatrule_version < 32:
        rules.set(qrs.index('qr_BROKEN_GETPIXEL_VALUE'), True)

    if compatrule_version < 33:
        rules.set(qrs.index('qr_NO_LIFT_SPRITE'), True)

    if compatrule_version < 34:
        rules.set(qrs.index('qr_OLD_SIDEVIEW_LANDING_CODE'), True)
        rules.set(qrs.index('qr_OLD_FFC_SPEED_CAP'), True)
        rules.set(qrs.index('qr_OLD_FFC_FUNCTIONALITY'), True)
        rules.set(qrs.index('qr_OLD_WIZZROBE_SUBMERGING'), True)

    if compatrule_version < 36:
        rules.set(qrs.index('qr_OLD_SHALLOW_SFX'), True)

    rules.set(qrs.index('qr_ANIMATECUSTOMWEAPONS'), False)
    if version < 16:
        rules.set(qrs.index('qr_BROKEN_HORIZONTAL_WEAPON_ANIM'), True)
